import sys
from pathlib import Path

# Add the project root to sys.path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from app.message_decoder import MessageDecoder
from app.messages import (
    InitMessage,
)


def test_init_message():
    input_bytes = bytes.fromhex(
        "001000021100000708a0880a8a59a1012006226e46111a0b59caaf126043eb5bbf28c34f3a5e332a1fc7b2b73cf188910f"
    )
    m = MessageDecoder.from_bytes(input_bytes)
    assert type(m) is InitMessage
    assert m.type_code == 16
    assert m.type_name == "init"
    assert m.__str__() is not None, "Expected a non-empty string representation"
    assert m.length == 49
    assert m.global_features.data is not None
    assert m.local_features.data is not None
    assert m.to_bytes() == input_bytes

    # An init message, with no global features, and 0b10101010 as local
    # features.
    m = MessageDecoder.from_bytes(b"\x00\x10\x00\x00\x00\x01\xaa")
    assert type(m) is InitMessage
    assert m.type_code == 16
    assert m.type_name == "init"
    assert m.length == 7
    assert m.global_features.data == b""
    assert m.local_features.data == 0b10101010.to_bytes(1, "big")
    assert m.to_bytes() == b"\x00\x10\x00\x00\x00\x01\xaa"


def test_examples():
    """Tests that data/examples parse properly."""
    f = open("data/examples", "r")
    for line in f:
        msg = MessageDecoder.from_bytes(bytes.fromhex(line))
        assert msg.id is not None
        assert msg.name is not None
