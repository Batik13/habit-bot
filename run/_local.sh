#!/usr/bin/env bash
export BOT_TOKEN="${BOT_TOKEN:?set}"
export TG_WEBHOOK_SECRET="${TG_WEBHOOK_SECRET:?set}"
uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload