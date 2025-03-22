
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
from neuro_san.internals.messages.message_utils import pretty_the_messages
from neuro_san.internals.messages.message_utils import convert_to_base_message
from neuro_san.message_processing.message_processor import MessageProcessor


class AgentLogProcessor(MessageProcessor):
    """
    Tells the UI there's an agent log to process.
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
        if chat_message_dict is None:
            print(">>>>chat_message_dict is None>>>>")
            return

        print("  ---------- ChatMessage ----------")
        # print(f"  MESSAGE_TYPE: {message_type}")
        # print(f"  CHAT_MESSAGE_DICT: {chat_message_dict}")
        # origin_log = self.process_origin(chat_message_dict["origin"])
        # print(f"  ORIGIN: {origin_log}")
        # print(f"  TYPE: {chat_message_dict['type']}")
        # print(f"  MESSAGE: {chat_message_dict['text']}")
        chat_message = convert_to_base_message(chat_message_dict, langchain_only=False)
        print(pretty_the_messages([chat_message]))

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

        # print("  ---------- ChatMessage ----------")
        # print(f"  LOG: {log_dict["log"]}")

        self.socketio.emit('agent_log', log_dict, room=self.sid)
        # Allow the event loop to process and send WebSocket messages before continuing execution.
        self.socketio.sleep(0)

    # @staticmethod
    # def process_origin(origin: List) -> str:
    #     # Extract tool names in order
    #     sequence = " -> ".join(tool['tool'] for tool in origin)
    #     return sequence
