# import asyncio
# import base64
# import os
# import time
# from dotenv import load_dotenv
# import datetime

# # Import Hume client and related classes
# from hume.client import AsyncHumeClient
# from hume.empathic_voice.chat.socket_client import ChatConnectOptions, ChatWebsocketConnection
# from hume.empathic_voice.chat.types import SubscribeEvent
# from hume.core.api_error import ApiError
# from hume import MicrophoneInterface, Stream

# # Import simpleaudio for playback
# import simpleaudio as sa
# import wave

# def play_audio(audio_bytes):
#     """
#     Play raw audio bytes using simpleaudio.
#     """
#     play_obj = sa.play_buffer(audio_bytes, num_channels=1, bytes_per_sample=2, sample_rate=16000)
#     play_obj.wait_done()

# class WebSocketHandler:
#     """Interface for containing the EVI WebSocket and associated socket handling behavior."""

#     def __init__(self):
#         """Construct the WebSocketHandler, initially assigning the socket to None and the byte stream to a new Stream object."""
#         self.socket = None
#         self.byte_strs = Stream.new()
#         self.waiting_for_response = False
#         self.assistant_speaking = False
#         self.audio_player_task = None
#         self.user_has_spoken = False  # Flag to track if the user has spoken
#         self.chat_initialized = False  # Flag to track if chat is initialized

#     def set_socket(self, socket: ChatWebsocketConnection):
#         """Set the socket."""
#         self.socket = socket

#     async def on_open(self):
#         """Logic invoked when the WebSocket connection is opened."""
#         print("WebSocket connection opened.")
#         print("Waiting for you to speak... (Press Ctrl+C to exit)")

#     async def on_message(self, message: SubscribeEvent):
#         """Callback function to handle a WebSocket message event."""
#         now = datetime.datetime.now().strftime("%H:%M:%S")

#         if message.type == "chat_metadata":
#             chat_id = message.chat_id
#             chat_group_id = message.chat_group_id
#             print(f"[{now}] Chat initialized - ID: {chat_id}, Group: {chat_group_id}")
#             self.chat_initialized = True
            
#         elif message.type == "user_message":
#             role = message.message.role.upper()
#             message_text = message.message.content
#             print(f"[{now}] {role}: {message_text}")
#             self.waiting_for_response = True
#             self.user_has_spoken = True  # Mark that the user has spoken
            
#         elif message.type == "assistant_message":
#             # Only process assistant messages after the user has spoken
#             if self.user_has_spoken:
#                 role = message.message.role.upper()
#                 message_text = message.message.content
#                 print(f"[{now}] {role}: {message_text}")
#                 self.assistant_speaking = True
            
#         elif message.type == "audio_output":
#             # Only process audio if the user has spoken first
#             if self.user_has_spoken:
#                 message_str: str = message.data
#                 message_bytes = base64.b64decode(message_str.encode("utf-8"))
#                 await self.byte_strs.put(message_bytes)
            
#         elif message.type == "assistant_message_done":
#             if self.user_has_spoken:
#                 self.waiting_for_response = False
#                 self.assistant_speaking = False
#                 print(f"[{now}] Assistant finished speaking. Ready for your input...")
            
#         elif message.type == "error":
#             error_message = message.message
#             error_code = message.code
#             print(f"[{now}] ERROR ({error_code}): {error_message}")
#             raise ApiError(f"Error ({error_code}): {error_message}")
            
#         elif message.type == "speech_detection":
#             if message.is_speech_detected:
#                 print(f"[{now}] Speech detected...")
#             else:
#                 print(f"[{now}] Speech ended.")
                
#         elif message.type == "transcript_partial":
#             print(f"[{now}] Partial: {message.text}")
            
#         elif message.type == "transcript_final":
#             print(f"[{now}] Final: {message.text}")

#     async def audio_player(self):
#         """Process audio from the stream."""
#         try:
#             while True:
#                 audio_chunk = await self.byte_strs.get()
#                 if audio_chunk and self.user_has_spoken:
#                     # Play the audio chunk only if user has spoken
#                     play_audio(audio_chunk)
#         except Exception as e:
#             print(f"Error in audio player: {e}")

#     async def on_close(self):
#         """Logic invoked when the WebSocket connection is closed."""
#         print("WebSocket connection closed.")

#     async def on_error(self, error):
#         """Logic invoked when an error occurs in the WebSocket connection."""
#         print(f"Error: {error}")

# async def main() -> None:
#     # Load environment variables from the .env file.
#     load_dotenv()
#     HUME_API_KEY = os.getenv("HUMEAI_API_KEY")
#     HUME_CONFIG_ID = os.getenv("HUMEAI_CONFIG_ID")
#     HUME_SECRET_KEY = os.getenv("HUMEAI_SECRET_KEY")
#     if not HUME_API_KEY or not HUME_CONFIG_ID or not HUME_SECRET_KEY:
#         raise ValueError("Please set HUMEAI_API_KEY, HUMEAI_CONFIG_ID, and HUMEAI_SECRET_KEY in your .env file.")

#     client = AsyncHumeClient(api_key=HUME_API_KEY)
    
#     # Define the connection options.
#     options = ChatConnectOptions(
#         config_id=HUME_CONFIG_ID,
#         secret_key=HUME_SECRET_KEY,
#         wait_for_user_message=True,  # This ensures the AI waits for user input before responding
#         enable_auto_ptt=False  # Disable auto push-to-talk to ensure AI doesn't speak first
#     )

#     # Instantiate your WebSocketHandler.
#     websocket_handler = WebSocketHandler()

#     try:
#         # Connect with callbacks for open, message, close, and error.
#         async with client.empathic_voice.chat.connect_with_callbacks(
#             options=options,
#             on_open=websocket_handler.on_open,
#             on_message=websocket_handler.on_message,
#             on_close=websocket_handler.on_close,
#             on_error=websocket_handler.on_error
#         ) as socket:
#             # Set the socket into the handler.
#             websocket_handler.set_socket(socket)
            
#             # Start the audio player task
#             audio_player_task = asyncio.create_task(websocket_handler.audio_player())
            
#             # Start the microphone interface with the correct parameters
#             mic_task = asyncio.create_task(
#                 MicrophoneInterface.start(
#                     socket,
#                     # byte_stream=websocket_handler.byte_strs,
#                     allow_user_interrupt=True
#                 )
#             )
            
#             # Wait for both tasks
#             await asyncio.gather(mic_task, audio_player_task)
            
#     except KeyboardInterrupt:
#         print("\nExiting program...")
#     except Exception as e:
#         print(f"Error: {e}")

# if __name__ == "__main__":
#     asyncio.run(main())


from hume.legacy import HumeVoiceClient, MicrophoneInterface, VoiceConfig
from dotenv import load_dotenv
import asyncio
import os

async def main() -> None:
    load_dotenv() # Load environment variables from.env file.
    HUME_API_KEY = os.getenv("HUMEAI_API_KEY")
    CONFIG_ID = os.getenv("HUMEAI_CONFIG_ID")


    client = HumeVoiceClient(api_key=HUME_API_KEY)

    async with client.connect(config_id=CONFIG_ID) as socket:
        await MicrophoneInterface.start(socket)

asyncio.run(main())