"""Post-Process Files"""
# !/usr/bin/python3
import os
import logging
import sys
import time
from dotenv import load_dotenv
import ffmpeg
from post_process import slack_functions

load_dotenv("./.env")

# logging
logging.basicConfig(format="%(levelname)s:%(message)s", level=logging.INFO)

def configure():
    """Setup"""
    exists = os.path.isfile("./.env")
    if exists:
        logging.info(".env file exists!")
    else:
        logging.critical(
            ".env file oes not exist! Create an .env configuration file in the root of the directory "
        )
        raise FileNotFoundError(".env DNE!")

    global PATH, FILE_FORMAT, FILE_FORMAT_LENGTH
    PATH = os.getenv("convert_path")

    logging.info("PATH set to %s", PATH)

    FILE_FORMAT = os.getenv("file_format")

    FILE_FORMAT_LENGTH = len(FILE_FORMAT)


def check_path():
    """Check that PATH exists"""
    if os.path.exists(PATH):
        logging.info("PATH exists, continuing")
    else:
        logging.info("PATH does not exist: attempting to mount...")
        os.system(
            "osascript -e 'mount volume \"smb://macserver.local/Live TV Jellyfin Recordings [WD2TB]\"'"
        )
        logging.info("PATH mounted! continuing...")


def get_files():
    """get all files in specified format in PATH"""
    global FILE_FORMAT_FILES, FILE_FORMAT_FILES_RAW
    FILE_FORMAT_FILES = []
    FILE_FORMAT_FILES_RAW = []
    for root, dirs, files in os.walk(PATH):
        for file in files:
            if file.endswith(FILE_FORMAT):
                FILE_FORMAT_FILES_RAW.append(file)
                FILE_FORMAT_FILES.append(os.path.join(root, file))
    if len(FILE_FORMAT_FILES) == 0:
        logging.info("No files found in format %s to convert! exiting...", FILE_FORMAT)
        sys.exit()

    logging.info("%i Files found to convert!", len(FILE_FORMAT_FILES))
    logging.info("Files found: %s", FILE_FORMAT_FILES)


def transcode():
    """for each file, transcode"""
    for i in range(len(FILE_FORMAT_FILES)):
        # set params
        rawtrnc = FILE_FORMAT_FILES_RAW[i][:-FILE_FORMAT_LENGTH]
        filename = FILE_FORMAT_FILES[i]
        output_filename = filename[:-FILE_FORMAT_LENGTH] + ".mp4"

        # send slack message starting transcode
        result = slack_functions.send_parent_message(f"Starting Transcode {rawtrnc}")
        timestamp = result["ts"]
        slack_functions.add_react("beachball", timestamp)

        # record start time
        start_time = time.time()

        # transcode!
        logging.info("Transcoding %s", rawtrnc)
        # command = "ffmpeg -hide_banner -loglevel fatal -stats -i \"" + filename + "\" -vcodec h264_videotoolbox -b:v 3000k \"" + output_filename +"\""
        # logging.debug(f'FFMPEG command: {command}')

        (
            ffmpeg.input(filename)
            .output(output_filename, vcodec="h264_videotoolbox", acodec="copy", **{'b:v': 3000000}, loglevel="fatal")
            .run()
        )

        try:
            # if os.system(command) != 0:
            #     raise Exception('FFMPEG has not completed successfully! Please check output of ffmpeg!')
            print("do something")
        except ffmpeg.Error as exception:
            slack_functions.remove_react("beachball", timestamp)
            slack_functions.error_ocurred(exception, timestamp)

        # record end time and compute total time (rounded)
        total_time = round(time.time() - start_time, 3)

        # update parent slack message to say complete, reply with total time, and remove the beach ball loading reaction
        slack_functions.update_msg(
            f"Transcode of {rawtrnc} completed! :party_parrot:", timestamp
        )
        slack_functions.send_reply_message(
            f"Completed in {total_time} seconds!", timestamp
        )
        slack_functions.remove_react("beachball", timestamp)

        logging.info(
            "DONE! Transcode of %s completed in %d seconds!", rawtrnc, total_time
        )

        # TODO: change this path to move up one level to the postprocessBAK folder
        # move old file out of directory into postProcessBAK folder
        move_to_path = f"{PATH}/OLDFILE_" + rawtrnc + FILE_FORMAT
        try:
            os.rename(filename, move_to_path)
            logging.info("Non-transcoded file renamed to %s", move_to_path)
        except OSError as exception:
            slack_functions.error_ocurred(exception, timestamp)

        slack_functions.send_reply_message(
            f"Non-transcoded file renamed to {move_to_path}", timestamp
        )
        slack_functions.add_react("white_check_mark", timestamp)


def main():
    """main method"""
    configure()
    check_path()
    get_files()
    transcode()


if __name__ == "__main__":
    main()
