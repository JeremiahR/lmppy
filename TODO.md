# Features

## Todo

- Async -> send pings in another thread.
- Recieve pings and respond.
- Support node_announcement.
- Advanced serialization (more than one signature, etc.)
- Learn about new nodes and connect to them -> build graph outward.
- Frontend? Maybe with [textual](https://textual.textualize.io/).

## Completed

- Basic serializer/deserializer for (init, ping, pong, node_announcement).
- Send pings, recieve pongs.

# Spec

- What are we building?
    > Lightning "minipeer" like the bitcoin one (use library for noise protocol), implement as many P2P exchanges as you can
- Per Carla:
    > LDK does a whole lot under the hood that you don't want for a node like this - connecting to a bitcoin node, validating UTXOs etc.
    > For this project we're essentially thinking about the most lightweight, low effort shell of a lightning node that one could feasibly put up.
    > For example, if you're a researcher who'e interested in figuring out the parameters for minisketch gossip in lightning - you could just spin up a few of these and record whatever you see on the gossip network without having to bother with a bitcoin node at all.
    > You'll def want to re-use components like the bolt-8 handshake, because that's as lightweight as is gets already, but for the other protocol messages there's a lot that can be cut out.
