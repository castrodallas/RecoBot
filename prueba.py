import os
import telebot #Manejar la API de Telegram
from telebot.types import ReplyKeyboardMarkup #Para crear botones
from telebot.types import ReplyKeyboardRemove #Eliminar botonera
from telebot.types import ForceReply #Para citar mensajes

bot_token = os.environ['BOT_TOKEN']
bot = telebot.TeleBot(bot_token)
usuarios = {}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Hola! Soy Spotibot. Estoy aquí para ayudarte a armar una playlist personalizada de acuerdo a la canción que más te guste. Al finalizar te entregaré el link de la playlist creada :)")

@bot.message_handler(content_types=['text'])
def text_handler(message):
  if(message.text.startswith('/')):
    bot.send_message(message.chat.id, "Comando no disponible")
  else:
    bot.send_message(message.chat.id, "Hola")

#Te obliga a contestar el mensaje que te envía
@bot.message_handler(commands=['alta'])
def cmd_alta(message):
  #Pregunta el nombre de usuario
  markup = ForceReply()
  msg = bot.send_message(message.chat.id, "¿Cómo te llamas?", markup)
  bot.register_next_step_handler(msg, preguntar_edad)

def preguntar_edad(message):
  #Preguntar edad
  usuarios[message.chat.id]["Nombre"] = message.text
  markup = ForceReply()
  msg = bot.send_message(message.chat.id, "¿Cuántos años tienes?", reply_markup=markup)
  bot.register_next_step_handler(msg, preguntar_sexo)

def preguntar_sexo(message):
  #pregunta sexo del usuario
  if not message.text.isdigit():
    markup = ForceReply()
    msg = bot.send_message(message.chat.id, "ERROR \n¿Cuál es tu edad?")
    bot.register_next_step_handler(msg, preguntar_sexo)
  else:
    usuarios[message.chat.id]["Edad"] = message.text
    markup = ReplyKeyboardMarkup(
      one_time_keyboard=True, 
      input_field_placeholder="Pulsa un boton",
    resize_keyboard=True
    )
    markup.add("Hombre", "Mujer")
    msg = bot.send_message(message.chat.id, "¿Cuál es tu sexo?", reply_markup = markup)
    bot.register_next_step_handler(msg, guardar_datos_usuarios)

def guardar_datos_usuarios(message):
  if message.text != 'Hombre' and message.text != 'Mujer':
    msg = bot.send_message(message.chat.id, "ERROR \n¿Cuál es tu sexo?")
    bot.register_next_step_handler(msg, guardar_datos_usuarios)
  else:
    markup = ReplyKeyboardRemove()
    bot.send_message(message.chat.id, "Fin", reply_markup=markup)
    usuarios[message.chat.id]["Sexo"] = message.text
    print(usuarios)

#MAIN
if __name__ == '__main__':
  #setear los comandos
  bot.set_my_commands([
    telebot.types.BotCommand("/start", "Da la bienvenida"),
    telebot.types.BotCommand("/ayuda", "Proporciona ayuda")
  ])

"""
texto-html = '<b>NEGRITA</b>'
texto-html = '<i>CURSIVA</i>'
texto-html = '<u>SUBRAYADO</u>'
texto-html = '<s>TACHADO</s>'
texto-html = '<code>MONOESPACIADO</code>'
texto-html = '<span class='tg-spoiler'>SPOILER</spoiler>'
texto-html = '<a href='link'>LINK</a>'

bot.send_message(message.chat.id, "Hola", parse_mode='html')

para deshabilitar la vista previa de los links:
bot.send_message(message.chat.id, "Hola", parse_mode='html', disable_web_page_preview = True)
"""

