A toy lightning peer.

The goal of this project is to create the lightest-possible-weight lightning peer for testing purposes. This is not verified or audited and should not be used in production.

Written in Python and using [uv](https://docs.astral.sh/uv/) for package management.

A good way to create a demo network is with [polar](https://lightningpolar.com/).

Usage:
`uv run python src/main.py pubkey@url:port`

For example:
`uv run python src/main.py 03df0d35f7e0efd274cc46387e45da08c358b71ca62bedfdfca10cc9f6482166da@127.0.0.1:9637`

# Contributing

This project uses pre-commit, install [with these instructions](https://pre-commit.com/#install) then `pre-commit install`.
Run tests with :`uv run pytest`
