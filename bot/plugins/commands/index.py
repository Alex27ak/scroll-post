from contextlib import suppress
from urllib.parse import quote_plus
from pyrogram import Client, filters
from pyrogram.types import (
    Message,
    Video,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    Document,
)
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
            post: Message
            if post.video or post.document:
                file = post.video or post.document
                thumbnail = None

                if file.thumbs and len(file.thumbs) > 0:
                    thumbnail = file.thumbs[0].file_id

                if (
                    isinstance(file, Document)
                    and file.mime_type.split("/")[0] != "video"
                ):
                    continue

                name = file.file_name
                caption = post.caption.html if post.caption else ""
                duration = file.duration if isinstance(file, Video) else 0.00
                file_id = file.file_id
                file_unique_id = file.file_unique_id

                if await db.files.exists(file_unique_id):
                    continue
                
                log_msg = await floodwait_handler(
                    post.copy,
                    chat_id=Config.LOG_CHANNEL,
                    caption=caption,
                    reply_markup=InlineKeyboardMarkup(
                        [[InlineKeyboardButton("Delete", "delete")]]
                    ),
                )
                stream_link = f"watch/{str(log_msg.id)}/{quote_plus(get_name(log_msg))}?hash={get_hash(log_msg)}"
                await db.files.create_file(
                    file_id,
                    file_unique_id,
                    name,
                    duration,
                    caption,
                    stream_link,
                    log_msg.id,
                    log_msg.chat.id,
                    thumbnail,
                )
                counter += 1
                with suppress(Exception):
                    await out.edit(f"Indexed {counter} messages")

    await out.edit_text(f"Indexing completed for {channel.title} with {counter} messages")
    return


async def floodwait_handler(func, *args, **kwargs):
    try:
        return await func(*args, **kwargs)
    except FloodWait as e:
        await asyncio.sleep(e.value)
        return await floodwait_handler(func, *args, **kwargs)
