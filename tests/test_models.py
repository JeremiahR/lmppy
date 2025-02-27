import sys
from pathlib import Path

# Add the project root to sys.path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from app.messages import InitMessage, MessageDecoder


def test_init_message():
    m = MessageDecoder.from_bytes(
        bytes.fromhex(
            "001000021100000708a0880a8a59a1012006226e46111a0b59caaf126043eb5bbf28c34f3a5e332a1fc7b2b73cf188910f"
        )
    )
    assert type(m) is InitMessage
    assert m.type_code == 16
    assert m.type_name == "init"
    assert m.length == 49
