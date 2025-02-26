# Tiny Lightning Peer

The goal of this project is to create a tiny lightning network peer for testing and understanding the network. It is not intended for production and is not audited or verified.

Most lightning software is written in compiled languages like Go, Rust and C. This is written in Python so that can eventually be used from the repl.

Built using [uv](https://docs.astral.sh/uv/) for package management. Implementation based on [lightning bolts](https://github.com/lightning/bolts).

# Implementation Status:

- Currently working on [BOLT #8](https://github.com/lightning/bolts/blob/master/08-transport.md).

# Usage

**Note:** This doesn't work yet.

The user runs the below command to connect to a peer on the lightning network. For example a peer from a test network created in [polar](https://lightningpolar.com/).
`uv run python lmp/main.py pubkey@url:port`

This python will handshake and speak lightning to the remote node, printing status updates for each message.

# Contributing

When faced with equivalent choice(s), we prefer pure python code over anything compiled.

This project uses pre-commit, install [with these instructions](https://pre-commit.com/#install) then `pre-commit install`.
Run tests with :`uv run pytest`
