# import asyncio
# import requests
# import aioschedule
# from aiogram import Bot, types, Dispatcher
# from config import config
# from tgbot.utiles import database
# import time
#
# bot = Bot(token=config.BOT_TOKEN.get_secret_value())
# dp = Dispatcher(bot)
#
# chat_id = "1093031870"
# text = "Выберите смайлик на сегодня"
# need_time = "17:30"
# needTime = str(int(time.mktime(time.strptime('2023-07-21 18:10:00', '%Y-%m-%d %H:%M:%S'))))
# # needTime = '1689766500'
#
#
# async def createNot():
#     res = requests.post(
#                 f'https://api.telegram.org/bot<TOKEN>/sendmessage?chat_id={chat_id}&text={text}&schedule_date={needTime}')
#     print(res)
#     print(needTime)
#
#
# """ Уведомление """
# @dp.message_handler()
# async def reminder(message: types.Message):
#     allUsers = await database.getAllUser()
#     async for user in allUsers:
#         await bot.send_message(chat_id=await database.getInfo(user.id, "chat_id"),
#                                text="Выбери смайл!",
#                                reply_markup=show_button(smileys))
# async def scheduler():
#     allUsers = await database.getAllUser()
#     async for user in allUsers:
#         aioschedule.every().day.at(await database.getInfo(user.id, "notification")).do(reminder)
#         while True:
#             await aioschedule.run_pending()
#             await asyncio.sleep(1)
#
# async def on_startup(dp):
#     asyncio.create_task(scheduler())
