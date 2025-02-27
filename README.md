# Lightning Mini Peer

A tiny lightning network peer for testing and understanding the network. It is not intended for production and is not audited or verified.

Written in Python so that it may be quickly modified. Uses [pyln-proto](https://github.com/ElementsProject/lightning/tree/master/contrib/pyln-proto) as a base layer for [Bolt 8](https://github.com/lightning/bolts/blob/master/08-transport.md).

# Usage

`pip install uv`
`uv install`
`uv run python -m app.main pubkey@url:port`

For example, you might use this to connect to a peer from a test network created in [polar](https://lightningpolar.com/).

This python will handshake and speak lightning to the remote node, printing status updates for each message.
