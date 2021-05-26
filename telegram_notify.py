import os
import telebot

# You need to set environment variables TG_CHAT_ID and TG_BOT_TOKEN
# for example:
# export TG_BOT_TOKEN="jehfjh92dkjs0fdpja00vjja"

# How to create telegram bot end get Token?
# 1. Find @BotFather in Telegram.
# 2. Create new bot by command /newbot.
# 3. Set name. Get token.
# How to get CHAT_ID?:
# 1. Find @userinfobot in Telegram
# 2. Command /start
# 3. Get your chat id

CHAT_ID = os.environ.get('TG_CHAT_ID')
BOT_TOKEN = os.environ.get('TG_BOT_TOKEN')


def send_tg(message):

    bot = telebot.TeleBot(BOT_TOKEN)
    bot.send_message(CHAT_ID, message)
