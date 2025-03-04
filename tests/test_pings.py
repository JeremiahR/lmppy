import sys
from pathlib import Path

# Add the project root to sys.path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from app.message_decoder import MessageDecoder
from app.message_elements import MessageTypeElement, U16Element, U16VarBytesElement
from app.messages import (
    MessageProperty,
    PingMessage,
    PongMessage,
)


def test_construct_ping():
    m = PingMessage(
        id=18,
        name="ping",
        properties={
            MessageProperty.TYPE: MessageTypeElement(id=18, name="ping"),
            MessageProperty.NUM_PONG_BYTES: U16Element(num_bytes=10),
            MessageProperty.PING_OR_PONG_BYTES: U16VarBytesElement(
                1, data=bytes.fromhex("aa")
            ),
        },
    )
    # Note: not sure if this format is correct
    assert m.to_bytes() == b"\x00\x12\x00\n\x00\x01\xaa", (
        "Serialized bytes should match expected value"
    )

    m = PingMessage.create(10, bytes.fromhex("aa"))
    assert m.to_bytes() == b"\x00\x12\x00\n\x00\x01\xaa", (
        "Serialized bytes should match expected value"
    )


def test_generate_ping_response():
    msg_hex = "0012086c00500000003044d4216b3f1c92f3954700f52a4301f71158b7ef79a21f968b9c0f2d904c5f260aafe7d8a51df27614480e4314edbdee1d44d15a5d987c9b6533c9fd0b8d5a0c6233c667ffff7f2002000000"
    ping = MessageDecoder.from_bytes(bytes.fromhex(msg_hex))
    assert type(ping) is PingMessage
    pong = PongMessage.create_from_ping(ping)
    assert pong.num_bytes == ping.num_pong_bytes
