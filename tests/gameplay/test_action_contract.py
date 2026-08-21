import subprocess, sys
from pathlib import Path

def test_action_contract_validator():
    root = Path(__file__).resolve().parents[2]
    result = subprocess.run([sys.executable, str(root / 'tools/validate_action_contract.py')], cwd=root, capture_output=True, text=True, check=False)
    assert result.returncode == 0, result.stdout + result.stderr
    assert 'ACTION_CONTRACT PASS' in result.stdout
