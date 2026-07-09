from pathlib import Path

from handlers.request import is_back_action


def test_project_files_exist():
    required = [
        Path("bot.py"),
        Path("config.py"),
        Path("handlers/request.py"),
        Path("handlers/admin.py"),
        Path("database/models.py"),
        Path("database/queries.py"),
    ]
    for path in required:
        assert path.exists(), f"Missing file: {path}"


def test_back_action_detection():
    assert is_back_action("🔙 برگشت") is True
    assert is_back_action("سلام") is False
    assert is_back_action(None) is False
