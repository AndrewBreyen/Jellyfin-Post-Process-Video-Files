from slack_sdk import WebClient
import logging
from post_process import config_helper

# config = config_helper.read_config()

# client = WebClient(token=(config['Slack']['slack_token']))
# channel = config['Slack']['slack_channel']

client = WebClient(token='xoxb-2960424248564-2979465734582-sFmEOtWpcsD1h2UHVRSGjwOK')
channel = 'C02U64GT5QB'

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
def errorOcurred(msg, ts):
    client.chat_postMessage(channel=channel,
                            thread_ts=ts,
                            text=f"ERROR: {msg}",)
    addReact('warning', ts)
    
    logging.critical(f'ERROR: {msg}')
    quit()