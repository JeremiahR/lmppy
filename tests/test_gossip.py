import sys
from pathlib import Path

# Add the project root to sys.path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from app.message_decoder import MessageDecoder
from app.messages import GossipTimestampFilterMessage


def test_gossip_timestamp_filter():
    msg_hex = "010906226e46111a0b59caaf126043eb5bbf28c34f3a5e332a1fc7b2b73cf188910f67c6d3e3ffffffff"
    m = MessageDecoder.from_bytes(bytes.fromhex(msg_hex))
    assert type(m) is GossipTimestampFilterMessage
    assert m.first_timestamp.value == 1741083619  # pyright: ignore
    assert m.timestamp_range.value == 0xFFFFFFFF  # pyright: ignore
