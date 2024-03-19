import unittest
import subprocess

class TestTranscription(unittest.TestCase):
    def test_query_paper_ollama(self):
        script_path = 'sources/query-paper-ollama.py'
        result = subprocess.run(['python', script_path, '-f', 'reference/paper.pdf', '-q', 'what does this paper mainly talk about?'], capture_output=True, text=True)
        self.assertIn('atopic dermatis', result.stdout.lower(), "The fetched content should include 'atopic dermatis'")
        self.assertIn('scratch', result.stdout.lower(), "The fetched content should include 'scratch'")

if __name__ == '__main__':
    unittest.main()

