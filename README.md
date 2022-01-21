# Jellyfin Post Process Video Files
 
Scripts in this repo can be used to bulk process video files in a Media Directory

Requirements:
Python3
pip
ffmpeg
python-dotenv
slackclient

Installing Python3:
*prereq: brew is installed
In a shell:
1. `brew install python3`

Installing pip:
In a shell:
1. `curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py`
2. `python3 getpip.py`

Installing slackclient
*prereq: pip is installed
In a shell:
1. pip install slackclient