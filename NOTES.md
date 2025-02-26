- Looking at creating a lightweight lightning node
- Unfortunately, the rust-lightning component PeerChannelEncryptor for handling bolt8 [is private](https://github.com/lightningdevkit/rust-lightning/blob/main/lightning/src/ln/peer_channel_encryptor.rs)
- Attempts at creating a minimal lightning node using rust-lightning quickly spiral out of control, with increasing requirements in order to get a minimal stack working (key manager, channel manager, route manager, etc etc)
- There's an argument that python is better anyway, since it's interpreted and would be more amenable to modification while running.
- In order for that to happen, you'd want to handshake quickly and easily and them move onto capturing gossip/network traffic.
- Per Carla:
    > LDK does a whole lot under the hood that you don't want for a node like this - connecting to a bitcoin node, validating UTXOs etc.
    For this project we're essentially thinking about the most lightweight, low effort shell of a lightning node that one could feasibly put up.
    For example, if you're a researcher who'e interested in figuring out the parameters for minisketch gossip in lightning - you could just spin up a few of these and record whatever you see on the gossip network without having to bother with a bitcoin node at all.
    You'll def want to re-use components like the bolt-8 handshake, because that's as lightweight as is gets already, but for the other protocol messages there's a lot that can be cut out.