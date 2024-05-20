from pyrogram import Client, filters, types
from database import db
from bot.config import Config


@Client.on_message(
    filters.command("remove_all")
    & filters.private
    & filters.incoming
    & filters.user(Config.OWNER_ID)
)
async def remove_all(bot, message):
    return await message.reply_text(
        "Are you sure you want to remove all files?",
        reply_markup=types.InlineKeyboardMarkup(
            [
                [
                    types.InlineKeyboardButton("Yes", callback_data="remove_all_yes"),
                    types.InlineKeyboardButton("No", callback_data="remove_all_no"),
                ]
            ]
        ),
    )


@Client.on_callback_query(filters.regex("remove_all_yes"))
async def remove_all_yes(bot, callback_query):
    await db.files.col.delete_many({})
    await callback_query.message.edit_text("All files removed.")


@Client.on_callback_query(filters.regex("remove_all_no"))
async def remove_all_no(bot, callback_query):
    await callback_query.message.edit_text("Cancelled.")
