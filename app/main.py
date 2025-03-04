import asyncio
import signal

from app.peer import PeerConnection
from app.util import generate_private_key, parse_args


async def main():
    peers = []
    args = parse_args()
    private_key = generate_private_key()

    peer = PeerConnection(args.host, private_key)
    peer.send_init()
    peers.append(peer)

    asyncio.create_task(peer.start())
    stop_event = asyncio.Event()

    def handle_exit():
        print("\nCTRL+C received. Shutting down...")
        stop_event.set()

    loop = asyncio.get_running_loop()
    loop.add_signal_handler(signal.SIGINT, handle_exit)
    loop.add_signal_handler(signal.SIGTERM, handle_exit)

    try:
        await stop_event.wait()
    finally:
        # Just kill all the tasks
        tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
        if tasks:
            print(f"Cancelling {len(tasks)} remaining tasks...")
            for task in tasks:
                task.cancel()
            await asyncio.gather(*tasks, return_exceptions=True)
        print("All tasks cancelled. Exiting.")


if __name__ == "__main__":
    asyncio.run(main())  # Properly handles event loop start/stop
