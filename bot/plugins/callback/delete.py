from pyrogram import Client, filters
from pyrogram.types import CallbackQuery
from database import db


@Client.on_callback_query(filters.regex("delete"))
async def delete(c: Client, q: CallbackQuery):
    message_id = q.message.id
    chat_id = q.message.chat.id
    await c.delete_messages(chat_id, message_id)
    await db.files.delete_file_by_message_id(message_id, chat_id)
