import telebot, os, logging, psycopg2
from flask import Flask, request

TOKEN = "773839668:AAEHel4AUB-ZSIqpHI_HqOXyPbgErpebk_g"
bot = telebot.TeleBot(TOKEN)
DATABASE_URL = os.environ['DATABASE_URL']
conn = psycopg2.connect(DATABASE_URL, sslmode='require')
cur = conn.cursor()

@bot.message_handler(commands=['start'])
def start(message):
	cur.execute("SELECT * FROM Users")
	while True:
		row = cur.fetchone()
		if row == None:
			bot.send_message(message.chat.id, 'Hello, ' + message.from_user.first_name)
			break
		else:
			if row[0] == message.from_user.id:
				mess = "ID: " + str(row[0])
				if row[1] != "-":
					mess += "\nUsername: " + row[1]
				mess += "\nFirst name: " + row[2]
				if row[3] != "-":
					mess += "\nLast name: " + row[3]
				mess += "\nFirst message: \"" + row[4] +"\""
				bot.send_message(message.chat.id, mess)
				break

@bot.message_handler(func=lambda message: True, content_types=['text'])
def echo_message(message):
	cur.execute("SELECT * FROM Users")
	while True:
		row = cur.fetchone()
		if row == None:
			mess = 'INSERT INTO Users VALUES(' + str(message.from_user.id)
			if message.from_user.username != None:
				mess += ', \'' + message.from_user.username + '\', \''
			else:
				mess += ', \'-\', \''
			mess += message.from_user.first_name + '\', \''
			if message.from_user.last_name != None:
				mess += message.from_user.last_name + '\', \''
			else:
				mess += '-\', \''
			mess += message.text + '\')'
			cur.execute(mess)
			conn.commit()
			bot.send_message(message.chat.id, "Your data in database")
			break
		else:
			if row[0] == message.from_user.id:
				mess = "ID: " + str(row[0])
				if row[1] != "-":
					mess += "\nUsername: " + row[1]
				mess += "\nFirst name: " + row[2]
				if row[3] != "-":
					mess += "\nLast name: " + row[3]
				mess += "\nFirst message: \"" + row[4] +"\""
				bot.send_message(message.chat.id, mess)
				break


if "HEROKU" in list(os.environ.keys()):
    logger = telebot.logger
    telebot.logger.setLevel(logging.INFO)

    server = Flask(__name__)
    @server.route("/bot", methods=['POST'])
    def getMessage():
        bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
        return "!", 200
		
    @server.route("/")
    def webhook():
        bot.remove_webhook()
        bot.set_webhook(url="https://stark-mountain-74246.herokuapp.com/bot")
        return "?", 200
    server.run(host="0.0.0.0", port=os.environ.get('PORT', 80))
else:
    bot.remove_webhook()
    bot.polling(none_stop=True)