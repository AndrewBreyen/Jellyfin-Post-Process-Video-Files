"""Functions used to send and change slack messages"""
import logging
import os
import sys
from dotenv import load_dotenv
from slack_sdk import WebClient

load_dotenv("./.env")

client = WebClient(token=os.getenv("slack_token"))
channel = os.getenv("slack_channel")


def add_react(react, time_stamp):
    """Adds a specified reaction (react) to a slack message specified via timestamp (time_stamp)"""
    client.reactions_add(channel=channel, name=react, timestamp=time_stamp)


def remove_react(react, time_stamp):
    """Removes a specified reaction (react) to a slack message specified via timestamp (time_stamp)"""
    client.reactions_remove(channel=channel, name=react, timestamp=time_stamp)


def send_parent_message(msg):
    """Sends a parent message with specified text (msg)"""
    return client.chat_postMessage(channel=channel, text=msg)


def send_reply_message(msg, time_stamp):
    """Sends a reply message with specified text (msg) to a parent message specified by timestamp (time_stamp)"""
    client.chat_postMessage(channel=channel, thread_time_stamp=time_stamp, text=msg)


def update_msg(msg, time_stamp):
    """updates a message specified by timestamp to be msg"""
    client.chat_update(channel=channel, ts=time_stamp, text=msg)


def error_ocurred(msg, time_stamp):
    """Note that an error occurred and reply to parent message specified by timestamp (time_stamp) with specified message (msg)"""
    client.chat_postMessage(
        channel=channel,
        thread_time_stamp=time_stamp,
        text=f"ERROR: {msg}",
    )
    add_react("warning", time_stamp)

    logging.critical("ERROR: %s", msg)
    sys.exit()
