#!/bin/bash
# Enter the directory
cd /home/immiuser/my_translator

# Activate the virtual environment
source env/bin/activate

# Set the hardware driver for the button
export GPIOZERO_PIN_FACTORY=lgpio

# Set your ElevenLabs credentials
export ELEVENLABS_API_KEY="sk_e7050538248ee37c1b60ad3267399a8d14708af46cc99650"
export ELEVENLABS_AGENT_ID="agent_1401kep9fzsrfjetmfkg7ahpy7zx"

# Run the script
python translator.py
