from bot.bot import main
import logging

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        import asyncio
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("bot stop working")

    asyncio.run(main())

