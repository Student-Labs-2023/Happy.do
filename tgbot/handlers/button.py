# from aiogram import types
# from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
# from aiogram import Dispatcher
# from bot import dp, bot
#
# smileys = [
#     '😀', '😃', '😄', '😁', '😆', '😅',
#     '🙂', '😂', '🤣', '😊', '😇', '🙃',
#     '😉', '😌', '😘', '😍', '😗', '😙',
#     '😚', '😋', '😛', '😜', '😝', '🤪',
#     '🤨', '🤢', '🤮', '🤧', '🥱', '🥶',
#     '😤', '😱', '😓', '😡', '🥵', '🤬',
# ]
#
#
# def show_button(list_emogi):
#     keyboard = InlineKeyboardMarkup(row_width=6)
#     buttons = [InlineKeyboardButton(smiley, callback_data=smiley) for smiley in list_emogi]
#     keyboard.add(*buttons)
#     return keyboard
#
#
# def add_checkmark(lst, variable):
#     return [elem + "✅" if elem == variable else elem for elem in lst]
#
#
# @dp.message_handler(commands=['emoji'])
# async def show_emogi(message: types.Message):
#     await message.reply('Выберите смайлик:', reply_markup=show_button(smileys))
#
#
# @dp.callback_query_handler()
# async def button(callback_query: types.CallbackQuery):
#     query = callback_query
#     await query.answer()
#     new_emoji_list = add_checkmark(smileys, query.data)
#     await bot.answer_callback_query(callback_query.id)
#     await query.message.edit_text('выбранный смайлик ✅', reply_markup=show_button(new_emoji_list))
#
#     print(f'выбранный смайлик {query.data}')
#
#
