import unittest
import subprocess

class TestTranscription(unittest.TestCase):
    def test_successful_transcription(self):
        script_path = 'src/websearch_cli.py'
        result = subprocess.run(['python', script_path, '-t', 'uptodate', '-q', 'heart failure'], capture_output=True, text=True)
        self.assertIn('UpToDate 2018', result.stdout, "The fetched content should include 'UpToDate 2018'")
        self.assertIn('heart failure', result.stdout, "The fetched content should include 'heart failure'")

if __name__ == '__main__':
    unittest.main()
