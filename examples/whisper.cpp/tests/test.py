import unittest
import subprocess

class TestTranscription(unittest.TestCase):
    def test_successful_transcription(self):
        # Path to the whisper-cli.py script
        script_path = 'src/whisper-cli.py'
        # Path to a known audio file for testing
        test_audio_file = 'samples/jfk.wav'
        # Expected transcription result for the known audio file
        expected_transcription = "And so, my fellow Americans, ask not what your country can do for you. Ask what you can do for your country."

        # Run the script with the test audio file
        result = subprocess.run(['python', script_path, '-f', test_audio_file], capture_output=True, text=True)

        self.assertEqual(result.returncode, 0, "Script failed to execute successfully.")
        self.assertIn(expected_transcription, result.stdout, "Transcription does not match expected output.")

if __name__ == '__main__':
    unittest.main()
