import sys
import socket
from pyln.proto.wire import connect
from pyln.proto.primitives import PrivateKey, PublicKey
from ecdsa import SigningKey, SECP256k1
from binascii import hexlify

MESSAGE_TYPES = {
    16: "Init",
}


def diagnose(message):
    print("Diagnosing message...")
    message_type = int.from_bytes(message[:2], byteorder="big", signed=True)
    print("Message type: ", MESSAGE_TYPES.get(message_type, message_type))
    print("Message length: ", len(message))
    print("Message content: ", hexlify(message[2:]).decode("ASCII"))


def main():
    if len(sys.argv) < 2:
        print("Usage: python lmppy.py pubkey@url:port")
        sys.exit(1)
    peer = sys.argv[1]

    node_id, host = peer.split("@")
    host, port = host.split(":")
    port = int(port)
    print(f"Host: {host}, Port: {port}, Public Key: {node_id}")

    node_id = PublicKey(bytes.fromhex(node_id))

    private_key = SigningKey.generate(curve=SECP256k1)
    private_key = PrivateKey(private_key.to_string())

    sock = socket.socket()
    sock.connect((host, port))

    lc = connect(private_key, node_id, host, port=port, socks_addr=None)
    # Send an init message, with no global features, and 0b10101010 as local
    # features.
    lc.send_message(b"\x00\x10\x00\x00\x00\x01\xaa")

    # Now just read whatever our peer decides to send us
    while True:
        message = lc.read_message()
        diagnose(message)


if __name__ == "__main__":
    main()
