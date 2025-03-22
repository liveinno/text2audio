#!/usr/bin/env python3
import pyttsx3
import sys

print(f"Python version: {sys.version}")
print(f"pyttsx3 version: {pyttsx3.__version__ if hasattr(pyttsx3, '__version__') else 'Unknown'}")
print(f"pyttsx3 dir: {dir(pyttsx3)}")

try:
    print("Trying to initialize pyttsx3...")
    engine = pyttsx3.init()
    print("pyttsx3 initialized successfully!")
    
    print("Getting voices...")
    voices = engine.getProperty('voices')
    print(f"Found {len(voices)} voices")
    
except Exception as e:
    print(f"Error: {e}")
    print(f"Error type: {type(e)}")