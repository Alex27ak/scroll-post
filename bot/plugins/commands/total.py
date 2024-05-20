from pyrogram import Client, filters, types
from database import db
from bot.config import Config


@Client.on_message(
    filters.command("total")
    & filters.private
    & filters.incoming
    & filters.user(Config.OWNER_ID)
)
async def total(bot, message):
    total_files = await db.files.get_total_files()
    return await message.reply_text(f"Total files: {total_files}")