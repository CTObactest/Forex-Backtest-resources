import asyncio

# Create and set a new event loop for the main thread 
# BEFORE importing Bot or Pyrogram to prevent RuntimeError
try:
    loop = asyncio.get_event_loop()
except RuntimeError:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

from bot import Bot

if __name__ == "__main__":
    Bot().run()
