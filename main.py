import sys
import socket
from pyln.proto.wire import LightningConnection
from pyln.proto.primitives import PrivateKey, PublicKey
from ecdsa import SigningKey, SECP256k1


def main():
    if len(sys.argv) < 2:
        print("Usage: python lmppy.py pubkey@url:port")
        sys.exit(1)
    peer = sys.argv[1]

    remote_pubkey, host = peer.split("@")
    host, port = host.split(":")
    port = int(port)
    print(f"Host: {host}, Port: {port}, Public Key: {remote_pubkey}")

    remote_pubkey = PublicKey(bytes.fromhex(remote_pubkey))

    private_key = SigningKey.generate(curve=SECP256k1)
    private_key = PrivateKey(private_key.to_string())

    sock = socket.socket()
    sock.connect((host, port))

    lc = LightningConnection(sock, remote_pubkey, private_key, True)
    lc.init_handshake()


if __name__ == "__main__":
    main()
