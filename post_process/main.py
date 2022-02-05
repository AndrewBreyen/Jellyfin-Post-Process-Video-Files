# !/usr/bin/python3
import os
import logging
import time
from post_process import slack_functions
from dotenv import load_dotenv, find_dotenv

load_dotenv('./.env')

# logging
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)

def configure():
    global path, file_format, file_format_length
    path = os.getenv("convert_path")

    logging.info(f'path set to {path}')

    file_format = os.getenv("file_format")
    
    file_format_length = len(file_format)

def check_path():
    # check to see if file path exists
    if os.path.exists(path):
        logging.info('path exists, continuing')
    else:
        logging.info('path does not exist: attempting to mount...')
        os.system("osascript -e 'mount volume \"smb://macserver.local/Live TV Jellyfin Recordings [WD2TB]\"'")
        logging.info('path mounted! continuing...')

def get_files():
    # get all files in specified format in PATH 
    global fileFormatFiles, fileFormatFilesRaw
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

def transcode():
    for i in range(len(fileFormatFiles)):
        # set params
        rawtrnc = fileFormatFilesRaw[i][:-file_format_length]
        filename = fileFormatFiles[i]
        output_filename = filename[:-file_format_length] + ".mp4"

        # send slack message starting transcode
        result = slack_functions.sendParentMsg(f'Starting Transcode {rawtrnc}')
        ts=result['ts']
        slack_functions.addReact('beachball', ts)

        # record start time
        startTime = time.time()

        # transcode!
        logging.info(f'Transcoding {rawtrnc}')
        command = "ffmpeg -hide_banner -loglevel fatal -stats -i \"" + filename + "\" -vcodec h264_videotoolbox -b:v 3000k \"" + output_filename +"\""
        logging.debug(f'FFMPEG command: {command}')
        try:
            if os.system(command) != 0:
                raise Exception('FFMPEG has not completed successfully! Please check output of ffmpeg!')
        except Exception as e:
            slack_functions.removeReact('beachball', ts)
            slack_functions.errorOcurred(e, ts)

        # record end time and compute total time (rounded)
        totalTime = round(time.time() - startTime, 3)

        # update parent slack message to say complete, reply with total time, and remove the beach ball loading reaction
        slack_functions.updateMsg(f"Transcode of {rawtrnc} completed! :party_parrot:", ts)
        slack_functions.sendReplyMsg(f'Completed in {totalTime} seconds!', ts)
        slack_functions.removeReact('beachball', ts)
        
        logging.info(f'DONE! Transcode of {rawtrnc} completed in {totalTime} seconds!')

        # move old file out of directory into postProcessBAK folder
        moveToPath = f"{path}/OLDFILE_"+rawtrnc+".mkv"
        try:
            os.rename(filename, moveToPath)
        except Exception as e:
            slack_functions.errorOcurred(e)

        slack_functions.sendReplyMsg(f"Non-transcoded file renamed to {moveToPath}", ts)
        slack_functions.addReact('white_check_mark', ts)


def main():
    configure()
    check_path()
    get_files()
    transcode()


if __name__ == "__main__":
    main()