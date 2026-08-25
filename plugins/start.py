@Bot.on_message(filters.command('start') & filters.private & subscribed)
async def start_command(client: Client, message: Message):
    id = message.from_user.id
    if not await present_user(id):
        try:
            await add_user(id)
        except:
            pass
    text = message.text
    if len(text)>7:
        try:
            base64_string = text.split(" ", 1)[1]
        except:
            return

        if await is_link_revoked(base64_string):
            await message.reply_text(
                "❌ <b>This link has been revoked</b> and can no longer be used to access files.",
                quote=True
            )
            return

        # ---- SECURITY CHECK ----
        string = await decode(base64_string)
        
        # If decode returns None, the signature failed (link was tampered with or is invalid)
        if string is None:
            await message.reply_text(
                "❌ <b>Invalid or tampered link.</b>\n\nFor security reasons, this request has been denied.",
                quote=True
            )
            return

        argument = string.split("-")

        # PREMIUM LINK CHECK
        if argument[0] == "premium":
            if not await is_premium_subscribed(client, id):
                buttons = [
                    [InlineKeyboardButton("🔒 Join Premium", url=PREMIUM_JOIN_LINK)],
                    [InlineKeyboardButton("🔄 Try Again", url=f"https://t.me/{client.username}?start={base64_string}")]
                ]
                await message.reply_text(
                    text=PREMIUM_MSG.format(
                        first=message.from_user.first_name,
                        last=message.from_user.last_name,
                        username=None if not message.from_user.username else '@' + message.from_user.username,
                        mention=message.from_user.mention,
                        id=message.from_user.id
                    ),
                    reply_markup=InlineKeyboardMarkup(buttons),
                    quote=True,
                    disable_web_page_preview=True
                )
                return

        if len(argument) == 3:
            try:
                start = int(int(argument[1]) / abs(client.db_channel.id))
                end = int(int(argument[2]) / abs(client.db_channel.id))
            except:
                return
            if start <= end:
                ids = range(start,end+1)
            else:
                ids = []
                i = start
                while True:
                    ids.append(i)
                    i -= 1
                    if i < end:
                        break
        elif len(argument) == 2:
            try:
                ids = [int(int(argument[1]) / abs(client.db_channel.id))]
            except:
                return
        temp_msg = await message.reply("Please wait...")
        try:
            messages = await get_messages(client, ids)
        except:
            await message.reply_text("Something went wrong..!")
            return
        await temp_msg.delete()

        track_msgs = []

        for msg in messages:

            if bool(CUSTOM_CAPTION) & bool(msg.document):
                caption = CUSTOM_CAPTION.format(previouscaption = "" if not msg.caption else msg.caption.html, filename = msg.document.file_name)
            else:
                caption = "" if not msg.caption else msg.caption.html

            if DISABLE_CHANNEL_BUTTON:
                reply_markup = msg.reply_markup
            else:
                reply_markup = None

            if AUTO_DELETE_TIME and AUTO_DELETE_TIME > 0:

                try:
                    copied_msg_for_deletion = await msg.copy(chat_id=message.from_user.id, caption=caption, parse_mode=ParseMode.HTML, reply_markup=reply_markup, protect_content=PROTECT_CONTENT)
                    if copied_msg_for_deletion:
                        track_msgs.append(copied_msg_for_deletion)
                    else:
                        print("Failed to copy message, skipping.")

                except FloodWait as e:
                    await asyncio.sleep(e.value)
                    copied_msg_for_deletion = await msg.copy(chat_id=message.from_user.id, caption=caption, parse_mode=ParseMode.HTML, reply_markup=reply_markup, protect_content=PROTECT_CONTENT)
                    if copied_msg_for_deletion:
                        track_msgs.append(copied_msg_for_deletion)
                    else:
                        print("Failed to copy message after retry, skipping.")

                except Exception as e:
                    print(f"Error copying message: {e}")
                    pass

            else:
                try:
                    await msg.copy(chat_id=message.from_user.id, caption=caption, parse_mode=ParseMode.HTML, reply_markup=reply_markup, protect_content=PROTECT_CONTENT)
                    await asyncio.sleep(0.5)
                except FloodWait as e:
                    await asyncio.sleep(e.value)
                    await msg.copy(chat_id=message.from_user.id, caption=caption, parse_mode=ParseMode.HTML, reply_markup=reply_markup, protect_content=PROTECT_CONTENT)
                except:
                    pass

        if track_msgs:
            delete_data = await client.send_message(
                chat_id=message.from_user.id,
                text=AUTO_DELETE_MSG.format(time=AUTO_DELETE_TIME)
            )
            # Schedule the file deletion task after all messages have been copied
            asyncio.create_task(delete_file(track_msgs, client, delete_data))
        else:
            print("No messages to track for deletion.")

        return
    else:
        reply_markup = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("😊 About Me", callback_data = "about"),
                    InlineKeyboardButton("🔒 Close", callback_data = "close")
                ]
            ]
        )
        if START_PIC: 
            await message.reply_photo(
                photo=START_PIC,
                caption=START_MSG.format(
                    first=message.from_user.first_name,
                    last=message.from_user.last_name,
                    username=None if not message.from_user.username else '@' + message.from_user.username,
                    mention=message.from_user.mention,
                    id=message.from_user.id
                ),
                reply_markup=reply_markup,
                quote=True
            )
        else: 
            await message.reply_text(
                text=START_MSG.format(
                    first=message.from_user.first_name,
                    last=message.from_user.last_name,
                    username=None if not message.from_user.username else '@' + message.from_user.username,
                    mention=message.from_user.mention,
                    id=message.from_user.id
                ),
                reply_markup=reply_markup,
                disable_web_page_preview=True,
                quote=True
            )
        return
