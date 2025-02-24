import sys
import hashlib
from ecdsa import SigningKey, SECP256k1

def generate_keypair():
    """Generates an ECDSA secp256k1 keypair."""
    private_key = SigningKey.generate(curve=SECP256k1)
    public_key = private_key.verifying_key.to_string()
    return private_key, public_key

def ecdh(private_key, peer_public_key):
    """Derives a shared secret using ECDH."""
    peer_pub = SigningKey.from_string(peer_public_key, curve=SECP256k1)
    shared_secret = private_key.privkey.secret_multiplier * peer_pub.pubkey.point
    return hashlib.sha256(int.to_bytes(shared_secret.x(), 32, "big")).digest()

def main():
    if len(sys.argv) < 2:
        print("Usage: python lmppy.py pubkey@url:port")
        sys.exit(1)
    peer = sys.argv[1]
    print("Connecting to peer:", peer)

    private_key, public_key = generate_keypair()
    print("Public key:", public_key.hex())

if __name__ == "__main__":
    main()
