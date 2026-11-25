import unittest
import subprocess
import os
import sys

# Ensure the parent directory is in python path so we can import fetch_quota
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import fetch_quota

class TestVlfstatus(unittest.TestCase):
    
    def test_bash_syntax(self):
        """Verify that vlfstatus script has valid bash syntax."""
        script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../vlfstatus'))
        result = subprocess.run(['bash', '-n', script_path], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, f"Bash syntax check failed: {result.stderr}")
        
    def test_install_script_syntax(self):
        """Verify that install.sh script has valid bash syntax."""
        script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../install.sh'))
        if os.path.exists(script_path):
            result = subprocess.run(['bash', '-n', script_path], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, f"Install script syntax check failed: {result.stderr}")

    def test_help_flags(self):
        """Verify -h and --help print usage and exit cleanly without starting the bar loop."""
        script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../vlfstatus'))
        outputs = []
        for flag in ('-h', '--help'):
            result = subprocess.run(
                [script_path, flag],
                capture_output=True,
                text=True,
                timeout=5,
            )
            self.assertEqual(result.returncode, 0, f"{flag} exited with {result.returncode}: {result.stderr}")
            self.assertIn('Usage: vlfstatus [OPTIONS]', result.stdout)
            self.assertIn('-h, --help', result.stdout)
            self.assertNotIn('"version": 1', result.stdout)
            self.assertEqual(result.stderr, '')
            outputs.append(result.stdout)
        self.assertEqual(outputs[0], outputs[1])

    def test_unknown_option(self):
        """Verify unknown options exit non-zero with an error instead of starting the bar loop."""
        script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../vlfstatus'))
        result = subprocess.run(
            [script_path, '--invalid-option'],
            capture_output=True,
            text=True,
            timeout=5,
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn('Unknown option: --invalid-option', result.stderr)
        self.assertEqual(result.stdout, '')

    def test_fetch_quota_definitions(self):
        """Verify core functions are defined in fetch_quota."""
        self.assertTrue(hasattr(fetch_quota, 'get_client_secret'))
        self.assertTrue(hasattr(fetch_quota, 'fetch_quota_from_agy_cli'))
        self.assertTrue(hasattr(fetch_quota, 'refresh_token'))

if __name__ == '__main__':
    unittest.main()
