Hi there, 

This serves as a record of what working through this project looked like.

---

WhatsApp exports do not contain transcriptions of voice notes in the text log. 



**Output.** Simple. I want to look at the text file that contains all the messages in a chat and, where I would see the voice note, see the transcribed text.



---

**Sample export.** Look at the sample export that I have put in the exports folder. I downloaded several of these exports for the same person so the filename contains a "(N)" suffix so account for that but in general assume that the filenames of the exports will follow a similar format. The filename for the export follows whichever format is used for exports on Mac OS. 



**Input.** This will be a utility which expects, for now, a single export in the `exports` folder. The export will be a `.zip` file. The export is expected to have the anatomy detailed in the `README.md` file. 

**Processing.** The utility will unzip the file and start parsing through the text log of the chat. It will retain the information in the text log. Where there is an indication of a voice note, it will match it to the recording stored in the export. It will then use a transcription service to create transcription text of the recording. The transcription will be stored in the text log alongside the usual metadata like the sender and timestamp. There will also be some new metadata: mainly, a message that says that this text was retrieved using transcription service. This kind of flag may be useful for AI use cases. The script will continue processing the entire file. The final output will be a `.zip` file of the text chat with transcriptions as well as the other files that were originally found in the zip. The file will be stored in the `output` directory and named as the original export was only with a suffix attached at the end -- `_transcribed` . 



This utlity assumes that the user can use Docker Desktop or some other Docker engine to run the utility in an ephemeral container.



The `docker-compose.yml` file contains spec for a service that runs ad-hoc. There is a bash script `transcribe.sh` to run the utility. I think a Docker Compose profile is needed to do this with a flag like `--tools`.



The utility is written in Python uses PEP 8 standards. The code is modular and available through a simple CLI. There are unit tests for 85% code coverage. 



There is a GitHub workflow triggered when a developer pushes to the remote branch. The workflow runs any linting like flake8 and runs the unit tests. 



Any tools needed locally are specified in `mise.toml` therefore Mise is required.



There needs to be some quick discovery for transcription service to use. I think we likely need a paid service to get quality results however I am sure. Perhaps there are free ways to transcribe accurately.