# Features

## Todos

- Async -> send pings in another thread, so that can connect to > 1 node, and chat w/ node while pings are going.
- Recieve pings and respond (only sends pings now).
- Support node_announcement and discovery.
- Rework serialization (more than one signature, etc.)
    - starts as a list of named values
    - minimal abstraction
    - can create constructors later, but devs will likely value the composability
    - channel_announcement as an example
      [message_type]
      [signature:node_signature_1]
      [signature:node_signature_2]
      [signature:bitcoin_signature_1]
      [signature:bitcoin_signature_2]
      [u16:len]
      [len*byte:features]
      [chain_hash:chain_hash]
      [short_channel_id:short_channel_id]
      [point:node_id_1]
      [point:node_id_2]
      [point:bitcoin_key_1]
      [point:bitcoin_key_2]
- Learn about new nodes and connect to them -> build graph outward.
- Potentially a UI with [textual](https://textual.textualize.io/), similar to [lazydocker](https://github.com/jesseduffield/lazydocker).

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
