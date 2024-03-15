#!/usr/bin/env python3

import os
import argparse
import subprocess
import sys

def transcribe_audio(whisper_exe_path, model_path, audio_file_path, output_format='text'):
    # Construct the command to run the Whisper CLI
    command = [
        whisper_exe_path + 'main',
        '-m', model_path,
        '-f', audio_file_path,
        '-oj',  # Output the result in a JSON file
    ]

    # Run the command and capture the output
    result = subprocess.run(command, capture_output=True, text=True)

    if result.returncode == 0:
        print(result.stdout)
    else:
        print("Error transcribing audio:", result.stderr, file=sys.stderr)

if __name__ == "__main__":
    # Create the parser
    parser = argparse.ArgumentParser(description='Transcribe audio files using Whisper.')

    # Add the arguments
    parser.add_argument('-f', '--file', type=str, required=True, help='Path to the audio file')
    parser.add_argument('-m', '--model', type=str, default='models/ggml-large-v2-distil.bin', help='Path to the model file (default: models/ggml-large-v2-distil.bin)')
    parser.add_argument('-w', '--whisper-path', type=str, default='/Users/chenhao/Github/whisper.cpp/', help='Path to the Whisper executable directory (default: /Users/chenhao/Github/whisper.cpp/)')

    # Execute the parse_args() method
    args = parser.parse_args()

    # Update the model path to include the whisper executable path if not absolute
    if not os.path.isabs(args.model):
        args.model = os.path.join(args.whisper_path, args.model)

    transcribe_audio(args.whisper_path, args.model, args.file)
