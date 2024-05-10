import asyncio
from pyrogram import Client, filters
from pyrogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputMediaPhoto,
)
from bot.config import Config
from database import db
from pyrogram.errors import FloodWait


@Client.on_message(filters.command("brazzers") & filters.private & filters.incoming)
@Client.on_callback_query(filters.regex("files"))
async def files(bot: Client, message: Message | CallbackQuery):
    # if message is instance of Message, then page and video number is one, else grab the page number and video number and show it accordingly
    files = await db.files.get_all_files()
    FILES_PER_PAGE = 10
    if isinstance(message, Message):
        page_number = 1
        video_number = 1
    else:
        data = message.data.split("_")
        page_number = int(data[1])
        video_number = int(data[2])

    files = await db.files.get_all_files()

    # Calculate the index of the current video based on page_number and video_number
    index = video_number - 1

    if index < len(files):
        file_info = files[index]
        text = f"Current Video : {video_number} / {len(files)}\n"
        text += f"Current Page : {page_number}\n\n"
        text += f"Name : {file_info['file_name']}\n"
        text += f"Duration : {file_info['duration']}\n"
        text = f"**{text}**"
        # Assuming stream_link is the URL for online play
        stream_link = f"{Config.URL}{file_info['stream_link']}"
        buttons = []
        buttons.append([InlineKeyboardButton("Online Play", url=stream_link)])

        # Add navigation buttons
        video_buttons = []
        page_buttons = []
        if video_number > 1:
            # calculate the page number if the video is the first video in the current page

            if video_number % FILES_PER_PAGE == 1:
                previous_page_number = page_number - 1
                previous_page_first_video = video_number - 1
            else:
                previous_page_first_video = video_number - 1
                previous_page_number = page_number

            video_buttons.append(
                InlineKeyboardButton(
                    "Previous Video",
                    callback_data=f"files_{previous_page_number}_{previous_page_first_video}",
                )
            )

        if video_number < len(files):
            # calculate the next page number
            if video_number % FILES_PER_PAGE == 0:
                next_page_number = page_number + 1
                next_page_first_video = video_number + 1
            else:
                next_page_first_video = video_number + 1
                next_page_number = page_number
            video_buttons.append(
                InlineKeyboardButton(
                    "Next Video",
                    callback_data=f"files_{next_page_number}_{next_page_first_video}",
                )
            )

        buttons.append(video_buttons)
        if page_number > 1:
            # calculate the first video number in the previous page
            previous_page_first_video = (page_number - 2) * FILES_PER_PAGE + 1
            page_buttons.append(
                InlineKeyboardButton(
                    "Previous Page",
                    callback_data=f"files_{page_number - 1}_{previous_page_first_video}",
                )
            )

        if page_number < len(files) // FILES_PER_PAGE + 1:
            # calculate the first video number in the next page
            next_page_first_video = (page_number + 1) * FILES_PER_PAGE - 1
            page_buttons.append(
                InlineKeyboardButton(
                    "Next Page",
                    callback_data=f"files_{page_number + 1}_{next_page_first_video}",
                )
            )
        buttons.append(page_buttons)
        # Add a home button
        buttons.append([InlineKeyboardButton("Home", callback_data="files_1_1")])

        reply_markup = InlineKeyboardMarkup(buttons)

        func = (
            message.edit_message_text
            if isinstance(message, CallbackQuery)
            else message.reply
        )
        await floodwait_handler(func, text, reply_markup=reply_markup)

    else:
        func = message.answer if isinstance(message, CallbackQuery) else message.reply
        await func("No more videos available")


async def floodwait_handler(func, *args, **kwargs):
    try:
        await func(*args, **kwargs)
    except FloodWait as e:
        await asyncio.sleep(e.value)
        await floodwait_handler(func, *args, **kwargs)
