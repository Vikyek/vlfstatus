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

    def test_fetch_quota_definitions(self):
        """Verify core functions are defined in fetch_quota."""
        self.assertTrue(hasattr(fetch_quota, 'get_ref_tokens'))
        self.assertTrue(hasattr(fetch_quota, 'fetch_quota_summary'))
        self.assertTrue(hasattr(fetch_quota, 'refresh_token'))

if __name__ == '__main__':
    unittest.main()
