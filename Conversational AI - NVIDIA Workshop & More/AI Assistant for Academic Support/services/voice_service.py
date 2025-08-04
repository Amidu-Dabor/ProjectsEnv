# services/voice_service.py

import os
import asyncio
import threading
from dotenv import load_dotenv
from hume.legacy import HumeVoiceClient, MicrophoneInterface, VoiceConfig

class VoiceChat:
    def __init__(self, api_key=None, config_id=None):
        load_dotenv()  # Load environment variables from .env file
        self.api_key = api_key or os.getenv("HUMEAI_API_KEY")
        self.config_id = config_id or os.getenv("HUMEAI_CONFIG_ID")
        self.voice_thread = None
        self.is_running = False
        
    def start_voice_chat(self, callback=None):
        """Start voice chat in a separate thread"""
        if self.voice_thread and self.is_running:
            return False  # Already running
            
        self.is_running = True
        self.voice_thread = threading.Thread(
            target=self._run_voice_chat_async,
            args=(callback,)
        )
        self.voice_thread.daemon = True
        self.voice_thread.start()
        return True
        
    def stop_voice_chat(self):
        """Stop the voice chat thread"""
        self.is_running = False
        if self.voice_thread:
            self.voice_thread.join(timeout=2)
            self.voice_thread = None
        return True
        
    def _run_voice_chat_async(self, callback=None):
        """Run the voice chat asyncio loop in the thread"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self._voice_chat_main(callback))
        loop.close()
        
    async def _voice_chat_main(self, callback=None):
        """Main voice chat async function"""
        try:
            client = HumeVoiceClient(api_key=self.api_key)
            
            # Message handler to process incoming voice-to-text
            def message_handler(message):
                if callback and message.text and message.text.strip():
                    # Send the transcript to the callback function
                    callback(message.text.strip())
            
            # Connect to HumeAI voice service
            async with client.connect(config_id=self.config_id) as socket:
                socket.register_message_handler(message_handler)
                await MicrophoneInterface.start(socket)
                
                # Keep running until stopped
                while self.is_running:
                    await asyncio.sleep(0.1)
                    
                # Stop gracefully
                await MicrophoneInterface.stop(socket)
                
        except Exception as e:
            print(f"Voice chat error: {e}")
            self.is_running = False