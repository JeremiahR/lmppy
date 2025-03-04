import asyncio

from pyln.proto.primitives import PrivateKey, PublicKey
from pyln.proto.wire import LightningConnection, connect

from app.message_decoder import MessageDecoder
from app.messages import Message, PingMessage

DEFAULT_PING_INTERVAL = 120


class PeerConnection:
    lc: LightningConnection
    local_private_key: PrivateKey
    node_id: PublicKey
    host: str
    port: int
    running: bool

    def __init__(self, s: str, local_private_key: PrivateKey):
        node_id, host = s.split("@")
        host, port = host.split(":")

        self.host = host
        self.local_private_key = local_private_key
        self.port = int(port)
        self.node_id = PublicKey(bytes.fromhex(node_id))
        self.running = True
        self.outgoing_messages = asyncio.Queue()

        self.lc = connect(self.local_private_key, self.node_id, self.host, port=self.port)  # pyright: ignore

    def __str__(self):
        return f"ln://{self.node_id.to_bytes().hex()}@{self.host}:{self.port}"

    async def send(self, message: Message):
        """Adds a message to the outgoing queue"""
        await self.outgoing_messages.put(message)

    async def receive_messages(self):
        """Asynchronously reads incoming messages"""
        while self.running:
            try:
                data = await asyncio.to_thread(self.lc.read_message)
                message = MessageDecoder.from_bytes(data)
                print(f"{self} Received:", message)
            except ValueError:  # deep error in pyln that we are ignoring for now
                await asyncio.sleep(1)  # Avoid excessive looping

    async def send_messages(self):
        """Sends messages from the queue"""
        while self.running:
            try:
                msg = await self.outgoing_messages.get()
                await asyncio.to_thread(self.lc.send_message, msg.to_bytes())
                print(f"{self} Sent:", msg)
            except Exception as e:
                print(f"{self} Error sending message: {e}")

    async def ping_peer(self):
        """Sends a ping every DEFAULT_PING_INTERVAL seconds"""
        while self.running:
            ping = PingMessage.create(10, bytes.fromhex("aa"))
            await self.send(ping)
            await asyncio.sleep(DEFAULT_PING_INTERVAL)

    async def start(self):
        self.tasks = [
            asyncio.create_task(self.receive_messages()),
            asyncio.create_task(self.send_messages()),
            asyncio.create_task(self.ping_peer()),
        ]

    async def stop(self):
        self.running = False
        for task in self.tasks:
            task.cancel()

    def send_init(self):
        # Send an init message, with no global features, and 0b10101010 as local features.
        self.lc.send_message(b"\x00\x10\x00\x00\x00\x01\xaa")
