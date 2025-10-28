"""
Generate session string for Railway deployment
Run this LOCALLY before deploying!
"""

from telethon.sync import TelegramClient
from telethon.sessions import StringSession
import os

API_ID = int(input("Enter API_ID: "))
API_HASH = input("Enter API_HASH: ")
PHONE = input("Enter phone number (+1234567890): ")

with TelegramClient(StringSession(), API_ID, API_HASH) as client:
    print("\n✅ Session generated!")
    print("\nAdd this to Railway environment variables:")
    print(f"SESSION_STRING={client.session.save()}")
