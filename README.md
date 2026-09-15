# bambi-sings

Place unpacked WhatsApp chat exports under [`exports/`](exports/). A loader utility will consume that directory later; this document describes the export layout parsers should assume.

## WhatsApp export anatomy

WhatsApp does not publish a formal export specification. Layout and string literals vary by platform (iOS vs Android), app language, and whether **Include media** was selected. Treat exports as **locale-sensitive, de facto formats** validated against real files.

### Package layout

| Artifact | Role |
| --- | --- |
| ZIP archive | Delivered by **Export chat** on device; filename is user-defined (e.g. `WhatsApp Chat - {contact} (n).zip`). |
| Chat log | Single UTF-8 text file: `_chat.txt` (typical on iOS) or `WhatsApp Chat with {name}.txt` (common on Android). |
| Media files | Sibling entries in the same ZIP root when media is included; no standard subfolder. |

Unpacked layout for this repo:

```text
exports/
  {export-id}/          # one directory per unpacked ZIP
    _chat.txt           # or Android-named .txt
    00000197-PHOTO-…jpg
    …
```

### Chat log (`_chat.txt`)

Plain text, chronological. Each **logical message** begins with a header line; additional lines without a header are continuations (multiline body, quoted replies prefixed with `>`, etc.).

**iOS (observed in sample exports)**

```text
[M/D/YY, H:MM:SS AM/PM] {Sender}: {body}
```

**Android (documented by parsers; not identical to iOS)**

```text
DD/MM/YYYY, HH:MM - {Sender}: {body}
```

**Unicode:** Lines often contain U+200E/U+200F (directionality) and U+202F (narrow no-break space before `AM`/`PM`). Strip or normalize before regex matching.

**System vs user:** If the header matches but `{Sender}` is absent or the body is a fixed system string (encryption notice, *You deleted this message*, block/unblock, call events), classify as **system**. Otherwise **user**, with `sender` taken from the header.

**Edits:** Suffix `‎<This message was edited>` on the same line; original text is not retained.

**Media omitted:** Without **Include media**, attachment lines use placeholders (locale-specific), e.g. `‎<media omitted>`, `‎audio omitted`, `‎video omitted`, or Android `(file attached)` with no file in the ZIP. Re-export with media to recover filenames.

### Media files

When included, binaries sit next to the chat log. Extensions observed in sample exports:

| Kind | Typical extensions | Log reference |
| --- | --- | --- |
| Photo | `.jpg`, `.webp` | `<attached: …>` or filename + `(file attached)` |
| Voice note / audio | `.opus` (also `.aac`, `.mp3` in other exports) | same |
| Video | `.mp4` | same; may duplicate with `video omitted` if size limits apply |
| Sticker | `.webp` | same |
| Document | original name (`.pdf`, `.docx`, …) | often `{display name} • {pages} pages ‎<attached: …>` |

**On-disk naming (iOS-style, recent):**

```text
{8-digit-seq}-{PHOTO|AUDIO|VIDEO|STICKER}-{YYYY-MM-DD-HH-MM-SS}.{ext}
```

Documents may embed the original basename: `00002792-347911229-Betrayal-J-Hillman.pdf`.

**Legacy Android-style** (still seen in the wild): `IMG-YYYYMMDD-WA####.jpg`, `PTT-…opus`, `VID-…mp4`. Case and prefix are not guaranteed across locales and versions.

The timestamp embedded in a media **filename** reflects WhatsApp’s internal naming (often receive/storage time), not the message header timestamp. Do not use filename dates as the source of truth for *when* or *by whom* a file was sent.

### Linking media to messages

Association is **by explicit filename in the chat log**, not by inferring from image metadata or filename dates alone.

1. Parse the message header → `sent_at`, `sender`.
2. From the same logical message (header line plus continuations until the next header), extract an attachment token:
   - **iOS:** `‎<attached: {basename}>`
   - **Android:** `{basename} (file attached)` or localized equivalent
   - **Omitted:** placeholder only; no file to join
3. Resolve `{basename}` against files in the export directory (case-sensitive match on case-sensitive filesystems).
4. Optional caption: text on the header line before the `<attached:` marker (voice notes may be attachment-only).

Burst sends may emit a header with an empty body immediately followed by one or more attachment-only messages (each with its own timestamp and sender).

View-once and some privacy messages appear as system text with **no** retrievable file in the export.

### Normalized message schema (target model)

Design for a **line-oriented parser** that outputs structured records; keep raw text for audit.

```yaml
ChatExport:
  export_id: string          # directory name under exports/
  chat_log: path             # _chat.txt or Android name
  platform: ios | android | unknown
  locale_hint: string | null # from date/time tokens if detected

Message:
  index: int                 # stable order in log
  sent_at: datetime          # from header; timezone as exported (often implicit local)
  sender: string | null      # null for system lines
  kind: user | system
  body: string               # text after header; attachment markers stripped
  attachment:
    filename: string
    media_kind: photo | audio | video | sticker | document | unknown
    resolved_path: path | null   # null if omitted or missing on disk
  flags:
    edited: bool
    deleted: bool              # body is deletion notice
    media_omitted: bool
  raw: string                  # full logical message (multiline)
```

**Parsing pipeline**

1. Normalize Unicode (BOM, bidi marks, narrow spaces).
2. Split on message-header regex (platform-specific or unified with alternation); append non-matching lines to the current message.
3. Classify system messages via allowlist/patterns.
4. Extract attachment filename with permissive patterns (filenames may contain spaces, hyphens, and mixed case).
5. Join attachments to ZIP/directory entries by basename; report orphans (file without log line, log line without file).

**Pitfalls:** locale-specific dates and AM/PM; multiline and quoted content; captions spanning lines; duplicate video lines (`attached` + `omitted`); edited/deleted markers; hash-prefixed `.jpg` names in some German/locale exports; assuming `IMG-*` or uppercase only.

### References

- [WhatsApp Help — Exporting chats](https://faq.whatsapp.com/general/chats/how-to-export-your-chat-history) (user-facing; no field-level spec).
- Community parsers and write-ups: [whatsapp-chat-parser](https://github.com/Pustur/whatsapp-chat-parser), [Stack Overflow — chat log regex](https://stackoverflow.com/questions/55066839/whatsapp-chat-log-parsing-with-regex).

Sample material used while drafting this section: an iOS export with `_chat.txt`, `PHOTO`/`AUDIO`/`VIDEO`/`STICKER` assets, and PDF attachments (~290 media files + log).
