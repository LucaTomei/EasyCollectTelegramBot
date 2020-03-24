from telepot.loop import MessageLoop
import telepot, time
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove


from utils import Utils


class EasyCollect_Bot(object):
	def __init__(self):
		self.Utils_obj = Utils()
		self.bot_token = self.Utils_obj.getToken()
		self.bot = telepot.Bot(self.bot_token)
	

	def handler(self, msg):
		chat_id = msg['chat']['id']
		first_name = msg['from']['first_name']
		last_name = msg['from']['last_name']
		message_send = msg['text']
		msgToSend = "*Ciao " + first_name + " " +  last_name + "*, per caso mi hai inviato *" + message_send + "*?"
		

		self.bot.sendMessage(chat_id, msgToSend, parse_mode = 'Markdown')



	def main(self):
		print("Bot in Loop...")
		MessageLoop(self.bot, self.handler).run_as_thread()


		while 1:
			time.sleep(1)



if __name__ == '__main__':
	botInstance = EasyCollect_Bot()
	botInstance.main()
