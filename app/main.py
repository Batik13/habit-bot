from __future__ import annotations
import asyncio
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from telegram import Update
from app.config.settings import settings
from app.wire.bootstrap import bootstrap_application

app = FastAPI(title="Habit Bot Webhook")

@app.on_event("startup")
async def startup():
    app.state.tg_app, app.state.services = await bootstrap_application(settings.BOT_TOKEN)
    # Start PTB application (which starts JobQueue)
    await app.state.tg_app.initialize()
    await app.state.tg_app.start()

@app.on_event("shutdown")
async def shutdown():
    await app.state.tg_app.stop()

@app.get("/health")
async def health():
    return {"ok": True}

@app.post("/tg/webhook")
async def telegram_webhook(request: Request):
    secret = request.headers.get("X-Telegram-Bot-Api-Secret-Token")
    if not secret or secret != settings.TG_WEBHOOK_SECRET:
        raise HTTPException(status_code=401, detail="invalid secret")

    data = await request.json()
    update = Update.de_json(data=data, bot=app.state.tg_app.bot)
    await app.state.tg_app.process_update(update)
    return JSONResponse({"ok": True})