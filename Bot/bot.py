import json, requests, telepot, time
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove

from utils import Utils

# 	Dopo aver inviato la roba tramite rest devo resettare le variabili locali -----|
#	self.resetAllVariables()	<--------------------------------------------------|

# rimozione altra categoria 

"""
"Benvenuto <NomeCliente>, del negozio <NomeNegozio>.
Sono EasyCollect, il bot che ti accompagnerà nella vendita online della tua attività. 
Nei pannelli sottostanti potrai selezionare le categorie che descrivono il tuo negozio e condividerne la posizione con i clienti.
"""

class Bot(object):
	def __init__(self):
		self.Utils_obj = Utils()
		self.bot_token = self.Utils_obj.getToken()	# contiene il token del bot

		self.bot = telepot.Bot(self.bot_token)

		# Definizione Bottoni tastiera
		self.button_location = "📍 Posizione 📍"
		self.button_categoty = "🥐 Categoria 🍷"
		self.stop_button = "Fine"
		self.other_categories_button = "Altra Categoria"
		self.yes_button = "👍 SI 👍"
		self.no_button = "👎 NO 👎"

		categories_list = self.Utils_obj.getAllMerchantCategories()
		self.categories_keyboard = self.makeAKeyboard(categories_list, 6)
		
		self.main_keyboard = [[self.button_categoty],[self.button_location]]

		self.yes_no_keyboard = [[self.yes_button],[self.no_button]]

		self.category_message = "Seleziona a quale categoria appartiene il tuo negozio.(Max 3)\n*[Premere il pulsante Fine per terminare la selezione]*"
		self.position_message = "Inviami la posizione(clicca sulla spilla e seleziona *Posizione*, quindi seleziona *Invia posizione corrente*)"
		self.main_message = "Utilizza la tastiera sottostante"
		self.category_error_message = "Inserire almeno una tra le categorie elencate"
		


		self.added_categories = []
		self.myLocation = (None, None)

		self.max_categories = 3
		
		self.resetAllVariables()
		
	def makeAKeyboard(self,alist, parti):
	    length = len(alist)
	    keyboard =  [alist[i*length // parti: (i+1)*length // parti] for i in range(parti)]
	    keyboard.append([self.other_categories_button, self.stop_button])
	    return keyboard

	def resetAllVariables(self):
		self.count_categories = 0
		self.is_set_categoria = False
		self.is_set_location = False
		self.i_can_send_location = False
		self.myLocation = (None, None)
		self.yes_no_step = (False, None)

	def main_handler(self, msg):
		try:
			content_type, chat_type, chat_id = telepot.glance(msg)
			print("Tipo contenuto: " + content_type + " - Tipo Chat: " + chat_type)
			chat_id = msg['chat']['id']
			first_name = msg['from']['first_name']
			last_name = msg['from']['last_name']
			group_title = msg['chat']['title']

			# si tratta di un commerciante che è in un gruppo
			if 'chat' in msg and 'group' in chat_type:	# per gruppi e supergruppi
				if not self.is_set_location or not self.is_set_categoria:
					# Si tratta di messaggio testuale
					if content_type == 'text':
						chat_message = msg['text']
						# hai premuto uno dei bottoni della tastiera principale
						if chat_message in [j for i in self.main_keyboard for j in i]:
							if chat_message == self.button_categoty:
								self.bot.sendMessage(chat_id, text=self.category_message, reply_markup={'keyboard': self.categories_keyboard},parse_mode= 'Markdown')
							elif chat_message == self.button_location:
								self.bot.sendMessage(chat_id, text=self.position_message,parse_mode= 'Markdown', reply_markup = ReplyKeyboardRemove())
								self.i_can_send_location = True

						elif chat_message in [j for i in self.yes_no_keyboard for j in i] and self.yes_no_step[0]:
							category = self.yes_no_step[1]
							if chat_message == self.yes_button:
								self.added_categories.append(category)
								self.count_categories += 1
								# rimozione bottone categoria dalla tastiera principale
								if self.count_categories == self.max_categories:
									self.main_keyboard = [[self.button_location]]
									self.is_set_categoria = True
									toSend = "Ecco le categorie che hai impostato *" + str(self.added_categories) + "*"
									if self.is_set_location:
										toSend = toSend + ", questa è la posizione del tuo negozio " + str(self.myLocation[1])
										self.bot.sendMessage(chat_id, text=toSend, reply_markup={'keyboard': self.main_keyboard},parse_mode= 'Markdown')
									else:
										self.bot.sendMessage(chat_id, text=toSend, reply_markup={'keyboard': self.main_keyboard},parse_mode= 'Markdown')
								else:
									self.bot.sendMessage(chat_id, text="Categoria *" + category +"* aggiunta con successo [Premere il pulsante *Fine* per terminare la selezione]", reply_markup={'keyboard': self.categories_keyboard},parse_mode= 'Markdown')
							elif chat_message == self.no_button:
								self.bot.sendMessage(chat_id, text="Inserire nuovamente la categoria", reply_markup={'keyboard': self.categories_keyboard},parse_mode= 'Markdown')
							self.yes_no_step = (False, None)
						elif chat_message in [j for i in self.categories_keyboard for j in i]:
							if chat_message == self.stop_button:
								if len(self.added_categories) > 0:
									self.is_set_categoria = True
									if not self.is_set_location:
										self.main_keyboard = [[self.button_location]]
										toSend = "Ecco le categorie che hai impostato *" + str(self.added_categories) + "*"
										self.bot.sendMessage(chat_id, text= toSend, reply_markup = {'keyboard': self.main_keyboard},parse_mode= 'Markdown')
									else:
										toSend = "Tutto impostato con successo:\nCategorie del negozio: *" + str(self.added_categories) + "*\nPosizione del negozio: *" + str(self.myLocation) + "*."
										self.bot.sendMessage(chat_id, text= toSend, reply_markup = ReplyKeyboardRemove(),parse_mode= 'Markdown')
								else:
									self.bot.sendMessage(chat_id, text=self.category_error_message, reply_markup = {'keyboard': self.main_keyboard},parse_mode= 'Markdown')
							elif chat_message == self.other_categories_button:
								self.added_categories.append(chat_message)
								self.is_set_categoria = True
								self.bot.sendMessage(chat_id, text=self.category_error_message, reply_markup = {'keyboard': self.main_keyboard},parse_mode= 'Markdown')
							if not self.is_set_categoria:
								if chat_message not in self.added_categories:
									if chat_message != self.stop_button:
										self.bot.sendMessage(chat_id, text="Sei sicuro di voler aggiungere la categoria *" + chat_message + "*?", reply_markup={'keyboard': self.yes_no_keyboard},parse_mode= 'Markdown')
										self.yes_no_step = (True, chat_message)
								else:
									self.bot.sendMessage(chat_id, text="Categoria di " + chat_message + " già aggiunta.", reply_markup={'keyboard': self.main_keyboard},parse_mode= 'Markdown')
						else:
							self.bot.sendMessage(chat_id, text=self.main_message, reply_markup={'keyboard': self.main_keyboard},parse_mode= 'Markdown')

					# mi hai inviato la posizione
					elif content_type == 'location' and self.i_can_send_location and not self.is_set_location:
						self.myLocation = (latitude, longitude) = (msg['location']['latitude'], msg['location']['longitude'])
						toSend = "Posizione Registrata: *[" + str(latitude) + ", " + str(longitude) + "]*"
						
						if not self.is_set_categoria:
							self.main_keyboard = [[self.button_categoty]]
							self.bot.sendMessage(chat_id, text=toSend,parse_mode= 'Markdown', reply_markup={'keyboard': self.main_keyboard})
						else:
							toSend = "Tutto impostato con successo:\nCategorie del negozio: *" + str(self.added_categories) + "*\nPosizione del negozio: *" + str(self.myLocation) + "*."
							self.bot.sendMessage(chat_id, text=toSend, parse_mode= 'Markdown', reply_markup=ReplyKeyboardRemove())
						self.is_set_location = True
					#  Messaggio di benvenuto appena si accede al bot
					elif content_type == 'group_chat_created':
						toSend = "Benvenuto *" + first_name + "*  del negozio *" + group_title + "* sono EasyCollect, il bot che ti accompagnerà nella vendita online della tua attività.\n"
						toSend = toSend + "Attraverso i pannelli sottostanti potrai selezionare le categorie che descrivono il tuo negozio e condividerne la tua posizione con i clienti."
						self.bot.sendMessage(chat_id, text=toSend, reply_markup={'keyboard': self.main_keyboard},parse_mode= 'Markdown')
					elif content_type == 'new_chat_member':	pass
					#  Per qualsiasi altro caso inviami la tastiera
					else:
						self.bot.sendMessage(chat_id, text=self.main_message, reply_markup={'keyboard': self.main_keyboard},parse_mode= 'Markdown')
				elif self.is_set_categoria and self.is_set_location:
					toSend = "Tutto impostato con successo:\nCategorie del negozio: *" + str(self.added_categories) + "*\nPosizione del negozio: *" + str(self.myLocation) + "*."
					self.bot.sendMessage(chat_id, text=toSend, reply_markup = ReplyKeyboardRemove(),parse_mode= 'Markdown')


		except telepot.exception.BotWasKickedError as e:
			print("Sei stato buttato fuori dal gruppo")
		except Exception as e:
			if "No suggested keys" in str(e):	pass
			elif "title" in str(e):	pass
			print("Eccezione non gestita: " + str(e))

	def main(self):
		print("In Loop...")
		MessageLoop(self.bot, self.main_handler).run_as_thread()
		
		while True:	time.sleep(1)



if __name__ == '__main__':
	Bot = Bot()
	Bot.main()



