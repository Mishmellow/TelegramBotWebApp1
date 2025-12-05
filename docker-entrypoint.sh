#!/bin/bash
exec /usr/local/bin/python -m uvicorn main_webhook_server:app --host 0.0.0.0 --port $PORT