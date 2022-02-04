# !/usr/bin/python3
import os
import sys
import logging
import time
from pathlib import Path
from dotenv import load_dotenv
from slack_sdk import WebClient

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)

# setup env file (.env)
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

# setup slack client
client = WebClient(token=os.environ.get("SLACK_TOKEN"))
channel=os.environ.get("SLACK_CHANNEL")

path = os.environ.get("CONVERT_PATH")
logging.info(f'path set to {path}')

file_format = os.environ.get("FILE_FORMAT")
file_format_length = len(file_format)

##################################
# METHODS USED FOR SLACK LOGGING #
##################################

# Adds a specified reaction (react) to a slack message specified via timestamp (ts)
def addReact(react, ts):
    client.reactions_add(channel=channel,
                        name=react,
                        timestamp=ts)

# Removes a specified reaction (react) to a slack message specified via timestamp (ts)
def removeReact(react, ts):
    client.reactions_remove(channel=channel,
                        name=react,
                        timestamp=ts)

# Sends a parent message with specified text (msg)
def sendParentMsg(msg):
    return client.chat_postMessage(channel=channel, text=msg)

# Sends a reply message with specified text (msg) to a parent message specified by timestamp (ts)
def sendReplyMsg(msg, ts):
    client.chat_postMessage(channel=channel,
                            thread_ts=ts,
                            text=msg)

def updateMsg(msg, ts):
    client.chat_update(channel=channel,
                            ts=ts,
                            text=msg)

# Note that an error occurred and reply to parent message specified by timestamp (ts) with specified message (msg) 
def errorOccurred(msg, ts):
    client.chat_postMessage(channel=channel,
                            thread_ts=ts,
                            text=f"ERROR: {msg}",)
    addReact('warning', ts)
    
    logging.critical(f'ERROR: {msg}')
    quit()





def main():
    # check to see if file path exists
    if os.path.exists(path):
        logging.info('path exists, continuing')
    else:
        logging.info('path does not exist: attempting to mount...')
        os.system("osascript -e 'mount volume \"smb://macserver.local/Live TV Jellyfin Recordings [WD2TB]\"'")
        logging.info('path mounted! continuing...')

    # get all files in specified format in PATH 
    fileFormatFiles = []
    fileFormatFilesRaw = []
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith(file_format):
                fileFormatFilesRaw.append(file)
                fileFormatFiles.append(os.path.join(root, file))
    
    if len(fileFormatFiles)==0:
        logging.info(f'No files found in format {file_format} to convert! exiting...')
        quit()

    logging.info(f'{len(fileFormatFiles)} Files found to convert!')
    logging.debug(f'Files found: {fileFormatFiles}')

    for i in range(len(fileFormatFiles)):
        # set params
        rawtrnc = fileFormatFilesRaw[i][:-file_format_length]
        filename = fileFormatFiles[i]
        output_filename = filename[:-file_format_length] + ".mp4"

        # send slack message starting transcode
        result = sendParentMsg(f'Starting Transcode {rawtrnc}')
        ts=result['ts']
        addReact('beachball', ts)

        # record start time
        startTime = time.time()

        # transcode!
        logging.info(f'Transcoding {rawtrnc}')
        command = "ffmpeg -hide_banner -loglevel fatal -stats -i \"" + filename + "\" -vcodec h264_videotoolbox -b:v 3000k \"" + output_filename +"\""
        try:
            if os.system(command) != 0:
                raise Exception('FFMPEG has not completed successfully! Please check output of ffmpeg!')
        except Exception as e:
            removeReact('beachball', ts)
            errorOccurred(e, ts)

        # record end time and compute total time (rounded)
        endTime = time.time()
        totalTime = endTime - startTime
        totalTime = round(totalTime, 3)

        # update parent slack message to say complete, reply with total time, and remove the beach ball loading reaction
        updateMsg(f"Transcode of {rawtrnc} completed! :party_parrot:", ts)
        sendReplyMsg(f'Completed in {totalTime} seconds!', ts)
        removeReact('beachball', ts)
        
        logging.info(f'DONE! Transcode of {rawtrnc} completed in {totalTime} seconds!')

        # move old file out of directory into postProcessBAK folder
        moveToPath = f"{path}/OLDFILE_"+rawtrnc+".mkv"
        try:
            os.rename(filename, moveToPath)
        except Exception as e:
            errorOccurred(e)

        sendReplyMsg(f"Non-transcoded file renamed to {moveToPath}", ts)
        addReact('white_check_mark', ts)


if __name__ == "__main__":
    main()