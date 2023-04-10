import logging
from aiogram import Bot, Dispatcher, executor
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.callback_data import CallbackData
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import pandas as pd

bot = Bot(token = '6014300125:AAFUHECvJdPDux5EXMJnXYMELD7ZCXEuryY', proxy = "http://proxy.server:3128")  # создаю бота и указываю его токен
logging.basicConfig(level=logging.INFO)  # включаю логирование, чтоб не упустить ошибки
storage = MemoryStorage() # Инициализируем диспетчер сообщений
dp = Dispatcher(bot, storage = storage) # считыватель переписки с ботом (диспетчер)
Callback = CallbackData('filter', 'option', 'action')
df = pd.read_csv('dividends.csv')
secid = df['secid'].values
df['year'] = pd.DatetimeIndex(df['registryclosedate']).year
year = df['year'].values

def df_to_str(df):
    values = df['value'].unique()
    result = ''
    for value in values:
        result += str(value) + '\n'
    return result

@dp.callback_query_handler(Callback.filter()) # Обработка кнопки, создание фильтров
async def mood_button(call, callback_data):
    match callback_data['action']:
        case 'mood':
            global mood
            mood = callback_data['option']
            if mood == 'Хорошо':
                await call.message.answer('Человечество любит деньги, из чего бы те ни были сделаны.')
                await bot.send_sticker(call.message.chat.id, 'CAACAgIAAxkBAAEIhFZkMnwoB3-MBEuxseTtOIzpGO0qKwACryYAAoOUQUgRFXcT7or2wi8E')
            elif mood == 'Плохо':
                await call.message.answer('Понимаю, был тяжелый день. Деньги не приносят счастья, но очень помогают без него обойтись.')
                await bot.send_sticker(call.message.chat.id, 'CAACAgIAAxkBAAEIhFhkMnxnXYgZJHlkglUszdr1-kvX-QAC5ikAAhjISEhlQgwTt6uq9y8E')
            else:
                await call.message.answer('Я знаю, нельзя иметь всего сразу, поэтому я начну с малого — с денег.')
                await bot.send_sticker(call.message.chat.id, 'CAACAgIAAxkBAAEIhFpkMnx4hTf0uONfWsmzN4GG4_EdiAAC9iMAApiFQUi9FydLExHDDS8E')
        case 'secid':
            global secid
            secid = callback_data['option']
            await call.message.answer('Ты выбрал - ' + str(callback_data['option']))
        case 'year':
            global year
            year = callback_data['option']
            await call.message.answer('Ты выбрал - ' + str(callback_data['option']))

@dp.message_handler(commands=['start', 'help'])                    # Главное меню с информацией
async def print_hi(message):
    await message.answer('Рад приветствовать тебя, мой друг!\n'
                         'Как дела?\n'
                         'Я чат-помощник для инвестора, который поможет получить данные о дивидендах по финансовым активам с Московской биржи.\n'
                         'Для этого введи команды /secid и /year \n'
                         'Когда определишься с компанией и годом введи команду /show')
    keyboard_of_mood = InlineKeyboardMarkup() # Объявление клавиатуры
    buttons = [InlineKeyboardButton(text = 'Хорошо :)', callback_data=Callback.new(option='Хорошо', action='mood')),  # Создание кнопок в массиве
               InlineKeyboardButton(text = 'Плохо :(', callback_data=Callback.new(option='Плохо', action='mood')),
               InlineKeyboardButton(text = 'По-разному...', callback_data=Callback.new(option='По-разному...', action='mood'))]

    keyboard_of_mood.add(*buttons)
    await message.answer("Выбери вариант: ", reply_markup=keyboard_of_mood)

@dp.message_handler(commands ='secid')                    # Обработка команды /secid
async def set_state_secid(message):
    await message.answer('Я могу рассказать о дивидендах одной из компаний: Газпром(GAZP), МТС(MTSS) и Сбербанк(SBER). Напиши сокращенное название одной компании.')
    keyboard_of_secid = InlineKeyboardMarkup() # Объявление клавиатуры
    buttons = [InlineKeyboardButton(text = 'Газпром', callback_data=Callback.new(option='GAZP', action='secid')),  # Создание кнопок в массиве
               InlineKeyboardButton(text = 'МТС', callback_data=Callback.new(option='MTSS', action='secid')),
               InlineKeyboardButton(text = 'Сбербанк', callback_data=Callback.new(option='SBER', action='secid'))]

    keyboard_of_secid.add(*buttons)
    await message.answer("Выбери вариант: ", reply_markup=keyboard_of_secid)

@dp.message_handler(commands ='year')                    # Обработка команды /year
async def set_state_year(message):
    await message.answer('Дивиденды в каком году тебя интересуют?')
    keyboard_of_year = InlineKeyboardMarkup() # Объявление клавиатуры
    buttons = [InlineKeyboardButton(text = '2019', callback_data=Callback.new(option='2019', action='year')),  # Создание кнопок в массиве
               InlineKeyboardButton(text = '2020', callback_data=Callback.new(option='2020', action='year')),
               InlineKeyboardButton(text = '2021', callback_data=Callback.new(option='2021', action='year')),
               InlineKeyboardButton(text = '2022', callback_data=Callback.new(option='2022', action='year'))]

    keyboard_of_year.add(*buttons)
    await message.answer("Выбери вариант: ", reply_markup=keyboard_of_year)

@dp.message_handler(commands = 'show')
async def show(message):
    filtred_df = df[(df['secid']==secid)&(df['year']==int(year))]

    await message.answer(df_to_str(filtred_df))

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)                  # Запускает проверку сообщений в диалоге (запускает бота)