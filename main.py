import logging

from bot.bot import main

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        import asyncio

        print("bot start working")
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("bot stop working")
