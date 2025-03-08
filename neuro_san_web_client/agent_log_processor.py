
# Copyright (C) 2023-2025 Cognizant Digital Business, Evolutionary AI.
# All Rights Reserved.
# Issued under the Academic Public License.
#
# You can be released from the terms, and requirements of the Academic Public
# License by purchasing a commercial license.
# Purchase of a commercial license is mandatory for any use of the
# neuro-san SDK Software in commercial settings.
#
# END COPYRIGHT

from typing import Any
from typing import Dict
from flask_socketio import SocketIO

from neuro_san.internals.messages.chat_message_type import ChatMessageType
from neuro_san.message_processing.message_processor import MessageProcessor


class AgentLogProcessor(MessageProcessor):
    """
    Tells the UI there's an agent logs to process.
    """

    def __init__(self, socketio: SocketIO, sid: str):
        """
        Constructor
        """
        self.socketio: SocketIO = socketio
        self.sid: str = sid

    def process_message(self, chat_message_dict: Dict[str, Any], message_type: ChatMessageType):
        """
        Process the message.
        :param chat_message_dict: The ChatMessage dictionary to process.
        :param message_type: The ChatMessageType of the chat_message_dictionary to process.
        """
        if message_type == ChatMessageType.LEGACY_LOGS:
            # Ignore LEGACY_LOGS messages. They are redundant.
            return
        if chat_message_dict is None:
            print(">>>>chat_message_dict is None>>>>")
            return

        log_text = chat_message_dict.get("text")
        # Log message coming from the last agent
        agent_name = "None"
        if len(chat_message_dict) > 0:
            origin = chat_message_dict.get("origin", [])
            if len(origin) > 0:
                agent_name = origin[-1].get("tool")

        log_dict = {
            "log": f"{agent_name}: {log_text}",
            "agent_name": agent_name
        }

        print(f"LOG: {log_dict["log"]}")

        self.socketio.emit('agent_log', log_dict, room=self.sid)
