from dataclasses import dataclass

from pyln.proto.primitives import PublicKey


@dataclass
class Peer:
    node_id: PublicKey
    host: str
    port: int

    @classmethod
    def from_string(cls, s: str):
        node_id, host = s.split("@")
        host, port = host.split(":")
        port = int(port)
        node_id = PublicKey(bytes.fromhex(node_id))
        return cls(node_id, host, port)
