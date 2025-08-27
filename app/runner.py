from __future__ import annotations
import asyncio
from telegram.ext import Application
from app.wire.bootstrap import bootstrap_application
from app.config.settings import settings

async def main():
    app, services = await bootstrap_application(settings.BOT_TOKEN)
    await app.initialize()
    print("Bot initialized. Use /start in DM.")
    await app.start()

    # Keep running until Ctrl+C
    try:
        await asyncio.Event().wait()
    except (KeyboardInterrupt, SystemExit):
        pass
    finally:
        await app.stop()

if __name__ == "__main__":
    asyncio.run(main())