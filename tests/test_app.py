"""Test app self-test."""

import subprocess
import sys


def test_self_test():
    result = subprocess.run([sys.executable, "-m", "answer_dataset.app", "--self-test"], 
                          capture_output=True, text=True, timeout=30)
    assert result.returncode == 0
    assert "self-test OK" in result.stdout
