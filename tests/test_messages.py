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
    assert m.global_features is not None
    assert m.local_features is not None

    # An init message, with no global features, and 0b10101010 as local
    # features.
    m = MessageDecoder.from_bytes(b"\x00\x10\x00\x00\x00\x01\xaa")
    assert type(m) is InitMessage
    assert m.type_code == 16
    assert m.type_name == "init"
    assert m.length == 7
    assert m.global_features.features == b""
    assert m.local_features.features == 0b10101010.to_bytes(1, "big")
    # assert m.serialize() == b"\x00\x10\x00\x00\x00\x01\xaa"
