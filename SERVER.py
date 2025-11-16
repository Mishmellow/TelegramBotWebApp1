# import asyncio
# import logging
# import os
# import sys
#
# from aiogram import Bot, Dispatcher
# from aiogram.enums.parse_mode import ParseMode
# from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
# from aiohttp import web
#
# logger = logging.getLogger(__name__)
#
# WEBHOOK_SECRET = os.getenv('WEBHOOK_SECRET')
# WEBHOOK_URL_BASE = os.getenv('WEBHOOK_URL_BASE')
#
# WEB_SERVER_HOST = os.getenv('WEB_SERVER_HOST', '0.0.0.0')
# WEB_SERVER_PORT = os.getenv('WEB_SERVER_PORT', '8030')
#
# WEBHOOK_PATH = f'/webhook/{WEBHOOK_SECRET}'
# WEBHOOK_URL = f'{WEBHOOK_URL_BASE}{WEBHOOK_PATH}'
#
# async def on_startup(bot: Bot):
#
#     if not WEBHOOK_URL_BASE: or not WEBHOOK_SECRET:
#         logger.error('🛑 WEBHOOK_URL_BASE или WEBHOOK_SECRET не установлен. Невозможно запустить Webhook.")')
#         sys.exit(1)
#
#     logger.info(f'Установка Webhook на URL: {WEBHOOK_URL}')
#
