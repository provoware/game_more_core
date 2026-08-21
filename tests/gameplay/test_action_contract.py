import subprocess
import sys
from pathlib import Path


def test_action_contract_validator():
    root = Path(__file__).resolve().parents[2]
    result = subprocess.run(
        [sys.executable, str(root / "tools/validate_action_contract.py")],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stdout.count("🟢 Checkpoint") == 5
    assert "Ressourcenvertrag" in result.stdout
    assert "ACTION_CONTRACT PASS" in result.stdout


def test_action_contract_validator_help():
    root = Path(__file__).resolve().parents[2]
    result = subprocess.run(
        [sys.executable, str(root / "tools/validate_action_contract.py"), "--help"],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "Prüft Actions, Gewichte, Ressourcen und Manifest-Referenzen." in result.stdout
    assert "Ampel: 🟢 bestanden, 🟡 nicht ausgeführt, 🔴 fehlgeschlagen." in result.stdout
