# Jellyfin Post Process Video Files
 
Scripts in this repo can be used to bulk process video files in a Media Directory

To run:
In a shell:
`python3 /path/to/convertAll.py`

## Requirements:
- Python3
- pip
- ffmpeg
- python-dotenv
- slackclient
- .env file configured

### Installing Python3:
*prereq: brew is installed

In a shell:
1. `brew install python3`

### Installing ffmpeg:
*prereq: brew is installed

In a shell:
1. `brew install ffmpeg`

### Installing pip:
*prereq: python3 is installed

In a shell:
1. `curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py`
2. `python3 getpip.py`

### Installing slackclient
*prereq: pip is installed

In a shell:
1. pip install slackclient

### Installing python-dotenv
*prereq: pip is installed

In a shell:
1. pip install dotenv
<hr>

## To configure .env file:

Create a file named `.env` in the same directory as convertAll.py

Add to the file:
````
SLACK_TOKEN=YOUR_SLACK_TOKEN
SLACK_CHANNEL=YOUR_SLACK_CHANNEL
SERIES_PATH=/Volumes/Live TV Jellyfin Recordings [WD2TB]/Series
````


