#Se importan todas las librerías
import os
import requests #Peticiones de apis. Para cualquiera.
import telebot
from telebot.types import ForceReply #Para citar mensajes
from telebot.types import ReplyKeyboardMarkup #Para crear botones
from telebot.types import ReplyKeyboardRemove #Eliminar botonera

# - VARIABLES -
#En secrets aparecen los códigos ocultos, que no aparecen en otro replit por seguridad. Para que no te roben los datos.
#Variables de entorno.
client_id = os.environ['SPOTIFY_CLIENT_ID']
client_secret = os.environ['SPOTIFY_CLIENT_SECRET']
bot_token = os.environ['BOT_TOKEN']
usuarios = {}

def get_access_token(client_id, client_secret):
    url = 'https://accounts.spotify.com/api/token'
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    data = {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret
    }

    response = requests.post(url, headers=headers, data=data)

    if response.status_code == 200:
        token_data = response.json()
        access_token = token_data['access_token']
        return access_token
    else:
        return None

def search_track(access_token, nombre_cancion, artista_cancion): #Recibe el acces token de spotify, el nombre, y el artista ingresados por el usuario. El pedido de api también se hace con clave-valor.
    url = 'https://api.spotify.com/v1/search' #Se hace desde una url que te da la api. Por defecto.
    headers = {'Authorization': f'Bearer {access_token}'} #Esto también es por defecto, la autorización es nuestro acces token. Si no es correcto te devuelve error.
    params = {
        'q': f'track:{nombre_cancion} artist:{artista_cancion}',
        'type': 'track', #track porque estamos buscando canciones.
        'limit': 10 #límite de los resultados.
    } #Parámetros de las cosas que quiero buscar.

    response = requests.get(url, headers=headers, params=params) #traeme desde esta url, de headers, poneme lo que puse en la varible, y de params, lo mismo. 

    if response.status_code == 200: #Cada respuesta tiene un código númerico de status. Significa que se conectó bien a la api.
        data = response.json() #Formato especial. El jason :D. Es un código larguísimo que te devuelve.
        tracks = data['tracks']['items'] #Porque es un ítem adentro de otro ítem. Un montón de información, pero sólo nos interesa tracks y items.
        if not tracks: #Si no hay canciones, devuelve falso. O sea se conectó bien a la api, pero no hay resultados de búsqueda.
          return False
        else:
          return tracks
    else:
        return False

def get_recommendations(access_token, id_cancion):
    url = 'https://api.spotify.com/v1/recommendations'
    headers = {'Authorization': f'Bearer {access_token}'}
    params = {
      "limit": 30,
      'seed_tracks': f'{id_cancion}' 
    } #A partir de qué va a buscar las canciones. 

    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200: #Lo mismo que antes. 
        data = response.json()
        tracks = data['tracks']
        if not tracks:
          return False
        else:
          return tracks
    else:
        return False



# - PROGRAMA PRINCIPAL -

bot = telebot.TeleBot(bot_token) #token de Telegram que nos dio botfather
access_token = get_access_token(client_id, client_secret) #token de la App de Spotify con cuenta jueguete 
print("Bot corriendo...") #indicador de que está todo funcionando (en python)

# - CONFIG TELEGRAM 
#Le dice los comandos que va a utilizar telegram y breve descripción del comando.
#Botfather crea tu bot. 
bot.set_my_commands([
  telebot.types.BotCommand("/start", "Da la bienvenida"),
  telebot.types.BotCommand("/ayuda", "Proporciona ayuda"),
  telebot.types.BotCommand("/buscar", "Busca recomendaciones a partir de una canción")
])

#A partir de un arroba, las funciones que van abajo, son las funciones que le corresponden. 
@bot.message_handler(commands=['start'])
def send_welcome(message): #Maneja el comando start. Da la bienvenida.
    markup = ReplyKeyboardRemove()
    bot.reply_to(message, "Hola! Soy RecoBot y estoy diseñado para recomendarte canciones. \nEn base a la canción que elijas, te dare una lista de tracks similares que incluye su título, artista, álbum al que pertenece y link a Spotify. \nPara comenzar, simplemente escribí /buscar y luego ingresá el nombre de una canción. \nEscribí /ayuda si necesitas más instrucciones sobre cómo utilizarme!", reply_markup=markup) #reply es para responderle. 
  #Siempre recibe el parametro message. Mínimos tiene que tener dos.
  #Directamente se va a ejecutar automaticamente, no es necesario llamarlas.

@bot.message_handler(commands=['ayuda'])
def cmd_ayuda(message): #Maneja el comando ayuda.
  bot.send_message(message.chat.id, "<b><u>Instrucciones para utilizar RecoBot:</u></b>\n\n<b>1. Escribí /buscar:</b> Esto te permitirá ingresar el nombre de la canción que deseas utilizar como base para las recomendaciones.\n<b>2. Ingresá el nombre del artista:</b> ingresá el nombre del artista para que la búsqueda se concrete correctamente.\n<b>3. Elegí entre los resultados:</b> a partir de la lista de resultados basados en tu búsqueda, seleccioná con la botonera el número correspondiente al resultado que te interese.\n<b>4. Explorá las recomendaciones:</b> una vez que hayas seleccionado una canción, RecoBot te va a proporcionar una lista de tracks similares. Cada recomendación incluirá el título de la canción, el nombre del artista, el álbum al que pertenece y un enlace directo a Spotify para que puedas escucharla y agregarla a la playlist que quieras!\n<b>5. Disfrutá de la música!:</b> usa los enlaces proporcionados para explorar y disfrutar de las canciones recomendadas.\nRecordá que siempre podés escribir /ayuda si necesitas recordar estas instrucciones en cualquier momento.", parse_mode='html') #Mini tutorial de cómo funciona.

@bot.message_handler(commands=['buscar'])
def cmd_buscar(message): #Maneja el comando buscar.
  if not message.text: #Devuelve lo que el usuario me responde. Si el usuario no mandó nada, va a ver un false. Booleana!!
    bot.send_message(message.chat.id, "No entiendo lo que dices :(, busca en el comando /ayuda") #Mandame un mensaje al chat id, porque nunca va a ser el mismo id. Tiene que saber de alguna manera a qué chat.
  else:
    usuarios[message.chat.id] = {} #Diccionario. Ahí se define la variable vacía de usuarios. Un diccionario adentro de un diccionario. Asociar cada dato al id.
    markup = ForceReply() #Son maneras de responder los mensajes. Ese va a forzar que el usuario de una respuesta.
    msg = bot.send_message(message.chat.id, "Ingresa el nombre de la canción:", reply_markup=markup) #Lo que guardé en la variable. La variable msg, es la respuesta del usuario. 
    bot.register_next_step_handler(msg, preguntar_nombre) #Automaticamente, guarda el mensaje y guarda la función.

def preguntar_nombre(message): #Ese message, ahora es msg. Trabaja sobre el último valor. message = msg. Es tonto, no se acuerda.
  if not message.text: #Se hace lo mismo que arriba.
    markup = ForceReply()
    msg = bot.send_message(message.chat.id, "ERROR: Se debe ingresar un nombre.\nIngresa el nombre de la canción:", reply_markup=markup)
    bot.register_next_step_handler(msg, preguntar_nombre) #Es como un while, hasta que la persona no ingrese texto, va a seguir pidiendo lo mismo.
  else:
    usuarios[message.chat.id]["Nombre"] = message.text.strip().title() #Le va a sacar los espacios vacíos y todas las primeras letras en mayúsculas, porque así funciona la api de spotify. Hay que guardarlo en usuarios, sino se olvida.
    markup = ForceReply()
    msg = bot.send_message(message.chat.id, "Ingresa el nombre del artista:", reply_markup=markup) #Lo mismo que lo anterior, pero con el artista.
    bot.register_next_step_handler(msg, preguntar_artista) #Le paso el mensaje que respondió.

def preguntar_artista(message):
  if not message.text:
    markup = ForceReply()
    msg = bot.send_message(message.chat.id, "ERROR: Se debe ingresar un nombre.\nIngresa el nombre del artista:", reply_markup=markup)
    bot.register_next_step_handler(msg, preguntar_nombre)
  else:
    usuarios[message.chat.id]["Artista"] = message.text.strip().title() #Guarda dentro de la clave.
    bot.send_message(message.chat.id, "Buscando canción...") #Manda mensaje.
    tracks = search_track(access_token, usuarios[message.chat.id]["Nombre"], usuarios[message.chat.id]["Artista"]) #Función común y corriente, está arriba.
    if(not tracks): #Acá devuelve el mensaje si es que no hay resultados.
      bot.send_message(message.chat.id, f'No se encontraron canciones con el nombre {usuarios[message.chat.id]["Nombre"]} o el artista {usuarios[message.chat.id]["Artista"]}. Intentá nuevamente con el comando /buscar') 
    else:
      bot.send_message(message.chat.id, 'Estos son los resultados de tu búsqueda:')
      markup = ReplyKeyboardMarkup(
          one_time_keyboard=True, #Una vez que responda, los botones se van a ocultar.
          input_field_placeholder="Pulsa un boton", 
          resize_keyboard=True #Los botones por defecto, son gigantes, con esto, los hace más chicos.
      ) #Esos son botones
      for index, track in enumerate(tracks, start=1): #Por la cantidad de resultados que recibió. index para enumerar más fácil. Esto fue con ayudita :P. Recorre un por uno. También guarda uno por uno. 
        track_name = track['name'] #Devuelve un str. Es parte del json.
        artist_name = track['artists'][0]['name'] #Sólo el primer artista.
        album_name = track['album']['name']
        track_link = track['external_urls']['spotify'] #Eso es para el url del spotify.
        html = f'<b><u>{index}. {track_name}</u></b>\nArtista: {artist_name}\nAlbum: {album_name}\n<a href="{track_link}">Link a la canción</a>'
        bot.send_message(message.chat.id, html, parse_mode='html', disable_web_page_preview = True) #Este coso de html, es para que se vea más bonito, con las referencias indicadas por telegram. 
        #El parse_mode, es un parámetro por defecto del telebot, le aclaramos lo de html, sino lo imprime tal cual. 
        #Deshabilitamos la vista previa, porque se veía mal.
        markup.add(f"{index}") #Botón con número de indice. 10 botones con las 10 canciones. Para que el usuario toque el botón directamente. 
        
      usuarios[message.chat.id]["Tracks"] = tracks #Guardo dentro del diccionario, las canciones.
      msg = bot.send_message(message.chat.id, "¿Cuál es la canción que buscabas?", reply_markup = markup) #El método se lo paso con la "botonera".
      bot.register_next_step_handler(msg, buscar_recomendaciones) #Pasamos a buscar.

def buscar_recomendaciones(message):
  tracks = usuarios[message.chat.id]["Tracks"] #Se llama al diccionario dentro del diccionario.
  selected_track = tracks[int(message.text) - 1] #Necesito que me lo pase a un int. - 1 porque arranca en 0 en realidad.
  track_id = selected_track['id'] #Busca en base al id.
  usuarios[message.chat.id]["Cancion"] = track_id
  rec_tracks = get_recommendations(access_token, usuarios[message.chat.id]["Cancion"]) #Recomendaciones a partir de la canción. el get recommendations tiene un montón de características por defecto que vienen con la api.
  #Nueva variable.
  markup = ReplyKeyboardRemove() #Elimina la botonera.
  bot.send_message(message.chat.id, 'Estas son las recomendaciones que busqué:', reply_markup=markup) 
  for index, song in enumerate(rec_tracks, start=1): #Lo mismo que antes.
    track_name = song['name']
    artist_name = song['artists'][0]['name']
    album_name = song['album']['name']
    track_link = song['external_urls']['spotify']
    html = f'<b><u>{index}. {track_name}</u></b>\nArtista: {artist_name}\nAlbum: {album_name}\n<a href="{track_link}">Link a la canción</a>'
    bot.send_message(message.chat.id, html, parse_mode='html', disable_web_page_preview = True) #Lo mimso con lo de html, para que quede bien. 
  bot.send_message(message.chat.id, "Fue un placer ayudarte a descubrir nuevas canciones! Ojala que te hayan gustado <3\nRecordá que si queres volver a utilizarme, simplemente escribí el comando /buscar.\nSaludos!")
     
bot.infinity_polling() #Está todo el tiempo buscando respuestas nuevas. Se tiene que usar si o si. 