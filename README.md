# Jellyfin Post Process Video Files
 
Scripts in this repo can be used to bulk process video files in a Media Directory

To run:
In a shell with working directory of cloned repo:
pip install .
post-process

## Requirements:
see `requirements.txt`

## Sample .env file:

Create a file named `.env` in the root of cloned repo

Add to the file:
````
slack_token = xoxb-your-slack-token
slack_channel = your-slack-channel-id

convert_path = /path/to/conversion/directory

file_format = .mkv
````


New Machine setup:
1. Clone repo
2. Install Brew from brew.sh
3. install pip:
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py

python3 get-pip.py

4. ** will change when migrated to python ffmpeg, but while using system calls: ** brew install ffmpeg
5. Using a terminal, CD into the cloned directory
6. pip install .