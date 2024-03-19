import unittest
import subprocess

class TestTranscription(unittest.TestCase):
    def test_query_img_ollama(self):
        script_path = 'sources/query-img-ollama.py'
        result = subprocess.run(['python', script_path, '-f', 'reference/paper.jpg', '-q', 'what does this image contain?'], capture_output=True, text=True)
        self.assertIn('sleep', result.stdout.lower(), "The fetched content should include 'sleep'")
        self.assertIn('detect', result.stdout.lower(), "The fetched content should include 'detect'")

if __name__ == '__main__':
    unittest.main()

