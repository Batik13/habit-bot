from telegram.ext import Application, ApplicationBuilder
from app.handlers.start import onboarding_conv
from app.handlers.commands import stats_handler
from app.handlers.callbacks import callbacks_handler

async def register_handlers(app: Application):
    app.add_handler(onboarding_conv())
    app.add_handler(stats_handler())
    app.add_handler(callbacks_handler())

# Application creation (used by runner or FastAPI integration)
async def build_app(bot_token: str) -> Application:
    app = ApplicationBuilder().token(bot_token).build()
    await register_handlers(app)
    return app