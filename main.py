# This is a sample Python script.
import concurrent
import os
import re
from datetime import datetime, timedelta
import time

import psycopg2
import schedule as schedule
import telebot
from telebot import types
from authorization import autorizationSpot
from messageUtils import messageUtils
from spotifyManager import spotifyManager
from dotenv import load_dotenv
from apscheduler.schedulers.blocking import BlockingScheduler
import threading
load_dotenv()


main_url = "http://bitesaitzz.pythonanywhere.com"
BOT_TOKEN = str(os.getenv("BOT_TOKEN"))
CLIENT_ID = str(os.getenv("CLIENT_ID"))
ADMIN_ID = str(os.getenv("ADMIN_ID"))
CLIENT_SECRET = str(os.getenv("CLIENT_SECRET"))
bot = telebot.TeleBot(BOT_TOKEN)
DATABASE_URL = os.environ['DATABASE_URL']


authSp = autorizationSpot()
messageUtils = messageUtils()
sm = spotifyManager()
user_states = {}
SIZE = 0


song_of_the_day = None


main_keyboard = telebot.types.ReplyKeyboardMarkup(True)
main_keyboard.row('/main')
main_keyboard.row('/options')


functions_keyboard = telebot.types.ReplyKeyboardMarkup(True)
functions_keyboard.row('/top_artists', '/top_tracks')
functions_keyboard.row('/recomendation', '/recently_played')
functions_keyboard.row('/listen_activity', '/song_of_the_day')
functions_keyboard.row('/options')


@bot.message_handler(commands=['list_login'])
def list(message):
    print(ADMIN_ID)
    if message.from_user.id != ADMIN_ID:
        bot.send_message(message.chat.id, "You have no rights to do this", reply_markup=main_keyboard)
        return
    connection = psycopg2.connect(DATABASE_URL, sslmode='require')
    cur = connection.cursor()
    cur.execute('SELECT * FROM users')
    users = cur.fetchall()
    info = 'List login:'
    for el in users:
        info += f'\nNAME: {el[1]}\n\tUSERNAME: {el[2]}\n\tID: {el[3]}\n\tEXPIRES IN: {el[6]}\n'
    cur.close()
    connection.close()
    bot.send_message(message.chat.id, info, reply_markup=main_keyboard)
@bot.message_handler(commands=['list_access'])
def list2(message):
    if message.from_user.id != ADMIN_ID:
        bot.send_message(message.chat.id, "You have no rights to do this", reply_markup=main_keyboard)
        return
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cur = conn.cursor()
    cur.execute('SELECT * FROM users_access')
    users = cur.fetchall()
    info = 'List access:'
    for el in users:
        info += f'\nNAME: {el[2]}\n\tID: {el[1]}\n\tEMAIL: {el[3]}\n'
    cur.close()
    conn.close()
    bot.send_message(message.chat.id, info, reply_markup=main_keyboard)
@bot.message_handler(commands=['list_listened'])
def list3(message):
    if message.from_user.id != ADMIN_ID:
        bot.send_message(message.chat.id, "You have no rights to do this", reply_markup=main_keyboard)
        return

    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cur = conn.cursor()
    cur.execute('SELECT * FROM users_listened')
    users = cur.fetchall()
    info = 'List access:'
    for el in users:
        info += f'\n{el[0]}\n{el[1]}\n{el[2]}\n'
    cur.close()
    conn.close()
    bot.send_message(message.chat.id, info, reply_markup=main_keyboard)
@bot.message_handler(commands=['main'])
def main(message):
    if user_states.get(message.chat.id) == 'main':
        return
    user_states[message.from_user.id] = 'main'

    #add check if is in db
    if(authSp.checkIfUser(message.from_user.id) == False):
        print('not user' + str(message.from_user.id))
        authSp.createDB()
        authSp.add_user(message)
        user_states[message.from_user.id] = 'none'
        main(message.from_user.id)
        return


    if (authSp.checkIfAccess(message.chat.id) == False):
        bot.send_message(message.chat.id, f'Hi, {message.from_user.first_name} First of all you should register your email,'
                                          f' which connected to spotify. /email', reply_markup=main_keyboard)
        return
    if (authSp.checkIfLogin(message.chat.id) == False):
        bot.send_message(message.chat.id, "You should login now /login")
        return

    sm.get_currently_playing(message, message.chat.id)
    bot.send_message(message.chat.id, 'Choose what u want to see', reply_markup=functions_keyboard)
    user_states[message.from_user.id] = 'none'
@bot.message_handler(commands=['clear_all'])
def clear(message):
    if message.from_user.id != ADMIN_ID:
        bot.send_message(message.chat.id, "You have no rights to do this")
        return
    authSp.deleteListened()
   ## authSp.deleteWeekListened()
    authSp.deleteAccess()
    authSp.deleteData()
    bot.send_message(message.chat.id, "All users access deleted", reply_markup=main_keyboard)
@bot.message_handler(commands=['clear_users_access'])
def clear_users_access(message):
    if message.from_user.id != ADMIN_ID:
        bot.send_message(message.chat.id, "You have no rights to do this")
        return
    authSp.deleteAccess()
    bot.send_message(message.chat.id, "Users access deleted", reply_markup=main_keyboard)
@bot.message_handler(commands=['clear_users_data'])
def clear_users_data(message):
    if message.from_user.id != ADMIN_ID:
        bot.send_message(message.chat.id, "You have no rights to do this")
        return
    authSp.deleteData()
    bot.send_message(message.chat.id, "Users data deleted", reply_markup=main_keyboard)
@bot.message_handler(commands=['clear_users_listened'])
def clear_users_listened(message):
    if message.from_user.id != ADMIN_ID:
        bot.send_message(message.chat.id, "You have no rights to do this")
        return
    authSp.deleteListened()
    bot.send_message(message.chat.id, "Users listened deleted", reply_markup=main_keyboard)
@bot.message_handler(commands=['clear_users_listened_weekly'])
def clear_users_weekly_listened(message):
    if message.from_user.id != ADMIN_ID:
        bot.send_message(message.chat.id, "You have no rights to do this")
        return
    authSp.deleteWeekListened()
    bot.send_message(message.chat.id, "Users listened weekly  deleted", reply_markup=main_keyboard)

@bot.message_handler(commands=['delete_tables'])
def delete_tables(message):
    if message.from_user.id != ADMIN_ID:
        bot.send_message(message.chat.id, "You have no rights to do this")
        return
    authSp.deleteTables()
    bot.send_message(message.chat.id, "Tables deleted", reply_markup=main_keyboard)
@bot.message_handler(commands=['recently_played'])
def recently_played(message):
    if user_states.get(message.chat.id) == 'recently_played':
        return
    user_states[message.from_user.id] = 'recently_played'
    type = 'recently_played'
    get_number_top(message, None, type)
@bot.message_handler(commands= ['recomendation'])
def recomendation(message):
    if user_states.get(message.chat.id) == 'recomendation':
        return
    user_states[message.from_user.id] = 'recomendation'
    if (authSp.checkIfLogin(message.from_user.id) == False):
        bot.send_message(message.chat.id, "You should login first")
        return
    keyboard = telebot.types.ReplyKeyboardMarkup(True)
    keyboard.row('artists', 'tracks')
    keyboard.row('cancel')
    bot.send_message(message.chat.id, "Choose type of recomendation", reply_markup=keyboard)
    bot.register_next_step_handler(message, get_recomendation_type)
@bot.message_handler(commands=['top_artists'])
def top_artists(message):
    if user_states.get(message.chat.id) == 'top_artists':
        return
    user_states[message.from_user.id] = 'top_artists'
    if (authSp.checkIfLogin(message.from_user.id) == False):
        bot.send_message(message.chat.id, "You should login first")
        return
    keyboard = telebot.types.ReplyKeyboardMarkup(True)
    keyboard.row('month', 'half year', 'all time')
    keyboard.row('cancel')
    bot.send_message(message.chat.id, "Choose time range", reply_markup=keyboard)
    bot.register_next_step_handler(message, get_time_range, 'artists')
@bot.message_handler(commands=['top_tracks'])
def top_tracks(message):
    if user_states.get(message.chat.id) == 'top_tracks':
        return
    user_states[message.from_user.id] = 'top_tracks'
    if (authSp.checkIfLogin(message.from_user.id) == False):
        bot.send_message(message.chat.id, "You should login first")
        return
    keyboard = telebot.types.ReplyKeyboardMarkup(True)
    keyboard.row('month', 'half year', 'all time')
    keyboard.row('cancel')
    bot.send_message(message.chat.id, "Choose time range", reply_markup=keyboard)
    bot.register_next_step_handler(message, get_time_range, 'tracks')
@bot.message_handler(commands=['create_db'])
def create_db(message):
    if message.from_user.id != ADMIN_ID:
        bot.send_message(message.chat.id, "You have no rights to do this")
        return
    authSp.createDB()
    bot.send_message(message.chat.id, "DB created", reply_markup=main_keyboard)
@bot.message_handler(commands=['start'])
def start_message(message):
    if user_states.get(message.chat.id) == 'start':
        return
    user_states[message.from_user.id] = 'start'
    authSp.createDB()

    #add_user(message)
    authSp.add_user(message)
    if (authSp.checkIfLogin(message.from_user.id) == True):
        bot.send_message(message.chat.id, f'{message.from_user.first_name} U are already logged in!')
        main(message)
        return
    if (authSp.checkIfAccess(message.from_user.id) == False):
        bot.send_message(message.chat.id, f'Hi, {message.from_user.first_name} First of all you should give your email, '
                                          f'which connected to spotify. Please', reply_markup=main_keyboard)
        bot.register_next_step_handler(message, get_email)
    else:
        bot.send_message(message.chat.id, f'Now you should login!')

        keyboard = telebot.types.ReplyKeyboardMarkup(True)
        keyboard.row('/login')
        keyboard.row('/options')
        bot.send_message(message.chat.id, 'Click to login', reply_markup=keyboard)
@bot.message_handler(commands=['email'])
def email(message):
    if user_states.get(message.chat.id) == 'email':
        return
    user_states[message.from_user.id] = 'email'
    bot.send_message(message.chat.id, "Enter your email", reply_markup=main_keyboard)
    bot.register_next_step_handler(message, get_email)
    return
@bot.message_handler(commands=['login'])
def login(message):
    if user_states.get(message.chat.id) == 'login':
        return
    user_states[message.from_user.id] = 'login'
    if(authSp.checkIfAccess(message.from_user.id) == False):
        bot.send_message(message.chat.id, "You should give your email first", reply_markup=main_keyboard)
        bot.register_next_step_handler(message, get_email)
        return
    authSp.delete_cache(message.from_user.id)
    username_id = message.from_user.id
    redirect_uri = f"{main_url}?chatid={message.chat.id}&client_id={CLIENT_ID}"
    keyboard = types.InlineKeyboardMarkup()
    url_button = types.InlineKeyboardButton(text="Open Link", url=redirect_uri)
    keyboard.add(url_button)
    bot.send_message(message.chat.id, "Click the button to open the link", reply_markup=keyboard)
    keyboard = telebot.types.ReplyKeyboardMarkup(True)
    keyboard.row('Continue')
    message_temp = bot.send_message(message.chat.id, 'You should get code and click "Continue"', reply_markup=keyboard)
    bot.register_next_step_handler(message_temp, get_code, message_temp.message_id, username_id)

@bot.message_handler(commands=['add_email'])
def add_new_account(message):
    if message.from_user.id == ADMIN_ID:
        bot.send_message(message.chat.id, "Enter username id email")
        #bot.register_next_step_handler(message, add_id)
        bot.register_next_step_handler(message, get_data_of_new_account)
    else:
        bot.send_message(message.chat.id, "You have no rights to do this")
def switch_account_final(message):
    if user_states.get(message.chat.id) == 'switch_account_final':
        return
    user_states[message.from_user.id] = 'switch_account_final'
    if message.text.lower() == 'yes':
        authSp.delete_cache(message.from_user.id)
        authSp.deleteFromAccess(message.from_user.id)
        authSp.deleteFromLoggined(message.from_user.id)
        bot.send_message(message.chat.id, "You switched the account. Now you can login on another email")
        email(message)
    elif message.text.lower() == 'no':
        bot.send_message(message.chat.id, "You didn't switch the account", reply_markup=main_keyboard)
    elif message.text.lower() == 'cancel':
        main(message)
    else:
        bot.send_message(message.chat.id, "Something went wrong. Please try again", reply_markup=main_keyboard)
@bot.message_handler(commands=['contact'])
def contact(message):
    if user_states.get(message.chat.id) == 'contact':
        return
    user_states[message.from_user.id] = 'contact'
    bot.send_message(message.chat.id, "Contact with admin: @bitesait", reply_markup=main_keyboard)
    return
@bot.message_handler(commands=['about'])
def about(message):
    if user_states.get(message.chat.id) == 'about':
        return
    user_states[message.from_user.id] = 'about'
    bot.send_message(message.chat.id, "This is a bot that allows you to see your top artists and tracks, as well as get "
                                      "recommendations based on your preferences", reply_markup=main_keyboard)
    return
@bot.message_handler(commands=['options'])
def options(message):
    if user_states.get(message.chat.id) == 'options':
        return
    user_states[message.from_user.id] = 'options'
    keyboard = telebot.types.ReplyKeyboardMarkup(True)
    keyboard.row('/login', '/email', '/about')
    keyboard.row('/switch_account')
    keyboard.row('/contact')
    keyboard.row('/cancel')
    bot.send_message(message.chat.id, 'Here you can switch your account. Remember that first you should access on your '
                                      'email and only then can login on THIS email. ', reply_markup=keyboard)
    return
@bot.message_handler(commands=['switch_account'])
def switch_account(message):
    if user_states.get(message.chat.id) == 'switch_account':
        return
    user_states[message.from_user.id] = 'switch_account'
    if (authSp.checkIfAccess(message.from_user.id) == False):
        bot.send_message(message.chat.id, "You should give your email first", reply_markup=main_keyboard)
        bot.register_next_step_handler(message, get_email)
        return
    if (authSp.checkIfLogin(message.from_user.id) == False):
        bot.send_message(message.chat.id, "You should login first", reply_markup=main_keyboard)
        return
    keyboard = telebot.types.ReplyKeyboardMarkup(True)
    keyboard.row('Yes', 'No', 'Cancel')
    bot.send_message(message.chat.id, "Are you sure you want to switch the account?", reply_markup=keyboard)
    bot.register_next_step_handler(message, switch_account_final)

def weekly_stats():
    all_users = authSp.get_all_users()
    for user in all_users:
        user_id = user[0]
        tracks_data = authSp.get_listened_weekly_tracks(user_id)
        tracks_data = sorted(tracks_data, key=lambda x: x[2], reverse=True)
        info_artists = 'Your weekly stats in Artists:\n'
        info_tracks = 'Your weekly stats in Tracks:\n'
        top_tracks, top_artists, top_artist_url, top_track_url = analize_weekly(user_id, tracks_data)
        if(top_tracks == "You have no listened tracks" or top_artists == None):
            continue
        info_artists += top_artists
        info_tracks += top_tracks
        if (top_artist_url != None):
            messageUtils.send_long_message_with_photo(user_id, info_artists, top_artist_url)
        if (top_track_url != None):
            messageUtils.send_long_message_with_photo(user_id, info_tracks, top_track_url)
    authSp.deleteWeekListened()


def analize_weekly(user_id, tracks_data):
    top_tracks = ''
    top_artists = ''
    top_artist_url = ''
    top_track_url = None
    artists = {}
    if (len(tracks_data) <= 1):
        return "You have no listened tracks", None, None, None

    tracks_data = sorted(tracks_data, key=lambda x: x[2], reverse=True)


    #split tracks_data into parts by 50 valles
    parts = [tracks_data[i:i + 50] for i in range(0, len(tracks_data), 50)]
    it = 1
    sp_token = authSp.get_sp_token(user_id)
    for part in parts:
        track_ids, play_counts = [track[1] for track in part if track[1] != '0'], [track[2] for track in part if track[1] != '0']
        tracks_info, track_url, artists_list = sm.getInfoByIds(track_ids, sp_token, it==1)
        if top_track_url == None:
            top_track_url = track_url
        if tracks_info == None:
            return "You have no listened tracks", None, None, None
        for track_info, play_count in zip(tracks_info, play_counts):
            # names_before_dash = track_info.split(" - ")[0]
            # artists_list = names_before_dash.split(", ")
            if play_count == 1:
                track_info = f"{it}. {track_info} - {play_count} time\n"
            else:
                track_info = f"{it}. {track_info} - {play_count} times\n"
            top_tracks += track_info
            it = it + 1
        for artist in artists_list:
            if artist in artists:
                artists[artist] += 1
            else:
                artists[artist] = 1

    sorted_artists = sorted(artists.items(), key=lambda item: item[1], reverse=True)
    top_artists_sort = sorted_artists[:10]
    it = 1
    for artist in top_artists_sort:
        if(artist[1] == 1):
            artist_info = f"{it}. [{artist[0]} - {artist[1]} time\n"
        else:
            artist_info = f"{it}. {artist[0]} - {artist[1]} times\n"
        it += 1
        top_artists += artist_info+"\n"
        if it == 11:
            break
    if(top_artists_sort == []):
        return "You have no listened tracks", None, None, None
    top_artist = top_artists_sort[0][0]
    sp = authSp.get_sp_token(user_id)
    if sp == None:
        return "You have no listened tracks", None, None
    result = ''
    pattern = r'\[(.*?)\]'  # Regular expression to match text inside square brackets
    matches = re.findall(pattern, str(top_artist))
    if matches:
        result = matches[0]
    results = sp.search(q='artist:' + result, type='artist')
    if results['artists']['items']:
        artist_id = results['artists']['items'][0]['id']
        artist_info = sp.artist(artist_id)
        if artist_info['images']:
            top_artist_url = artist_info['images'][0]['url']
        else:
            top_artist_url = "No photo available for this artist."
    else:
        top_artist_url = "Artist not found."
    #top_artist_url = first_artist['images'][0]['url']
    return top_tracks, top_artists, top_artist_url, top_track_url


@bot.message_handler(commands=['listen_activity'])
def listen_activity(message):
    if user_states.get(message.chat.id) == 'listen_activity':
        return
    user_states[message.from_user.id] = 'listen_activity'
    bot.send_message(message.chat.id, "Wait a moment, we are preparing your listen activity...")
    tracks_data = authSp.get_listened_tracks(message.chat.id)
    if(len(tracks_data) <= 1):
        bot.send_message(message.chat.id, "You have no listened tracks", reply_markup=main_keyboard)
        return
    info_artists = 'Your listened stats in Artists:\n'
    info_tracks = 'Your listened stats in Tracks:\n'
    top_tracks, top_artists, top_artist_url, top_track_url = analize_weekly(message.chat.id, tracks_data)
    info_artists += top_artists
    info_tracks += top_tracks
    if (top_artist_url != None):
        messageUtils.send_long_message_with_photo(message.chat.id, info_artists, top_artist_url)
    if (top_track_url != None):
        messageUtils.send_long_message_with_photo(message.chat.id, info_tracks, top_track_url)


@bot.message_handler(commands=['do_sql_request'])
def sql_request(message):
    if message.from_user.id != ADMIN_ID:
        bot.send_message(message.chat.id, "You have no rights to do this", reply_markup=main_keyboard)
        return
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cur = conn.cursor()
    print(message.text[16:])
    cur.execute(message.text[16:])
    conn.commit()
    cur.close()
    conn.close()
    bot.send_message(message.chat.id, "Request done", reply_markup=main_keyboard)


@bot.message_handler(commands=['song_of_the_day'])
def song_of_the_day_function(message):
    if user_states.get(message.chat.id) == 'song_of_the_day':
        return
    user_states[message.from_user.id] = 'song_of_the_day'
    if song_of_the_day is None:
        get_song_of_the_day()
    sp_token = authSp.get_sp_token(message.chat.id)
    info, track_photo = sm.getInfoById(message.chat.id, song_of_the_day, sp_token)
    info = f"Song of the day:\n{info}"
    if (track_photo != None and info != None):
        messageUtils.send_long_message_with_photo(message.chat.id, info, track_photo)
    else:
        bot.send_message(message.chat.id, "Song of the day is not available now. Try later", reply_markup=main_keyboard)


@bot.message_handler(commands=['erika'])
def erika_currently_listen(message):
    if message.chat.id != ADMIN_ID:
        return
    if sm.get_currently_playing(message, '904522858') == False:
        bot.send_message(message.chat.id, "Erika is not listening now")
    return

def get_recomendation_type(message):
    if user_states.get(message.chat.id) == 'get_recomendation_type':
        return
    user_states[message.from_user.id] = 'get_recomendation_type'
    if (message.text.lower() == 'cancel'):
        main(message)
        return
    if (message.text.lower() == 'artists'):
        get_recomendation_artists(message)
    elif (message.text.lower() == 'tracks'):
        get_recomendation_tracks(message)
    else:
        bot.send_message(message.chat.id, "Something went wrong. Please try again")
        recomendation(message)
        return
def get_recomendation_artists(message):
    if user_states.get(message.chat.id) == 'get_recomendation_artists':
        return
    user_states[message.from_user.id] = 'get_recomendation_artists'
    keyboard = telebot.types.ReplyKeyboardMarkup(True)
    keyboard.row('last 30 days', 'last 6 months', 'all time')
    keyboard.row('last added')
    keyboard.row('cancel')
    type = 'artists'
    bot.send_message(message.chat.id, "Chose the basis for recomendation", reply_markup=keyboard)
    bot.register_next_step_handler(message, get_recomendations_basis, type)
def get_recomendation_tracks(message):
    if user_states.get(message.chat.id) == 'get_recomendation_tracks':
        return
    user_states[message.from_user.id] = 'get_recomendation_tracks'
    keyboard = telebot.types.ReplyKeyboardMarkup(True)
    keyboard.row('last 30 days', 'last 6 months', 'all time')
    keyboard.row('last added')
    keyboard.row('cancel')
    type = 'tracks'
    bot.send_message(message.chat.id, "Chose the basis for recomendation", reply_markup=keyboard)
    bot.register_next_step_handler(message, get_recomendations_basis, type)
def get_recomendations_basis(message, type):
    if user_states.get(message.chat.id) == 'get_recomendations_basis':
        return
    user_states[message.from_user.id] = 'get_recomendations_basis'
    if (message.text.lower() == 'cancel'):
        main(message)
        return
    if (message.text.lower() == 'last 30 days'):
        time_range = 'short_term'
    elif (message.text.lower() == 'last 6 months'):
        time_range = 'medium_term'
    elif (message.text.lower() == 'all time'):
        time_range = 'long_term'
    elif (message.text.lower() == 'last added'):
        time_range = 'last_added'
    else:
        bot.send_message(message.chat.id, "Something went wrong. Please try again")
        recomendation(message)
        return
    if type == 'artists':
        sm.get_recomendation_artists_by_basis(message, time_range)
    elif type == 'tracks':
       recomendation_data =  sm.get_recomendation_tracks_by_basis(message, time_range)
       info = 'Recomendation tracks for you:\n'
       additional_info, track_photo = messageUtils.show_songs_artists(recomendation_data, 'track')
       info += additional_info
       messageUtils.send_long_message_with_photo(message.chat.id, info, track_photo)
       keyboard = telebot.types.ReplyKeyboardMarkup(True)
       keyboard.row('add playlist', 'cancel')
       bot.reply_to(message, "You also can add playlist with these songs to your library!", reply_markup=keyboard)
       bot.register_next_step_handler(message, sm.add_playlist, recomendation_data)
    else:
        bot.send_message(message.chat.id, "Something went wrong. Contact admin")
        main(message)
        return
def get_time_range(message, type):
    if user_states.get(message.chat.id) == 'get_time_range':
        return
    user_states[message.from_user.id] = 'get_time_range'
    if (message.text.lower() == 'cancel'):
        main(message)
        return
    if (message.text.lower() == 'month'):
        time_range = 'short_term'
    elif (message.text.lower() == 'half year'):
        time_range = 'medium_term'
    elif (message.text.lower() == 'all time'):
        time_range = 'long_term'
    else:
        bot.send_message(message.chat.id, "Something went wrong. Please try again")
        top_artists(message)
        return
    get_number_top(message, time_range, type)
def get_number_top(message, time_range, type):
    if user_states.get(message.chat.id) == 'get_number_top':
        return
    user_states[message.from_user.id] = 'get_number_top'
    keyboard = telebot.types.ReplyKeyboardMarkup(True)
    keyboard.row('5', '10', '25', '50')
    keyboard.row('cancel')
    if type == 'artists':
        bot.send_message(message.chat.id, "Choose number of artists", reply_markup=keyboard)
    elif type == 'tracks' or type == 'recently_played':
        bot.send_message(message.chat.id, "Choose number of tracks", reply_markup=keyboard)
    else:
        bot.send_message(message.chat.id, "Something went wrong. Contact admin")
        main(message)
        return
    bot.register_next_step_handler(message, check_get_number_top, time_range, type)
def check_get_number_top(message, time_range, type):
    if user_states.get(message.chat.id) == 'check_get_number_top':
        return
    user_states[message.from_user.id] = 'check_get_number_top'
    if (message.text.lower() == 'cancel'):
        main(message)
        return
    number = message.text

    if not number.isdigit():
        bot.send_message(message.chat.id, "Please enter number")
        get_number_top(message, time_range, type)
        return
    if int(number) < 1 or int(number) > 50:
        bot.send_message(message.chat.id, "Please enter number from 1 to 50")
        get_number_top(message, time_range, type)
        return
    number = int(number)
    if type == 'artists':
        sm.get_top_artists(message, time_range, number)
    elif type == 'tracks':
        sm.get_top_tracks(message, time_range, number)
    elif type == 'recently_played':
        sm.get_recently_played(message, number)
    else:
        bot.send_message(message.chat.id, "Something went wrong. Contact admin")
        main(message)
        return
def get_email(message):
    email = message.text
    keyboard = telebot.types.ReplyKeyboardMarkup(True)
    keyboard.row('Yes', 'No', 'Cancel')
    keyboard.row('/options')
    bot.send_message(message.chat.id, f'Your email is {email}. Right?', reply_markup=keyboard)
    bot.register_next_step_handler(message, send_email_to_admin, email)
def send_email_to_admin(message, email):
    keyboard = telebot.types.ReplyKeyboardMarkup(True)
    keyboard.row('/login')
    if (authSp.checkIfEmail(email) == True):
        authSp.add_access_db(message.chat.id, email)
        bot.send_message(message.chat.id, 'This email is already in use. You can login with it', reply_markup=keyboard)
        login(message)
        return

    if message.text.lower() == 'yes':
        bot.send_message(ADMIN_ID, f'New user ({message.from_user.username} with ID({message.chat.id}) with email: {email} '
                                   f'wants to login. Use /add_email')
        bot.send_message(ADMIN_ID, f'{message.from_user.username} {message.chat.id} {email}')
        bot.send_message(message.chat.id, "Your application has been sent. Due to Spotify's own limitations on the number "
                                          "of users, please wait for your email to be approved. You will receive a message "
                                          "asap", reply_markup=keyboard)
        return
    elif message.text.lower() == 'no':
        bot.send_message(message.chat.id, 'Enter your email again', reply_markup=main_keyboard)
        bot.register_next_step_handler(message, get_email)
    else:
        if (authSp.checkIfAccess(message.chat.id) == False):
            bot.send_message(message.chat.id, f'Hi, {message.from_user.first_name} First of all you should give your email, '
                                              f'which connected to spotify. Please', reply_markup=main_keyboard)
            bot.register_next_step_handler(message, email)
        elif (authSp.checkIfLogin(message.chat.id) == False):
            login(message)
        else:
            main(message)

def get_code(message, message_id, username_id):
    chat_id = message.chat.id
    message_id = message_id + 1

    message = bot.forward_message(chat_id, chat_id, message_id)

    if message.text.split(' ')[0] != 'Code:':
        bot.send_message(chat_id, 'Something went wrong! Please repeat /login"')
        # bot.register_next_step_handler(message, login, message_id, username_id)
        return
    code = message.text.split(' ')[1]
    sp_oauth = authSp.create_spoty_oauth(message.chat.id)
    token_info = sp_oauth.get_cached_token()
    if token_info is not None:
        authSp.save_token(token_info, username_id)
    else:
        token_info = sp_oauth.get_access_token(code)
        authSp.save_token(token_info, username_id)
    # bot.delete_message(chat_id, message.message_id)
    bot.delete_message(chat_id, message_id - 1)
    bot.delete_message(chat_id, message_id)
    bot.delete_message(chat_id, message.message_id)
    main(message)
    return
def get_data_of_new_account(message):
    #split message into 3 words
    words = message.text.split()
    if len(words) != 3:
        bot.send_message(message.chat.id, "Please enter correct data")
        return
    username = words[0]
    id = words[1]
    email = words[2]
    adding_account(message, username, id, email)
def adding_account(message, username, id, email):
    authSp.add_access_db(id, email)
    if (authSp.checkIfLogin(id) == True):
        authSp.deleteFromLoggined(id)
    bot.send_message(message.chat.id, f"Result of adding {username}: User added")
    bot.send_message(id, "Your email has been approved. Now you can /login")
    main(message)


def get_song_of_the_day():
    global song_of_the_day
    song_of_the_day=sm.song_of_the_day()
    print(f"{datetime.now()} -- get_song_of_the_day {str(song_of_the_day)}")

def check_change_size():
    global SIZE
    CHECK_SIZE = authSp.get_size_listened(ADMIN_ID)
    if (SIZE != CHECK_SIZE):
        bot.send_message(ADMIN_ID, f"Size of listened tracks changes from {SIZE} to {CHECK_SIZE}", reply_markup=main_keyboard)
        SIZE = CHECK_SIZE
        print(f"{datetime.now()} -- check_change_size {SIZE}")

@bot.message_handler()
def repeater(message):
    chat_id = message.chat.id
    if message.text.lower() == 'хуй':
        bot.reply_to(message, f'иди нахуй выблядина {message.from_user.first_name}', reply_markup=main_keyboard)
    elif message.text.lower()[0] == '/' or message.text.lower() == 'cancel':
        main(message)
    else:
        bot.send_message(message.chat.id, f'сам {message.text}', reply_markup=main_keyboard)

def run_schedule():
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__=='__main__':
    scheduler = BlockingScheduler()
    scheduler.add_job(sm.update_users_listened, 'cron', hour='0,3,6,9,12,15,18,21', minute=0)
    scheduler.add_job(weekly_stats, 'cron', hour=0, minute=1, day_of_week=4)
    scheduler.add_job(get_song_of_the_day, 'cron', hour=0, minute=2)
    scheduler_thread = threading.Thread(target=scheduler.start)
    scheduler_thread.start()

    while True:
        try:
            bot.polling(non_stop=True, interval=0)
            schedule.run_pending()
        except Exception as e:
            print(f"Error in main: {e}")
            print(BOT_TOKEN)
            time.sleep(5)
            continue
