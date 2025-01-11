import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.filters import Command
from aiogram import F
import asyncio
from pymongo import MongoClient
from datetime import datetime, timedelta
import logging
import json
from aiohttp import web

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Токен вашего бота
API_TOKEN = "7643886458:AAGr6E4H3HlkkU7jSZncXUGP8e_t-O04RNc"

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# URI для подключения к MongoDB
uri = "mongodb+srv://mvstarcorp:UFnERtzkd9fwvqzm@cluster0.ihw7m.mongodb.net/?retryWrites=true&w=majority&tlsAllowInvalidCertificates=True"
client = MongoClient(uri)
database = client.get_database("Yoga_bot")
basic_collection = database.get_collection("basic_clstr")
subs_collection = database.get_collection("subs_clstr")

# Ссылки на изображения
IMAGES = {
    "main": "https://i.imgur.com/q7Fgkhh.jpg",
    "group_practice": "https://i.imgur.com/5WWAIIc.jpg",
    "individual_practice": "https://i.imgur.com/EAXcUvg.jpg",
    "trial_practice": "https://i.imgur.com/ls7d2Ua.jpg",
    "results": "https://i.imgur.com/Rd4o7X4.jpg",
    "feedback": "https://i.imgur.com/HuPLLJ2.jpg",
    "tariff": "https://i.imgur.com/1PU75Nz.jpg",
}

# Дополнительные фотографии для результатов и отзывов
ADDITIONAL_PHOTOS = [
    "https://i.imgur.com/Gx6JnPF.jpg",
    "https://i.imgur.com/yTU7d3w.jpg",
    "https://i.imgur.com/kTfWNM3.jpg",
    "https://i.imgur.com/9kQ7axR.jpg",
    "https://i.imgur.com/JrYfCgH.jpg"
]

# Меню для результатов и отзывов
def results_menu_markup():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="НАЗАД", callback_data="main_menu")],
        [InlineKeyboardButton(text="ГЛАВНОЕ МЕНЮ", callback_data="main_menu")]
    ])

# Главное меню
def main_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="ГРУППОВЫЕ ПРАКТИКИ", callback_data="group_practice")],
        [InlineKeyboardButton(text="ИНДИВИДУАЛЬНЫЕ ПРАКТИКИ", callback_data="individual_practice")],
        [InlineKeyboardButton(text="ПРОБНАЯ ПРАКТИКА", callback_data="trial_practice")],
        [InlineKeyboardButton(text="РЕЗУЛЬТАТЫ И ОТЗЫВЫ", callback_data="results")],
        [InlineKeyboardButton(text="ОБРАТНАЯ СВЯЗЬ", callback_data="feedback")]
    ])

# Функция для добавления пользователя в базу данных
def add_user_to_db(user_id, username, date):
    if basic_collection.count_documents({"user_id": user_id}) == 0:
        basic_collection.insert_one({"user_id": user_id, "username": username, "date": date})
        logging.info(f"User {username} added to the basic_clstr database.")
    else:
        logging.info(f"User {username} already exists in the basic_clstr database.")

# Функция для добавления пользователя в subs_clstr после оплаты подписки
def add_user_to_subs_clstr(user_id, subscription_days):
    start_date = datetime.now()
    end_date = start_date + timedelta(days=subscription_days)
    subs_collection.insert_one({"user_id": user_id, "start_date": start_date, "end_date": end_date})
    logging.info(f"User {user_id} added to the subs_clstr database with subscription end date {end_date}.")

# Функция для отправки сообщения через 5 минут
async def send_delayed_message(user_id):
    await asyncio.sleep(300)  # 300 секунд = 5 минут
    if basic_collection.count_documents({"user_id": user_id}) > 0 and subs_collection.count_documents({"user_id": user_id}) == 0:
        await bot.send_message(user_id, "Привет! Вижу ты интересовалась ботом! В чем вопрос?")

# Обработчик команды /start
@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.username
    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    add_user_to_db(user_id, username, date)

    await message.answer_photo(
        IMAGES["main"],
        caption="Привет! \n\nМеня зовут Даша, я тренер по йоге с опытом более 4 лет. Если ты устал от болей в спине, стресса на работе или недостатка энергии, ты пришел по адресу!\n\nЯ помогу тебе:\n✨ Избавиться от болей в теле и улучшить осанку\n✨ Обрести внутренний баланс и спокойствие\n✨ Поднять уровень энергии и снять стресс, даже если у тебя очень плотный график.\n\nВ этом боте ты можешь узнать все о моих занятиях, тарифах и условиях. Готов улучшить свое тело и настроение? Давай начнем прямо сейчас!\n\nВыбери, что тебе интересно и давай сделаем первый шаг к здоровью!",
        reply_markup=main_menu()
    )

    # Запуск асинхронной задачи для отправки сообщения через 5 минут
    asyncio.create_task(send_delayed_message(user_id))

# Обработчик кнопки "ГРУППОВЫЕ ПРАКТИКИ"
@dp.callback_query(F.data == "group_practice")
async def group_practice_menu(callback_query: types.CallbackQuery):
    await callback_query.message.edit_media(
        types.InputMediaPhoto(media=IMAGES["group_practice"], caption="🫂Групповые практики\n\n✨ Практики в прямых эфирах 2 раза в неделю. ВТОРНИК, ПЯТНИЦА 8.00 МСК\n\n✨ Средняя продолжительность практики - 60 минут.\n\n✨ После каждого занятия запись сохраняется в канале. Тренируйтесь в любое удобное время, выбирая продолжительность и интенсивность, которая подходит именно вам.\n\n✨ Практики на канале идут от легких к сложным, поэтому можно спокойно начинать заниматься даже если у вас нет опыта в йоге."),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="ТАРИФ И ОПЛАТА", callback_data="tariff_group")],
            [InlineKeyboardButton(text="НАЗАД", callback_data="main_menu")]
        ])
    )

# Обработчик кнопки "ИНДИВИДУАЛЬНЫЕ ПРАКТИКИ"
@dp.callback_query(F.data == "individual_practice")
async def individual_practice_menu(callback_query: types.CallbackQuery):
    await callback_query.message.edit_media(
        types.InputMediaPhoto(media=IMAGES["individual_practice"], caption="🧘🧘🏻‍♀️Индивидуальные практики\n\n- Время и количество занятий подбирается индивидуально под ваше расписание.\n- Длительность: от 60 минут\n- Программа тренировочного процесса составляется индивидуально под ваш запрос и конкретное исходное состояние. За счет этого и происходит такой быстрый рост в практике.\n\n🌞Уже через 1-3 месяца регулярных практик вы почувствуете:\n- Спокойствие и более ясный ум в повседневной жизни.\n- Улучшение общего самочувствия, уменьшение дискомфорта в спине и суставах.\n- Легче справляться с рабочими и личными задачами, быстрее принимать решения."),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="ТАРИФ И ОПЛАТА", callback_data="tariff_individual")],
            [InlineKeyboardButton(text="НАЗАД", callback_data="main_menu")]
        ])
    )

# Обработчик кнопки "ПРОБНАЯ ПРАКТИКА"
@dp.callback_query(F.data == "trial_practice")
async def trial_practice_menu(callback_query: types.CallbackQuery):
    await callback_query.message.edit_media(
        types.InputMediaPhoto(media=IMAGES["trial_practice"], caption="Попробовав, ты ничего не теряешь, а только приобретаешь возможность изменить свою жизнь.\n\nПосле пробной практики напиши мне о своих ощущениях @dariakobrina.\n\nБуду тебе благодарна🤍"),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="ПОЛУЧИТЬ ПРОБНУЮ ПРАКТИКУ", url="https://youtu.be/ej-qJBF3jCQ?si=jMRDHDRvSrUZxfod")],
            [InlineKeyboardButton(text="НАЗАД", callback_data="main_menu")]
        ])
    )

# Обработчик кнопки "РЕЗУЛЬТАТЫ И ОТЗЫВЫ"
@dp.callback_query(F.data == "results")
async def results_menu(callback_query: types.CallbackQuery):
    # Отправка дополнительных фотографий
    for photo in ADDITIONAL_PHOTOS:
        await callback_query.message.answer_photo(photo=photo)

    # Отправка меню с фотографией после всех фотографий
    results_message = await callback_query.message.answer_photo(
        photo=IMAGES["results"],
        caption="Результаты и отзывы моих учеников.",
        reply_markup=results_menu_markup()
    )

    # Сохранение message_id для последующего обновления
    results_message_id = results_message.message_id

    # Обновление сообщения с кнопками
    await callback_query.message.edit_media(
        types.InputMediaPhoto(media=IMAGES["results"], caption="Результаты и отзывы моих учеников."),
        reply_markup=results_menu_markup()
    )

    # Сохранение message_id в контексте для последующего обновления
    dp.current_state(user=callback_query.from_user.id).update_data(results_message_id=results_message_id)

# Обработчик кнопки "НАЗАД" для результатов и отзывов
@dp.callback_query(F.data.startswith("results:"))
async def results_back_menu(callback_query: types.CallbackQuery):
    state = dp.current_state(user=callback_query.from_user.id)
    data = await state.get_data()
    message_id = data.get("results_message_id")

    if message_id:
        await bot.edit_message_media(
            chat_id=callback_query.message.chat.id,
            message_id=message_id,
            media=types.InputMediaPhoto(media=IMAGES["main"], caption="Привет! \n\nМеня зовут Даша, я тренер по йоге с опытом более 4 лет. Если ты устал от болей в спине, стресса на работе или недостатка энергии, ты пришел по адресу!\n\nЯ помогу тебе:\n✨ Избавиться от болей в теле и улучшить осанку\n✨ Обрести внутренний баланс и спокойствие\n✨ Поднять уровень энергии и снять стресс, даже если у тебя очень плотный график.\n\nВ этом боте ты можешь узнать все о моих занятиях, тарифах и условиях. Готов улучшить свое тело и настроение? Давай начнем прямо сейчас!\n\nВыбери, что тебе интересно и давай сделаем первый шаг к здоровью!"),
            reply_markup=main_menu()
        )

# Обработчик кнопки "ОБРАТНАЯ СВЯЗЬ"
@dp.callback_query(F.data == "feedback")
async def feedback_menu(callback_query: types.CallbackQuery):
    await callback_query.message.edit_media(
        types.InputMediaPhoto(media=IMAGES["feedback"], caption="Чтобы задать дополнительные вопросы и узнать подробнее о практиках напишите мне @dariakobrina."),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="НАЗАД", callback_data="main_menu")]
        ])
    )

# Обработчик кнопки "ТАРИФ И ОПЛАТА" для групповых практик
@dp.callback_query(F.data == "tariff_group")
async def tariff_group_menu(callback_query: types.CallbackQuery):
    await callback_query.message.edit_media(
        types.InputMediaPhoto(media=IMAGES["tariff"], caption="Приобретите нужную подписку по актуальной стоимости:\n\nПОДПИСКА 1 МЕСЯЦ - 2.450 ₽.\nПОДПИСКА 3 МЕСЯЦА - 6.835 ₽.\nПОДПИСКА 6 МЕСЯЦЕВ 12.495 ₽.\n\n💳 Вы можете оплатить подписку любой картой РФ банка или иностранного банка.\n\n💱Так же доступна оплата криптовалютой (USDT). Условия оплаты криптой смотрите далее в разделе «ОПЛАТИТЬ КРИПТОЙ»."),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="ОПЛАТА", callback_data="payment_group")],
            [InlineKeyboardButton(text="НАЗАД", callback_data="group_practice")],
            [InlineKeyboardButton(text="ГЛАВНОЕ МЕНЮ", callback_data="main_menu")]
        ])
    )

# Обработчик кнопки "ОПЛАТИТЬ" для групповых практик
@dp.callback_query(F.data == "payment_group")
async def payment_group_menu(callback_query: types.CallbackQuery):
    await callback_query.message.edit_media(
        types.InputMediaPhoto(media=IMAGES["tariff"], caption="Выберите нужную подписку"),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="ПОДПИСКА 1 МЕСЯЦ", callback_data="subscription_30")],
            [InlineKeyboardButton(text="ПОДПИСКА 3 МЕСЯЦА", callback_data="subscription_90")],
            [InlineKeyboardButton(text="ПОДПИСКА 6 МЕСЯЦЕВ", callback_data="subscription_180")],
            [InlineKeyboardButton(text="ОПЛАТИТЬ КРИПТОЙ", callback_data="payment_crypto")],
            [InlineKeyboardButton(text="ГЛАВНОЕ МЕНЮ", callback_data="main_menu")]
        ])
    )

# Обработчик кнопки "ОПЛАТИТЬ КРИПТОЙ" для групповых практик
@dp.callback_query(F.data == "payment_crypto")
async def payment_crypto_menu(callback_query: types.CallbackQuery):
    await callback_query.message.edit_media(
        types.InputMediaPhoto(media=IMAGES["tariff"], caption="Стоимость в USDT:\n\nПОДПИСКА 1 МЕСЯЦ - 24$\nПОДПИСКА 3 МЕСЯЦА - 68$\nПОДПИСКА 6 МЕСЯЦЕВ - 124$\n\nСеть - TRC 20\nTMrL9Yk1Mse7yLAbKdqeTC8DztwRhr9Ptk\n\nБудьте внимательны при копировании адреса кошелька. Перед совершением оплаты убедитесь в корректности адреса.\n\nПосле совершения оплаты сделайте скрин-шот успешной операции и нажмите на кнопку ниже и отправьте скрин-шот успешной операции."),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="ОПЛАТИЛ(А) - ОТПРАВИТЬ СКРИН", url="https://t.me/dariakobrina")],
            [InlineKeyboardButton(text="ГЛАВНОЕ МЕНЮ", callback_data="main_menu")]
        ])
    )

# Обработчик кнопки "ТАРИФ И ОПЛАТА" для индивидуальных практик
@dp.callback_query(F.data == "tariff_individual")
async def tariff_individual_menu(callback_query: types.CallbackQuery):
    await callback_query.message.edit_media(
        types.InputMediaPhoto(media=IMAGES["tariff"], caption="💲Актуальная стоимость:\n\nОдно занятие - 3.000₽.\nАбонемент на месяц (8 практик) - 24.000 ₽.\n\n💱Crypto (USDT)\n\nОдно занятие - 30$\nАбонемент на месяц (8 практик) - 240$\n\n💳 Вы можете оплатить подписку любой картой РФ банка.\n\n💱Так же доступна оплата криптовалютой (USDT).\n\nЧтобы записаться на индивидуальную практику нажмите кнопку «ЗАПИСАТЬСЯ НА ПРАКТИКУ» и напишите мне."),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="ЗАПИСАТЬСЯ НА ПРАКТИКУ", url="https://t.me/dariakobrina")],
            [InlineKeyboardButton(text="НАЗАД", callback_data="individual_practice")],
            [InlineKeyboardButton(text="ГЛАВНОЕ МЕНЮ", callback_data="main_menu")]
        ])
    )

# Обработчик кнопок подписок
@dp.callback_query(F.data.startswith("subscription_"))
async def handle_subscription(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    subscription_days = int(callback_query.data.split("_")[1])
    add_user_to_subs_clstr(user_id, subscription_days)
    await callback_query.message.answer("Спасибо за подписку! Теперь у вас есть доступ к каналу.")

    # Отправка ссылки на канал
    await bot.send_message(user_id, "Вот ссылка на канал: https://t.me/+UtAKtXuubOdlNWQy")

# Обработчик кнопки "НАЗАД"
@dp.callback_query(F.data == "main_menu")
async def main_menu_handler(callback_query: types.CallbackQuery):
    await callback_query.message.edit_media(
        types.InputMediaPhoto(media=IMAGES["main"], caption="Привет! \n\nМеня зовут Даша, я тренер по йоге с опытом более 4 лет. Если ты устал от болей в спине, стресса на работе или недостатка энергии, ты пришел по адресу!\n\nЯ помогу тебе:\n✨ Избавиться от болей в теле и улучшить осанку\n✨ Обрести внутренний баланс и спокойствие\n✨ Поднять уровень энергии и снять стресс, даже если у тебя очень плотный график.\n\nВ этом боте ты можешь узнать все о моих занятиях, тарифах и условиях. Готов улучшить свое тело и настроение? Давай начнем прямо сейчас!\n\nВыбери, что тебе интересно и давай сделаем первый шаг к здоровью!"),
        reply_markup=main_menu()
    )

# Обработчик вебхука для получения уведомлений о платежах от Prodamus
async def handle_webhook(request):
    data = await request.json()
    try:
        # Проверка подписи
        signature = request.headers.get("X-Signature")
        if signature != "37bc20c9d78758f336c5777b955ece74733e7fc31d42132c965d92f7f78c6f51":
            logging.error("Invalid signature")
            return web.Response(status=403)

        # Обработка данных платежа
        payment_data = json.loads(data)
        user_id = payment_data["user_id"]
        subscription_days = payment_data["subscription_days"]

        # Обновление базы данных
        add_user_to_subs_clstr(user_id, subscription_days)

        logging.info(f"User {user_id} subscription updated to {subscription_days} days")
        return web.Response(status=200)
    except Exception as e:
        logging.error(f"Error processing payment: {e}")
        return web.Response(status=500)

# Главная функция запуска бота
async def main():
    dp.startup.register(lambda: print("Бот запущен"))
    dp.message.register(send_welcome)
    dp.callback_query.register(group_practice_menu, F.data == "group_practice")
    dp.callback_query.register(individual_practice_menu, F.data == "individual_practice")
    dp.callback_query.register(trial_practice_menu, F.data == "trial_practice")
    dp.callback_query.register(results_menu, F.data == "results")
    dp.callback_query.register(feedback_menu, F.data == "feedback")
    dp.callback_query.register(tariff_group_menu, F.data == "tariff_group")
    dp.callback_query.register(payment_group_menu, F.data == "payment_group")
    dp.callback_query.register(tariff_individual_menu, F.data == "tariff_individual")
    dp.callback_query.register(main_menu_handler, F.data == "main_menu")
    dp.callback_query.register(results_back_menu, F.data.startswith("results:"))
    dp.callback_query.register(handle_subscription, F.data.startswith("subscription_"))

    # Настройка вебхука
    app = web.Application()
    app.router.add_post("/webhook", handle_webhook)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", 8080)
    await site.start()

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
