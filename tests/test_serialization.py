import sys
from pathlib import Path

# Add the project root to sys.path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from app.serialization import MessageTypeElement


def test_decode_type_of_init_message():
    data = bytes.fromhex(
        "001000021100000708a0880a8a59a1012006226e46111a0b59caaf126043eb5bbf28c34f3a5e332a1fc7b2b73cf188910f"
    )
    (m, new_data) = MessageTypeElement.from_bytes(data)
    assert type(m) is MessageTypeElement
    assert m.id == 16
    assert m.name == "init"
    assert len(new_data) == len(data) - 2
