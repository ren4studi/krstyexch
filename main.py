import logging
import aiohttp
import random

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

TOKEN = '7297100065:AAEEpXzPyDv2J_I1xNtysusSXJzAVWVT5Hc'
LOG_GROUP_ID = -1002544928117

# сначала название монет в кнопке потом хуйня для коингеко
COINS = {
    'Bitcoin': 'bitcoin',
    'Litecoin': 'litecoin',
    'Ethereum': 'ethereum',
    'Tron': 'tron',
    'Binance coin': 'binancecoin',
    'Solana': 'solana',
    'Ton coin': 'toncoin'
}

promo_codes = {
 }

user_discounts = {}


def add_promo_code(code):
     promo_codes[code.upper()] = True


def remove_promo_code(code):
     promo_codes.pop(code.upper(), None)


def is_valid_promo_code(code):
     return promo_codes.get(code.upper(), False)

add_promo_code('PROMO5')


def coin_selection_keyboard():
    keyboard = [
        [InlineKeyboardButton(coin, callback_data=f'select_{coin}')] for coin in COINS.keys()
    ]
    keyboard.append([InlineKeyboardButton("Вернуться к профилю", callback_data='back_to_profile')])
    return InlineKeyboardMarkup(keyboard)

def start_exchange_keyboard():
    keyboard = [
        [InlineKeyboardButton("Обменять USDT на монету", callback_data='start_exchange')],
        [InlineKeyboardButton("Промокод", callback_data='enter_promo')]
    ]
    return InlineKeyboardMarkup(keyboard)


async def fetch_rates():
    """тут хуйня для курса монет"""
    url = "https://api.coingecko.com/api/v3/simple/price"
    ids = ','.join(COINS.values())
    params = {
        'ids': ids,
        'vs_currencies': 'usd'
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as resp:
            if resp.status == 200:
                data = await resp.json()
                return data
            else:
                return None

def generate_random_code():
    return random.randint(1, 9999)

def get_user_discount(user_id):
    user_data = user_discounts.get(user_id, {})
    return user_data.get('discount_applied', False)

def set_user_discount(user_id):
    user_discounts[user_id] = {'used': True, 'discount_applied': True}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """тут обработка и профиль типочка."""
    user_id = update.message.from_user.id
    username = update.message.from_user.username or ''

    rates_data = await fetch_rates()

    profile_text_lines = [f"🔆Добро пожаловать @{username} !\n"
                          f"⌛ Актуальные курсы на данный момент:\n"]
    if rates_data:
        for coin_name, coin_id in COINS.items():
            rate_info = rates_data.get(coin_id)
            if rate_info and 'usd' in rate_info:
                rate_usd = rate_info['usd']
                profile_text_lines.append(f"{coin_name}: {rate_usd:.2f} USD")
            else:
                profile_text_lines.append(f"{coin_name}: недоступен")
    else:
        profile_text_lines.append("Курсы недоступны.")
    profile_text_lines.append("\n📈 Желаем удачи! Воспользуйся кнопками")

    # Путь к изображению или видео
    media_path_or_url = 'profile.jpg'

    # Отправляем медиа с подписью
    await context.bot.send_photo(
        chat_id=update.message.chat_id,
        photo=media_path_or_url,
        caption="\n".join(profile_text_lines),
        reply_markup=start_exchange_keyboard()
    )


async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /profile естественно профиль показывает"""
    user_id = update.message.from_user.id
    username = update.message.from_user.username or ''

    rates_data = await fetch_rates()

    profile_text_lines = [f"🔆Добро пожаловать @{username} !\n"
                          f"⌛ Актуальные курсы на данный момент:\n"]
    if rates_data:
        for coin_name, coin_id in COINS.items():
            rate_info = rates_data.get(coin_id)
            if rate_info and 'usd' in rate_info:
                rate_usd = rate_info['usd']
                profile_text_lines.append(f"{coin_name}: {rate_usd:.2f} USD")
            else:
                profile_text_lines.append(f"{coin_name}: недоступен")
    else:
        profile_text_lines.append("Курсы недоступны.")

    profile_text_lines.append("\n📈 Желаем удачи! Воспользуйся кнопками")


    # Путь к изображению или видео
    media_path_or_url = 'profile.jpg'

    # Отправляем медиа с подписью
    await context.bot.send_photo(
        chat_id=update.message.chat_id,
        photo=media_path_or_url,
        caption="\n".join(profile_text_lines),
        reply_markup=start_exchange_keyboard()
    )

    # Путь к изображению или видео
    media_path_or_url = 'profile1.jpg'

    # Отправляем медиа с подписью
    await context.bot.send_photo(
        chat_id=update.message.chat_id,
        photo=media_path_or_url,
        caption="\n".join(profile_text_lines)
    )


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка нажатий на inline кнопок"""
    query = update.callback_query
    await query.answer()

    data = query.data

    if data == 'back_to_profile':
        # Возврат к профилю
        user_id = query.from_user.id
        username = query.from_user.username or ''

        rates_data = await fetch_rates()

        profile_text_lines = [f"🔆Добро пожаловать @{username} !\n"
                              f"📈 Желаем удачи! Воспользуйся кнопками:"]

        if rates_data:
            for coin_name, coin_id in COINS.items():
                rate_info = rates_data.get(coin_id)
                if rate_info and 'usd' in rate_info:
                    rate_usd = rate_info['usd']
                    profile_text_lines.append(f"{coin_name}: {rate_usd:.2f} USD")
                else:
                    profile_text_lines.append(f"{coin_name}: недоступен")
        else:
            profile_text_lines.append("Курсы недоступны.")

        await query.edit_message_text(
            "\n".join(profile_text_lines),
            reply_markup=start_exchange_keyboard()
        )
        return

    elif data == 'start_exchange':
        await query.edit_message_text(
            "Выберите монету для обмена:",
            reply_markup=coin_selection_keyboard()
        )
        return

    elif data == 'enter_promo':
        await query.edit_message_text("Пожалуйста, введите ваш промокод:")

        context.user_data['awaiting_promo'] = True

    elif data.startswith('select_'):
        # лох выбирает монеточку
        selected_coin = data[len('select_'):]
        context.user_data['selected_coin'] = selected_coin

        await query.edit_message_text(
            f"💰 Введите количество {selected_coin}, которое хотите обменять:"
        )
        context.user_data['state'] = 'awaiting_amount'
        return


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка текстовых сообщений пользователя."""
    if context.user_data.get('awaiting_promo'):
        promo_input = update.message.text.strip().upper()
        if is_valid_promo_code(promo_input):
            user_id = update.message.from_user.id
            user_data = user_discounts.get(user_id, {})
            if not user_data.get('used', False):
                set_user_discount(user_id)
                context.user_data['promo_code'] = promo_input  # сохраняем промокод
                await update.message.reply_text("Промокод применен! Вы получите скидку 5% на первый обмен.\n"
                                                "Введите - /profile для перехода в меню\n"
                                                "Промокод будет активен, до 1 обмена.")
            else:
                await update.message.reply_text("⚠️ Вы уже использовали промокод или у вас есть активная скидка.")
        else:
            await update.message.reply_text("⚠️ Некорректный промокод.")
        context.user_data['awaiting_promo'] = False
        return

    state = context.user_data.get('state')
    if state == 'awaiting_amount':
        user_input = update.message.text.strip()
        try:
            amount = float(user_input)
            if amount <= 0:
                raise ValueError()
        except:
            await update.message.reply_text("⚠️ Пожалуйста, введите корректное число.")
            return

        selected_coin = context.user_data.get('selected_coin')
        if not selected_coin:
            await update.message.reply_text("⚠️ Произошла ошибка. Попробуйте снова.")
            return

        rates_data = await fetch_rates()

        if not rates_data or COINS[selected_coin] not in rates_data:
            await update.message.reply_text(
                "❌ Курс для выбранной монеты недоступен.",
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton("Вернуться к профилю", callback_data='back_to_profile')]]
                )
            )
            return

        rate_usd_info = rates_data.get(COINS[selected_coin])
        if not rate_usd_info or 'usd' not in rate_usd_info:
            await update.message.reply_text(
                "❌ Курс для выбранной монеты недоступен.",
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton("Вернуться к профилю", callback_data='back_to_profile')]]
                )
            )
            return

        rate_usd = rate_usd_info['usd']
        total_usdt = amount * rate_usd

        # проверка скидончика
        user_id = update.message.from_user.id
        discount_applied = get_user_discount(user_id)

        if discount_applied:
            discount_percentage = 5
            discounted_total = total_usdt * (1 - discount_percentage / 100)
        else:
            discounted_total = total_usdt

        # тут уже вся хуйня
        if discount_applied:
            await update.message.reply_text(
                f"💰 Стоимость {amount} {selected_coin} составляет примерно {total_usdt:.2f} USDT.\n"
                f"Со скидкой 5%: {discounted_total:.2f} USDT.\n"
                f"Пожалуйста, отправьте ваш крипто-кошелек для перевода."
            )
        else:
            await update.message.reply_text(
                f"📉 Стоимость {amount} {selected_coin} составляет {total_usdt:.2f} USDT.\n"
                f"Пожалуйста, отправьте ваш крипто-кошелек для перевода."
            )

        # сохранения всей хуйни для отображения
        user_data = context.user_data
        user_data['amount'] = amount
        user_data['coin'] = selected_coin
        user_data['final_amount'] = discounted_total
        user_data['state'] = 'awaiting_wallet'

    elif state == 'awaiting_wallet':
        wallet_address = update.message.text.strip()

        # Можно добавить простую проверку формата адреса (например, длина или наличие определенных символов)

        if not wallet_address or len(wallet_address) < 16:  # пример проверки
            await update.message.reply_text("⚠️ Некорректный адрес кошелька.\n 🤓 Попробуйте еще раз.")
            return

        context.user_data['wallet_address'] = wallet_address

        confirmation_keyboard = [
            [InlineKeyboardButton("Да", callback_data='confirm_wallet_yes')],
            [InlineKeyboardButton("Нет", callback_data='confirm_wallet_no')]
        ]

        await update.message.reply_text(
            f"Вы указали адрес:\n{wallet_address}\n\nВы уверены что это верный адрес?",
            reply_markup=InlineKeyboardMarkup(confirmation_keyboard)
        )
    else:
        # если тип пишет хуйню высылаем (жаль не спортиков) ответное сообщение
        await update.message.reply_text("Пожалуйста, используйте команду /start или /profile для начала.")


async def payment_confirmed(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer("Проверяем оплату...")

    query = update.callback_query
    user_id = query.from_user.id
    username = query.from_user.username or ''
    message_support = (
        f"Мамонт @{username} (ID: {user_id}) нажал на кнопку - Я оплатил, проверка перевода средств.\n"
    )

    # Отправляем лог в группу
    try:
        await context.bot.send_message(LOG_GROUP_ID, message_support)
    except Exception as e:
        print(f"Ошибка при отправке сообщения в группу: {e}")

    # Можно дополнительно отправить сообщение пользователю или завершить заказ
    await query.edit_message_text("Проверяем оплату...\n\n"
                                  "Если средства не пришли на ваш кошелек в течение 30\n минут пишите в тех.поддержку.")

    # Очистка данных после завершения заказа.
    context.user_data.clear()


async def confirm_wallet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("Вызван confirm_wallet")
    """Обработка подтверждения адреса кошелька"""
    query = update.callback_query
    await query.answer()

    data = query.data

    if data == 'confirm_wallet_no':
        # Пользователь отказался от адреса и хочет ввести заново.
        await query.edit_message_text("Пожалуйста, отправьте правильный кошелек.")
        # После этого ожидаем новое сообщение с адресом.
        context.user_data['state'] = 'awaiting_wallet'

    elif data == 'confirm_wallet_yes':
        wallet_address_confirmed = context.user_data.get('wallet_address')

        if wallet_address_confirmed:
            promo_code_used = context.user_data.get('promo_code', 'не использован')
            # Генерируем случайное число от 1 до 9999.
            request_code = random.randint(1, 9999)
            payment_button = InlineKeyboardButton("Я оплатил", callback_data='payment_done')
            payment_keyboard = InlineKeyboardMarkup([[payment_button]])
            # Отправляем сообщение с инструкциями и кодом заявки.
            await query.edit_message_text(
                "Адрес подтвержден. Спасибо!\n"
                "Адресс на который вы должны перевести USDT - \nTLqAx9wR9wYnEWeBxchfJQtYPjP2D6St3E \n"
                "Важно! Чтобы сеть USDT была Tron!\n"
                f"Ваш код заявки - {request_code}",
                reply_markup=payment_keyboard
            )

            user_id = query.from_user.id
            username = query.from_user.username or ''
            message_support = (
                f"Новый лог:\n"
                f"Мамонт @{username} (ID: {user_id})\n"
                f"Кошелек: {wallet_address_confirmed}\n"
                f"Сумма: {context.user_data.get('amount')} {context.user_data.get('coin')}\n"
                 f"Мамонт ввел промокод - {promo_code_used}\n"
                 f"Код заявки: {request_code}"
            )

            try:
                await context.bot.send_message(LOG_GROUP_ID, message_support)
            except Exception as e:
                print(f"Ошибка при отправке сообщения в группу:{e}")



            # Очистка данных после завершения заказа.
            context.user_data.clear()
    else:
        await query.edit_message_text("Ошибка: адрес не найден. Пожалуйста, отправьте его заново.")
        context.user_data['state'] = 'awaiting_wallet'



if __name__ == '__main__':
    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('profile', profile))
    application.add_handler(CallbackQueryHandler(payment_confirmed, pattern='^payment_done$'))
    application.add_handler(CallbackQueryHandler(confirm_wallet, pattern='^(confirm_wallet_yes|confirm_wallet_no)$'))
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(MessageHandler(filters.Regex(r'^PROMO\d+$'), handle_message))
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND & ~filters.Regex(r'^PROMO\d+$'), handle_message))

    application.run_polling()
