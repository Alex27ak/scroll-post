from contextlib import suppress
from urllib.parse import quote_plus
from pyrogram import Client, filters
from pyrogram.types import Message, Video, InlineKeyboardMarkup, InlineKeyboardButton
from bot.config import Config
from bot.utils.helpers import get_hash, get_name, is_admin
from database import db
from pyrogram.errors import FloodWait
import asyncio


@Client.on_message(filters.command("index") & filters.private & filters.incoming)
@is_admin
async def index_command(c: Client, m: Message):
    if len(m.command) == 1:
        text = "/index channel_id"
        await m.reply_text(text)
        return

    channel_id = m.command[1]

    try:
        channel_id = int(channel_id)
    except ValueError:
        await m.reply_text("Invalid channel id")
        return

    try:
        channel = await c.get_chat(channel_id)
    except Exception as e:
        await m.reply_text(
            f"Make sure you have added the bot to the channel and the channel id is correct.\n\nError: {e}"
        )
        return

    try:
        test_message = await c.send_message(channel_id, ".")
        await test_message.delete()
        last_message_id = test_message.id
    except Exception as e:
        await m.reply_text(f"Error: {e}")
        return

    out = await m.reply_text(f"Indexing started for {channel.title}")
    total_messages = range(1, last_message_id)
    counter = 0
    for i in range(0, len(total_messages), 200):
        channel_posts = await floodwait_handler(
            c.get_messages, channel_id, total_messages[i : i + 200]
        )
        for post in channel_posts:
            counter += 1
            post: Message
            if post.video or post.document:
                file = post.video or post.document
                thumbnail = None

                if len(file.thumbs) > 0:
                    thumbnail = file.thumbs[0].file_id

                name = file.file_name
                caption = post.caption.html if post.caption else ""
                duration = file.duration if isinstance(file, Video) else 0.00
                file_id = file.file_id
                log_msg = await floodwait_handler(
                    post.copy,
                    chat_id=Config.LOG_CHANNEL,
                    caption=caption,
                    reply_markup=InlineKeyboardMarkup(
                        [[InlineKeyboardButton("Delete", "delete")]]
                    ),
                )
                stream_link = f"{Config.URL}watch/{str(log_msg.id)}/{quote_plus(get_name(log_msg))}?hash={get_hash(log_msg)}"
                await db.files.create_file(
                    file_id,
                    name,
                    duration,
                    caption,
                    stream_link,
                    log_msg.id,
                    log_msg.chat.id,
                    thumbnail,
                )
                with suppress(Exception):
                    await out.edit(f"Indexed {counter} messages")

    await out.edit_text(f"Indexing completed for {channel.title}")
    return


async def floodwait_handler(func, *args, **kwargs):
    try:
        return await func(*args, **kwargs)
    except FloodWait as e:
        await asyncio.sleep(e.value)
        return await floodwait_handler(func, *args, **kwargs)
