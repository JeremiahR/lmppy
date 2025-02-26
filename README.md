# Tiny Lightning Peer

A tiny lightning network peer for testing and understanding the network. It is not intended for production and is not audited or verified.

Written in Python so that it may be quickly modified. Uses [pyln-proto](https://github.com/ElementsProject/lightning/tree/master/contrib/pyln-proto) for most of the heavy lifting.

# Usage

`pip install uv`
`uv install`
`uv run python main.py pubkey@url:port`

For, you might use this to connect to a peer from a test network created in [polar](https://lightningpolar.com/).

This python will handshake and speak lightning to the remote node, printing status updates for each message.
