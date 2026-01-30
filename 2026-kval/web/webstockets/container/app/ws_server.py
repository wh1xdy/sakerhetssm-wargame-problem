#!/usr/bin/env python

import asyncio
import json
import os


from websockets.asyncio.server import serve
from websockets.exceptions import ConnectionClosedError, ConnectionClosedOK

POLL_INTERVAL_SECONDS = 2


def load_feed(feed_name) -> dict:
    # We have an investor specific secret feed in /secret.txt, but this is not accessible for normal users because they are in the /feeds/ directory!
    target = "/feeds/"+feed_name
    with open(feed_name, "r", encoding="utf-8", errors='replace') as handle:
        return handle.read()


async def wsdata(websocket):
    """
    Stream JSON for the feed requested by the client via WebSocket messages.

    The client sends the filename (e.g. `lsoc.json`), and we keep streaming the
    corresponding JSON until another selection arrives.
    """
    selected_feed = None

    try:
        while True:
            try:
                message = await asyncio.wait_for(websocket.recv(), timeout=0.1)
                requested = message.strip()
                target = requested
                if not target:
                    await websocket.send(
                        json.dumps({"error": f"unknown feed '{requested}'"})
                    )
                    continue

                selected_feed = requested
                print(f"[ws] client requested feed: {target}")
            except asyncio.TimeoutError:
                pass

            if selected_feed:
                try:
                    payload = load_feed(selected_feed)
                    await websocket.send(json.dumps(payload))
                except (OSError) as exc:
                    await websocket.send(
                        json.dumps({"error": f"failed to read feed: {exc}"})
                    )
                    await asyncio.sleep(POLL_INTERVAL_SECONDS)
                    continue

                await asyncio.sleep(POLL_INTERVAL_SECONDS)
            else:
                await asyncio.sleep(0.1)

    except (ConnectionClosedError, ConnectionClosedOK):
        print("[ws] client disconnected")


async def main():
    async with serve(wsdata, "0.0.0.0", 8764):
        print("WebSocket server started on ws://0.0.0.0:8764")
        await asyncio.Future()  # Run forever


if __name__ == "__main__":
    asyncio.run(main())
