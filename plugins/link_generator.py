#(©)Codexbotz

from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ChatMemberStatus
from bot import Bot
from config import ADMINS, PREMIUM_CHANNEL
from helper_func import encode, get_message_id, revoke_link, unrevoke_link, extract_code_from_link, get_premium_channel, set_premium_channel

@Bot.on_message(filters.private & filters.user(ADMINS) & filters.command('batch'))
async def batch(client: Client, message: Message):
    while True:
        try:
            first_message = await client.ask(text = "Forward the First Message from DB Channel (with Quotes)..\n\nor Send the DB Channel Post Link", chat_id = message.from_user.id, filters=(filters.forwarded | (filters.text & ~filters.forwarded)), timeout=60)
        except:
            return
        f_msg_id = await get_message_id(client, first_message)
        if f_msg_id:
            break
        else:
            await first_message.reply("❌ Error\n\nthis Forwarded Post is not from my DB Channel or this Link is taken from DB Channel", quote = True)
            continue

    while True:
        try:
            second_message = await client.ask(text = "Forward the Last Message from DB Channel (with Quotes)..\nor Send the DB Channel Post link", chat_id = message.from_user.id, filters=(filters.forwarded | (filters.text & ~filters.forwarded)), timeout=60)
        except:
            return
        s_msg_id = await get_message_id(client, second_message)
        if s_msg_id:
            break
        else:
            await second_message.reply("❌ Error\n\nthis Forwarded Post is not from my DB Channel or this Link is taken from DB Channel", quote = True)
            continue

    # REMOVED MULTIPLICATION OBFUSCATION
    string = f"get-{f_msg_id}-{s_msg_id}"
    base64_string = await encode(string)
    link = f"https://t.me/{client.username}?start={base64_string}"
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("🔁 Share URL", url=f'https://telegram.me/share/url?url={link}')]])
    await second_message.reply_text(f"<b>Here is your link</b>\n\n{link}", quote=True, reply_markup=reply_markup)


@Bot.on_message(filters.private & filters.user(ADMINS) & filters.command('genlink'))
async def link_generator(client: Client, message: Message):
    while True:
        try:
            channel_message = await client.ask(text = "Forward Message from the DB Channel (with Quotes)..\nor Send the DB Channel Post link", chat_id = message.from_user.id, filters=(filters.forwarded | (filters.text & ~filters.forwarded)), timeout=60)
        except:
            return
        msg_id = await get_message_id(client, channel_message)
        if msg_id:
            break
        else:
            await channel_message.reply("❌ Error\n\nthis Forwarded Post is not from my DB Channel or this Link is not taken from DB Channel", quote = True)
            continue

    # REMOVED MULTIPLICATION OBFUSCATION
    base64_string = await encode(f"get-{msg_id}")
    link = f"https://t.me/{client.username}?start={base64_string}"
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("🔁 Share URL", url=f'https://telegram.me/share/url?url={link}')]])
    await channel_message.reply_text(f"<b>Here is your link</b>\n\n{link}", quote=True, reply_markup=reply_markup)


@Bot.on_message(filters.private & filters.user(ADMINS) & filters.command('premiumbatch'))
async def premium_batch(client: Client, message: Message):
    while True:
        try:
            first_message = await client.ask(text = "Forward the First Message from DB Channel (with Quotes) for this PREMIUM set..\n\nor Send the DB Channel Post Link", chat_id = message.from_user.id, filters=(filters.forwarded | (filters.text & ~filters.forwarded)), timeout=60)
        except:
            return
        f_msg_id = await get_message_id(client, first_message)
        if f_msg_id:
            break
        else:
            await first_message.reply("❌ Error\n\nthis Forwarded Post is not from my DB Channel or this Link is taken from DB Channel", quote = True)
            continue

    while True:
        try:
            second_message = await client.ask(text = "Forward the Last Message from DB Channel (with Quotes)..\nor Send the DB Channel Post link", chat_id = message.from_user.id, filters=(filters.forwarded | (filters.text & ~filters.forwarded)), timeout=60)
        except:
            return
        s_msg_id = await get_message_id(client, second_message)
        if s_msg_id:
            break
        else:
            await second_message.reply("❌ Error\n\nthis Forwarded Post is not from my DB Channel or this Link is taken from DB Channel", quote = True)
            continue

    # REMOVED MULTIPLICATION OBFUSCATION
    string = f"premium-{f_msg_id}-{s_msg_id}"
    base64_string = await encode(string)
    link = f"https://t.me/{client.username}?start={base64_string}"
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("🔁 Share URL", url=f'https://telegram.me/share/url?url={link}')]])
    await second_message.reply_text(f"<b>🔒 Here is your PREMIUM link</b>\n\n{link}\n\nAnyone opening this who isn't in the premium group will be denied and asked to join.", quote=True, reply_markup=reply_markup)


@Bot.on_message(filters.private & filters.user(ADMINS) & filters.command('premiumgenlink'))
async def premium_link_generator(client: Client, message: Message):
    while True:
        try:
            channel_message = await client.ask(text = "Forward Message from the DB Channel (with Quotes) for this PREMIUM file..\nor Send the DB Channel Post link", chat_id = message.from_user.id, filters=(filters.forwarded | (filters.text & ~filters.forwarded)), timeout=60)
        except:
            return
        msg_id = await get_message_id(client, channel_message)
        if msg_id:
            break
        else:
            await channel_message.reply("❌ Error\n\nthis Forwarded Post is not from my DB Channel or this Link is not taken from DB Channel", quote = True)
            continue

    # REMOVED MULTIPLICATION OBFUSCATION
    base64_string = await encode(f"premium-{msg_id}")
    link = f"https://t.me/{client.username}?start={base64_string}"
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("🔁 Share URL", url=f'https://telegram.me/share/url?url={link}')]])
    await channel_message.reply_text(f"<b>🔒 Here is your PREMIUM link</b>\n\n{link}\n\nAnyone opening this who isn't in the premium group will be denied and asked to join.", quote=True, reply_markup=reply_markup)


@Bot.on_message(filters.private & filters.user(ADMINS) & filters.command('revoke'))
async def revoke_command(client: Client, message: Message):
    if len(message.command) < 2:
        await message.reply_text(
            "<b>Usage:</b> <code>/revoke <link_or_code></code>\n\nSend the full share link, or just the code after <code>?start=</code>.",
            quote=True
        )
        return
    arg = message.text.split(None, 1)[1]
    code = extract_code_from_link(arg)
    await revoke_link(code)
    await message.reply_text(
        f"🔒 <b>Link revoked.</b> It can no longer be used to access files.\n\nCode: <code>{code}</code>",
        quote=True
    )

@Bot.on_message(filters.private & filters.user(ADMINS) & filters.command('unrevoke'))
async def unrevoke_command(client: Client, message: Message):
    if len(message.command) < 2:
        await message.reply_text(
            "<b>Usage:</b> <code>/unrevoke <link_or_code></code>\n\nSend the full share link, or just the code after <code>?start=</code>.",
            quote=True
        )
        return
    arg = message.text.split(None, 1)[1]
    code = extract_code_from_link(arg)
    was_revoked = await unrevoke_link(code)
    if was_revoked:
        await message.reply_text(f"✅ <b>Link restored.</b>\n\nCode: <code>{code}</code>", quote=True)
    else:
        await message.reply_text("That code wasn't revoked.", quote=True)


@Bot.on_message(filters.private & filters.user(ADMINS) & filters.command('connectpremium'))
async def connect_premium(client: Client, message: Message):
    try:
        fwd = await client.ask(
            text="Forward any message from your Premium channel/group (with Quotes)..\n\nMake sure the bot has already been added there as admin.",
            chat_id=message.from_user.id,
            filters=filters.forwarded,
            timeout=60
        )
    except:
        return

    if not fwd.forward_from_chat:
        await message.reply_text(
            "❌ That wasn't a forwarded channel/group message (or the sender chose to hide it). Run /connectpremium again.",
            quote=True
        )
        return

    chat = fwd.forward_from_chat
    try:
        member = await client.get_chat_member(chat.id, "me")
    except Exception as e:
        await message.reply_text(
            f"❌ I couldn't check my membership there: <code>{e}</code>\n\nMake sure the bot has been added to that channel/group as admin first, then run /connectpremium again.",
            quote=True
        )
        return

    if member.status not in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR]:
        await message.reply_text(
            "❌ I'm in that chat, but not as admin. Promote the bot to admin there, then run /connectpremium again.",
            quote=True
        )
        return

    await set_premium_channel(chat.id, chat.title or str(chat.id))
    await message.reply_text(
        f"✅ <b>Premium channel connected.</b>\n\nName: {chat.title or 'N/A'}\nID: <code>{chat.id}</code>\n\nPremium-tagged links will now check membership here.",
        quote=True
    )

@Bot.on_message(filters.private & filters.user(ADMINS) & filters.command('premiumstatus'))
async def premium_status(client: Client, message: Message):
    chat_id = await get_premium_channel()
    if not chat_id:
        await message.reply_text(
            f"No premium channel connected yet — run /connectpremium.\n\n"
            f"(Currently falling back to the PREMIUM_CHANNEL env var: <code>{PREMIUM_CHANNEL or 'not set'}</code>)",
            quote=True
        )
        return
    try:
        chat = await client.get_chat(chat_id)
        title = chat.title or "N/A"
    except Exception:
        title = "N/A (couldn't fetch chat info)"
    await message.reply_text(
        f"🔒 <b>Connected premium channel</b>\n\nName: {title}\nID: <code>{chat_id}</code>",
        quote=True
    )
