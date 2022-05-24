import logging
import os
import re
import sqlite3

import markovify
import wikipedia
from decouple import config
# Устанавливаем русский язык в Wikipedia
from telegram import KeyboardButton, ReplyKeyboardMarkup

wikipedia.set_lang("ru")
import gender
from Demotivator import Demotivator
import telegram

from telegram.ext import (Updater, CommandHandler, MessageHandler, ConversationHandler, Filters)
from gtts import gTTS

logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)
from chatterbot import ChatBot

chatbot = ChatBot('Kiki')


def getwiki(s):
    try:
        ny = wikipedia.page(s)
        wikitext = ny.content[:1000]
        wikimas = wikitext.split('.')
        wikimas = wikimas[:-1]
        wikitext2 = ''
        for x in wikimas:
            if not ('==' in x):
                if (len((x.strip())) > 3):
                    wikitext2 = wikitext2 + x + '.'
            else:
                break
        wikitext2 = re.sub('\([^()]*\)', '', wikitext2)
        wikitext2 = re.sub('\([^()]*\)', '', wikitext2)
        wikitext2 = re.sub('\{[^\{\}]*\}', '', wikitext2)
        return wikitext2
    except Exception as e:
        return 'В энциклопедии нет информации об этом'


def generate(text, out_file):
    tts = gTTS(text=text, lang="ru")
    tts.save(out_file)


def get_model(filename):
    with open(filename, encoding="utf-8") as f:
        text = f.read()

    return markovify.Text(text)


def start(update, context):
    sqlite_connection = sqlite3.connect('sqlite_python.db')
    cursor = sqlite_connection.cursor()
    info = cursor.execute('SELECT * FROM telegram_users WHERE idTelegram=?', (update.message.from_user.id,))
    if info.fetchone() is None:
        cursor.execute(
            f"INSERT INTO telegram_users (name, username,idTelegram)VALUES('{update.message.from_user.name}', '{update.message.from_user.username}', {update.message.from_user.id})")
        sqlite_connection.commit()
    cursor.close()
    buttons = [
        [  # start a row
            KeyboardButton("/help", callback_data="button1"),
            KeyboardButton("/start", callback_data="button2"),
        ]
    ]
    buttons_markup = ReplyKeyboardMarkup(buttons)
    update.message.reply_text("""  🌄Я могу болтать, всё что ты скажешь я запомню и буду учиться(ну пока учиться буду).
Также есть демотиватор нужно вставить фотку и оставить 2 строковый коментарий в поле caption.
Скинь свою 🌅 реальную фоточку 🌄 и я скажу, что думаю о тебе.\nКоманды:\n/help /start - крики помощи.\n/cancel - не работает(заглушка)\n/wiki \'  \' - поиск в wiki.\n 🍀🍀🍀Удачи🍀🍀🍀""")


def error(update, context):
    logger.warning('update "%s" casused error "%s"', update, context.error)


def photo(update, context):
    context.bot.send_chat_action(chat_id=update.effective_message.chat_id, action=telegram.ChatAction.RECORD_AUDIO)
    id = update.message.from_user.id
    out_file = "./user_data/" + str(id) + "mp3"
    name = str(id) + ".jpg"
    filepath = "./user_data/" + name
    largest_photo = update.message.photo[-1].get_file()
    largest_photo.download(filepath)
    if update.message.caption:
        try:
            demotText = update.message.caption.split('\n', 1)
            dem = Demotivator(demotText[0], demotText[1])  # 2 строчки
            dem.create(filepath)  # Название изображения, которое будет взято за основу демотиватора
            update.message.reply_photo(photo=open('./user_data/demresult.jpg', 'rb'))
            os.remove('./user_data/demresult.jpg')
            os.remove(filepath)
        except:
            update.message.reply_text("Подпиши в две строчки")
            os.remove(filepath)
        return

    genders = gender.resolve(filepath)
    if len(genders) == 0:
        update.message.reply_text("Отправь сюда фото с людьми, на этой фотографии я их не вижу")
        os.remove(filepath)
        return

    text = ""
    generator = None

    if genders[0] == "female":
        generator = get_model("female")
    else:
        generator = get_model("male")

    statement = True

    while statement:
        text = generator.make_sentence()
        if text is not None:
            statement = False

    generate(text, out_file)
    update.message.reply_audio(audio=open(out_file, "rb"))
    os.remove(out_file)
    os.remove(filepath)


def help(update, context):
    update.message.reply_text(
        "Скинь свою 🌅 реальную фоточку 🌄 и я скажу, что думаю о тебе.\nКоманды:\n/help /start - крики помощи.\n/cancel - Я обижусь.\n/wiki \'  \' - поиск в wiki.\n 🍀🍀🍀Удачи🍀🍀🍀")


def cancel(update, context):
    return ConversationHandler.END


def wiki(update, context):
    try:
        search = update.message.text.split(' ', 1)[1]
        update.message.reply_text(getwiki(search))
    except Exception as e:
        update.message.reply_text('Ты не написал запрос')


def messageAI(update, context):
    response = chatbot.get_response(update.message.text)
    update.message.reply_text(str(response))


def main():
    updater = Updater(config("TOKEN", default=''), use_context=True)
    dp = updater.dispatcher

    photo_handler = MessageHandler(Filters.photo, photo)
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler("cancel", cancel))
    dp.add_handler(CommandHandler("wiki", wiki))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(MessageHandler(Filters.text, messageAI))
    dp.add_handler(photo_handler)
    dp.add_error_handler(error)

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
