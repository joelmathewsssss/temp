import os
import signal
import time
import sys
import sounddevice as sd
from gpiozero import Button
from elevenlabs.client import ElevenLabs
from elevenlabs.conversational_ai.conversation import Conversation, ConversationInitiationData
from elevenlabs.conversational_ai.default_audio_interface import DefaultAudioInterface

# --- CRITICAL SYSTEM ROUTING ---
# Forces Python to use the PipeWire server we just configured
os.environ["SDL_AUDIODRIVER"] = "pulseaudio"
os.environ["ALSA_CARD"] = "default"

# --- Hardware Setup ---
activation_button = Button(17)
is_triggered = False

def handle_button_press():
    global is_triggered
    if not is_triggered:
        is_triggered = True
        print("\n[Button Pressed] Starting Translation Session...")

activation_button.when_pressed = handle_button_press

# --- ElevenLabs Setup ---
# Use environment variables for security
api_key = os.getenv("ELEVENLABS_API_KEY")
agent_id = os.getenv("ELEVENLABS_AGENT_ID")

if not api_key or not agent_id:
    print("ERROR: ELEVENLABS_API_KEY or ELEVENLABS_AGENT_ID not found in environment.")
    sys.exit(1)

client = ElevenLabs(api_key=api_key)
config = ConversationInitiationData()

def create_conversation():
    # DefaultAudioInterface() looks at your .asoundrc and wpctl defaults
    audio_interface = DefaultAudioInterface()
    
    # Explicitly telling the library to use the system 'default' 
    # which we locked to the QuadCast and MUVO
    audio_interface.input_device = "default"
    audio_interface.output_device = "default"
    
    return Conversation(
        client,
        agent_id,
        config=config,
        requires_auth=True,
        audio_interface=audio_interface,
        callback_agent_response=lambda response: print(f"Agent: {response}"),
        callback_user_transcript=lambda transcript: print(f"User: {transcript}"),
    )

print("------------------------------------------------")
print("  TRANSLATOR READY (USB Mic + Bluetooth Speaker)")
print("  Press Button on GPIO 17 to start session.     ")
print("------------------------------------------------")

# --- Main Loop ---
try:
    while True:
        if is_triggered:
            try:
                # Pre-warming the Bluetooth connection
                print("Waking up speaker...")
                time.sleep(0.5)
                
                conversation = create_conversation()
                
                def signal_handler(sig, frame):
                    print("\nClosing session...")
                    conversation.end_session()
                    sys.exit(0)
                
                signal.signal(signal.SIGINT, signal_handler)

                conversation.start_session()
                print("Conversation active. Speak now.")
                
                conversation.wait_for_session_end()
                
            except Exception as e:
                print(f"Session Error: {e}")
            finally:
                is_triggered = False
                print("\nSession ended. Waiting for next button press...")
        
        time.sleep(0.1)

except KeyboardInterrupt:
    print("\nPowering down translator...")
