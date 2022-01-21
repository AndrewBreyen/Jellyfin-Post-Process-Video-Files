# !/usr/bin/python3
import os
import logging
from pathlib import Path

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)


path = '/Volumes/Live TV Jellyfin Recordings [WD2TB]/Series'
logging.info(f'path set to {path}')


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

        # transcode
        logging.info(f'Transcoding {rawtrnc}')
        command = "ffmpeg -hide_banner -loglevel fatal -stats -i \"" + filename + "\" -vcodec h264_videotoolbox -b:v 3000k -acodec aac \"" + filenamemp4 +"\""
        try:
            if os.system(command) != 0:
                raise Exception('FFMPEG has not completed successfully! Please check output of ffmpeg!')
        except Exception as e:
            logging.critical(f'{e} FFMPEG error!')
            quit()

        logging.info(f'DONE Transcoding {rawtrnc}!')

        # move old file out of directory into postProcessBAK folder
        moveToPath = "/Volumes/Live TV Jellyfin Recordings [WD2TB]/postProcessBAK/OLDFILE_"+rawtrnc+".ts"

        try:
            os.rename(filename, moveToPath)
            logging.info(f'moved to post process BAK folder!')
        except Exception as e:
            logging.critical(f'{e} move error!')
            quit()

        logging.info(f'DONE!')

if __name__ == "__main__":
    main()