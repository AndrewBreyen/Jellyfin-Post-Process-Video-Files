# !/usr/bin/python3
import os
import sys
import logging

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)

path = "/Volumes/Live TV Jellyfin Recordings [WD2TB]/Series"
logging.info(f'path set to {path}')



# check to see if file path exists
if os.path.exists(path):
    logging.info('path exists, continuing')
else:
    logging.fatal('path does not exist: is the HD mounted?')
    #sys.exit("EXITING: path does not exist: is the HD mounted?")

# get all TS files on 
tsFiles = []
tsFilesRaw = []
for root, dirs, files in os.walk(path):
    for file in files:
        if file.endswith('.ts'):
            tsFilesRaw.append(file)
            tsFiles.append(os.path.join(root, file))

logging.info(f'{len(tsFiles)} Files found to convert!')
logging.debug(f'Files found: {tsFiles}')

for i in range(len(tsFiles)):
    rawtrnc = tsFilesRaw[i][:-3]
    filename = tsFiles[i]
    filenamemp4 = filename[:-3] + ".mp4"
    
    logging.info(f'Transcoding {rawtrnc}')
    command = "ffmpeg -hide_banner -stats -i \"" + filename + "\" -vcodec h264_videotoolbox -b:v 3000k -acodec aac \"" + filenamemp4 +"\""
    os.system(command)
    logging.info(f'DONE Transcoding {rawtrnc}!')
