"""
Experiment configuration.
Change OLLAMA_MODEL to match your local setup.
"""

import os

# Ollama settings
OLLAMA_BASE_URL = "http://localhost:11434"
# Default model; override without editing this file via OLLAMA_MODEL env var,
# e.g. `OLLAMA_MODEL=qwen2.5:14b python run_experiment.py`. Used to compare how
# model capacity (esp. base64 decoding) affects the encoding defense.
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3.1:8b")
TEMPERATURE = 1.0 # Match the paper's setting

# Experiment settings
NUM_ATTACK_DOCS = 50
ATTACK_KEYWORD = "TARGETKEYPHRASE" # Keyword payload for ASR measurement

# Spotlighting settings
DATAMARK_CHAR = "^"
DELIMITER_START = "<<"
DELIMITER_END = ">>"
# base64 is the paper's primary encoding choice. ROT13 is supported but
# weaker because the encoded text still reads as English-like characters,
# so the model may follow embedded instructions before decoding.
ENCODING_METHOD = "base64" # base64 or rot13