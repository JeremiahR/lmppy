# A tiny lightning peer.

The goal of this project is to create a lightweight lightning network peer for testing purposes. It is not verified or audited and should not be used in production.

Written in Python and using [uv](https://docs.astral.sh/uv/) for package management. Implementation based on [lightning bolts](https://github.com/lightning/bolts).

# Usage

**Note:** This doesn't work yet.

The user runs the below command to connect to a peer on the lightning network. Such a peer might first come from creating a test network with [polar](https://lightningpolar.com/).
`uv run python lmp/main.py pubkey@url:port`

This python will handshake and speak lightning to the remote node.

# Contributing

This project uses pre-commit, install [with these instructions](https://pre-commit.com/#install) then `pre-commit install`.
Run tests with :`uv run pytest`
