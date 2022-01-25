# !/usr/bin/python3
import os
import sys
import logging
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

path = os.environ['SERIES_PATH']
logging.info(f'path set to {path}')

def addReact(react, ts):
    client.reactions_add(channel=channel,
                        name=react,
                        timestamp=ts)

def removeReact(react, ts):
    client.reactions_remove(channel=channel,
                        name=react,
                        timestamp=ts)

def sendParentMsg(msg):
    return client.chat_postMessage(channel=channel, text=msg)

def sendReplyMsg(msg, ts):
    client.chat_postMessage(channel=channel,
                            thread_ts=ts,
                            text=msg)

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

    # get all TS files on 
    tsFiles = []
    tsFilesRaw = []
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith('.ts'):
                tsFilesRaw.append(file)
                tsFiles.append(os.path.join(root, file))
    
    if len(tsFiles)==0:
        logging.info(f'No files found to convert! exiting...')
        quit()

    logging.info(f'{len(tsFiles)} Files found to convert!')
    logging.debug(f'Files found: {tsFiles}')

    for i in range(len(tsFiles)):
        # set params
        rawtrnc = tsFilesRaw[i][:-3]
        filename = tsFiles[i]
        filenamemp4 = filename[:-3] + ".mp4"

        # send slack message starting transcode
        result = sendParentMsg(f'Starting Transcode {rawtrnc}')
        ts=result['ts']
        addReact('beachball', ts)

        # transcode
        logging.info(f'Transcoding {rawtrnc}')
        command = "ffmpeg -hide_banner -loglevel fatal -stats -i \"" + filename + "\" -vcodec h264_videotoolbox -b:v 3000k -acodec aac \"" + filenamemp4 +"\""
        try:
            if os.system(command) != 0:
                raise Exception('FFMPEG has not completed successfully! Please check output of ffmpeg!')
        except Exception as e:
            removeReact('beachball', ts)
            errorOccurred(e, ts)

        sendReplyMsg('Transcode complete!', ts)
        removeReact('beachball', ts)

        logging.info(f'DONE Transcoding {rawtrnc}!')

        # # move old file out of directory into postProcessBAK folder
        # moveToPath = "/Volumes/Live TV Jellyfin Recordings [WD2TB]/postProcessBAK/OLDFILE_"+rawtrnc+".ts"

        # try:
        #     os.rename(filename, moveToPath)
        # except Exception as e:
        #     errorOccurred(e)

        # sendReplyMsg('Non-transcoded file moved to postProcessBAK folder', ts)

        # delete non-transcoded file
        try:
            os.remove(filename)
        except Exception as e:
            errorOccurred(e)

        logging.info(f'Removed non-transcoded file {rawtrnc}')
        sendReplyMsg('Non-transcoded file removed', ts)


        sendReplyMsg('Done! :party_parrot:', ts)
        addReact('white_check_mark', ts)


if __name__ == "__main__":
    main()