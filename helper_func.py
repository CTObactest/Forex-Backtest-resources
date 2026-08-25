#(©)Codexbotz

import base64
import re
import asyncio
import logging 
import motor.motor_asyncio
import hmac
import hashlib
from pyrogram import filters
from pyrogram.enums import ChatMemberStatus
from config import FORCE_SUB_CHANNEL, ADMINS, AUTO_DELETE_TIME, AUTO_DEL_SUCCESS_MSG, PREMIUM_CHANNEL, DB_URI, DB_NAME
from pyrogram.errors.exceptions.bad_request_400 import UserNotParticipant
from pyrogram.errors import FloodWait

# ---- ADD YOUR SECRET KEY HERE ----
# This key is used to sign your links. Keep it secret and never change it 
# once set, or all previously generated signed links will become invalid.
SECRET_HMAC_KEY = b"REPLACE_THIS_WITH_A_LONG_RANDOM_SECURE_STRING"

# ---- Link revocation store (separate collection, own client) ----
_revoke_client = motor.motor_asyncio.AsyncIOMotorClient(DB_URI)
_revoked_links_col = _revoke_client[DB_NAME].revoked_links

# ---- Premium channel, connected via /connectpremium instead of an env var ----
_settings_col = _revoke_client[DB_NAME].bot_settings

async def is_subscribed(filter, client, update):
    if not FORCE_SUB_CHANNEL:
        return True
    user_id = update.from_user.id
    if user_id in ADMINS:
        return True
    try:
        member = await client.get_chat_member(chat_id = FORCE_SUB_CHANNEL, user_id = user_id)
    except UserNotParticipant:
        return False

    if not member.status in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.MEMBER]:
        return False
    else:
        return True

async def get_premium_channel():
    """Returns the chat_id connected via /connectpremium, or None if not set yet."""
    doc = await _settings_col.find_one({"_id": "premium_channel"})
    return doc["chat_id"] if doc else None

async def set_premium_channel(chat_id: int, title: str = ""):
    await _settings_col.update_one(
        {"_id": "premium_channel"},
        {"$set": {"chat_id": chat_id, "title": title}},
        upsert=True
    )

async def is_premium_subscribed(client, user_id):
    """Checks if user_id is a member of the connected premium channel. Admins always pass."""
    if user_id in ADMINS:
        return True
    premium_channel = await get_premium_channel()
    if not premium_channel:
        premium_channel = PREMIUM_CHANNEL  # fallback for anyone still using the env var
    if not premium_channel:
        return False
    try:
        member = await client.get_chat_member(chat_id=premium_channel, user_id=user_id)
    except UserNotParticipant:
        return False
    except Exception:
        return False

    return member.status in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.MEMBER]


# ---- NEW SECURITY FUNCTIONS ----
def generate_signature(payload: str) -> str:
    """Generates a secure HMAC-SHA256 signature for the given payload."""
    signature = hmac.new(
        SECRET_HMAC_KEY, 
        payload.encode('utf-8'), 
        hashlib.sha256
    ).hexdigest()
    return signature[:10]  # Only need 10 chars for URL brevity

async def encode(string):
    """Signs the string payload and encodes it."""
    # 1. Generate a signature for the string (e.g. "premium-12345")
    signature = generate_signature(string)
    # 2. Append the signature to the string
    signed_payload = f"{string}-{signature}"
    
    string_bytes = signed_payload.encode("ascii")
    base64_bytes = base64.urlsafe_b64encode(string_bytes)
    base64_string = (base64_bytes.decode("ascii")).strip("=")
    return base64_string

async def decode(base64_string):
    """Decodes the string, verifies the signature, and returns the payload if valid."""
    base64_string = base64_string.strip("=") 
    base64_bytes = (base64_string + "=" * (-len(base64_string) % 4)).encode("ascii")
    
    try:
        string_bytes = base64.urlsafe_b64decode(base64_bytes) 
        decoded_string = string_bytes.decode("ascii")
    except Exception:
        return None # Invalid Base64 format
        
    # Split the payload from the signature (splitting from the right)
    parts = decoded_string.rsplit('-', 1)
    
    if len(parts) != 2:
        return None # Format is wrong (likely an old, unsigned link or tampered link)
        
    payload, provided_signature = parts
    
    # Recalculate what the signature SHOULD be
    expected_signature = generate_signature(payload)
    
    # Check if they match perfectly
    if hmac.compare_digest(expected_signature, provided_signature):
        return payload
    else:
        return None # Signature mismatch - TAMPERING DETECTED!


async def get_messages(client, message_ids):
    messages = []
    total_messages = 0
    while total_messages != len(message_ids):
        temb_ids = message_ids[total_messages:total_messages+200]
        try:
            msgs = await client.get_messages(
                chat_id=client.db_channel.id,
                message_ids=temb_ids
            )
        except FloodWait as e:
            await asyncio.sleep(e.x)
            msgs = await client.get_messages(
                chat_id=client.db_channel.id,
                message_ids=temb_ids
            )
        except:
            pass
        total_messages += len(temb_ids)
        messages.extend(msgs)
    return messages

async def get_message_id(client, message):
    if message.forward_from_chat:
        if message.forward_from_chat.id == client.db_channel.id:
            return message.forward_from_message_id
        else:
            return 0
    elif message.forward_sender_name:
        return 0
    elif message.text:
        pattern = "https://t.me/(?:c/)?(.*)/(\d+)"
        matches = re.match(pattern,message.text)
        if not matches:
            return 0
        channel_id = matches.group(1)
        msg_id = int(matches.group(2))
        if channel_id.isdigit():
            if f"-100{channel_id}" == str(client.db_channel.id):
                return msg_id
        else:
            if channel_id == client.db_channel.username:
                return msg_id
    else:
        return 0

def get_readable_time(seconds: int) -> str:
    count = 0
    up_time = ""
    time_list = []
    time_suffix_list = ["s", "m", "h", "days"]
    while count < 4:
        count += 1
        remainder, result = divmod(seconds, 60) if count < 3 else divmod(seconds, 24)
        if seconds == 0 and remainder == 0:
            break
        time_list.append(int(result))
        seconds = int(remainder)
    hmm = len(time_list)
    for x in range(hmm):
        time_list[x] = str(time_list[x]) + time_suffix_list[x]
    if len(time_list) == 4:
        up_time += f"{time_list.pop()}, "
    time_list.reverse()
    up_time += ":".join(time_list)
    return up_time

async def delete_file(messages, client, process):
    await asyncio.sleep(AUTO_DELETE_TIME)
    for msg in messages:
        try:
            await client.delete_messages(chat_id=msg.chat.id, message_ids=[msg.id])
        except Exception as e:
            print(f"The attempt to delete the media {msg.id} was unsuccessful: {e}")

    await process.edit_text(AUTO_DEL_SUCCESS_MSG)


def extract_code_from_link(text: str) -> str:
    text = text.strip()
    if "start=" in text:
        text = text.split("start=", 1)[1]
    return text.split("&")[0].strip()

async def revoke_link(code: str):
    await _revoked_links_col.update_one(
        {"code": code},
        {"$set": {"code": code}},
        upsert=True
    )

async def unrevoke_link(code: str) -> bool:
    result = await _revoked_links_col.delete_one({"code": code})
    return result.deleted_count > 0

async def is_link_revoked(code: str) -> bool:
    doc = await _revoked_links_col.find_one({"code": code})
    return doc is not None

subscribed = filters.create(is_subscribed)
