"""
Convert files in SERIES_PATH specified in .env to allow for direct playback
"""

# !/usr/bin/python3
import os
import logging
import sys
from pathlib import Path
from dotenv import load_dotenv
from slack_sdk import WebClient

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)

# setup env file (.env)
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

# setup slack client using token and channel from ENV file
client = WebClient(token=os.environ.get("SLACK_TOKEN"))
channel = os.environ.get("SLACK_CHANNEL")

# set path directory from ENV file
path = os.environ['SERIES_PATH']
logging.info('path set to %s', path)


def add_react(react, parent_msg_timestamp):
    """Add reaction specified to parent message specified by timestamp"""
    client.reactions_add(channel=channel,
                         name=react,
                         timestamp=parent_msg_timestamp)


def remove_react(react, parent_msg_timestamp):
    """Remove reaction specified to parent message specified by timestamp"""
    client.reactions_remove(channel=channel,
                            name=react,
                            timestamp=parent_msg_timestamp)


def send_parent_msg(msg):
    """Send parent Slack message"""
    return client.chat_postMessage(channel=channel, text=msg)


def send_reply_msg(msg, parent_msg_timestamp):
    """Send reply msg to parent message specified by timestamp"""
    client.chat_postMessage(channel=channel,
                            thread_ts=parent_msg_timestamp,
                            text=msg)


def error_occurred(msg, parent_msg_timestamp):
    """Add error occured reply message and add error reaction"""
    client.chat_postMessage(channel=channel,
                            thread_ts=parent_msg_timestamp,
                            text=f"ERROR: {msg}",)
    add_react('warning', parent_msg_timestamp)

    logging.critical('ERROR: %s', msg)
    sys.exit()


def main():
    """main method"""
    # check to see if file path exists
    if os.path.exists(path):
        logging.info('path exists, continuing')
    else:
        logging.info('path does not exist: attempting to mount...')
        os.system(
            "osascript -e 'mount volume \"smb://macserver.local/Live TV Jellyfin Recordings [WD2TB]\"'")
        logging.info('path mounted! continuing...')

    # get all TS files in directory, save to ts_files array
    ts_files = []
    ts_files_raw = []
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith('.ts'):
                ts_files_raw.append(file)
                ts_files.append(os.path.join(root, file))

    if len(ts_files) == 0:
        logging.info('No files found to convert! exiting...')
        sys.exit()

    logging.info('%i Files found to convert!', len(ts_files))
    logging.debug('Files found: %s', ts_files)

    for i in range(len(ts_files)):
        # set params
        rawtrnc = ts_files_raw[i][:-3]
        filename = ts_files[i]
        filename_mp4 = filename[:-3] + ".mp4"

        # send slack message starting transcode
        result = send_parent_msg(f'Starting Transcode {rawtrnc}')
        parent_msg_timestamp = result['ts']
        add_react('beachball', parent_msg_timestamp)

        # transcode
        logging.info('Transcoding %s', rawtrnc)
        command = "ffmpeg -hide_banner -loglevel fatal -stats -i \"" + filename + \
            "\" -vcodec h264_videotoolbox -b:v 3000k -acodec aac \"" + filename_mp4 + "\""
        try:
            if os.system(command) != 0:
                raise Exception(
                    'FFMPEG has not completed successfully! Please check output of ffmpeg!')
        except Exception as error:
            remove_react('beachball', parent_msg_timestamp)
            error_occurred(error, parent_msg_timestamp)

        send_reply_msg('Transcode complete!', parent_msg_timestamp)
        remove_react('beachball', parent_msg_timestamp)

        logging.info('DONE Transcoding %s!', rawtrnc)

        # # move old file out of directory into postProcessBAK folder
        # moveToPath = "/Volumes/Live TV Jellyfin Recordings [WD2TB]/postProcessBAK/OLDFILE_" + rawtrnc + ".ts"

        # try:
        #     os.rename(filename, moveToPath)
        # except Exception as error:
        #     error_occurred(error)

        # send_reply_msg('Non-transcoded file moved to postProcessBAK folder', parent_msg_timestamp)

        # delete non-transcoded file
        try:
            os.remove(filename)
        except Exception as error:
            error_occurred(error, parent_msg_timestamp)

        logging.info('Removed non-transcoded file %s', rawtrnc)
        send_reply_msg('Non-transcoded file removed', parent_msg_timestamp)

        send_reply_msg('Done! :party_parrot:', parent_msg_timestamp)
        add_react('white_check_mark', parent_msg_timestamp)


if __name__ == "__main__":
    main()
