import os
import random
import requests
import telebot
from spotipy import SpotifyException
from datetime import datetime, timedelta
import time



user_states = {}
from authorization import autorizationSpot
from messageUtils import messageUtils
from dotenv import load_dotenv
load_dotenv()
BOT_TOKEN = str(os.getenv("BOT_TOKEN"))
ADMIN_ID = str(os.getenv("ADMIN_ID"))
bot = telebot.TeleBot(BOT_TOKEN)

authSp = autorizationSpot()
messageUtils = messageUtils()

main_keyboard = telebot.types.ReplyKeyboardMarkup(True)
main_keyboard.row('/main')
main_keyboard.row('/options')
functions_keyboard = telebot.types.ReplyKeyboardMarkup(True)
functions_keyboard.row('/top_artists', '/top_tracks')
functions_keyboard.row('/recomendation', '/recently_played')
functions_keyboard.row('/listen_activity', '/song_of_the_day')
functions_keyboard.row('/options')

class spotifyManager:
    def get_top_artists(self, message, time_range, number):
        if user_states.get(message.chat.id) == 'get_top_artists':
            return
        print(f"{datetime.now()} - Getting top artists by {message.from_user.id} {message.from_user.username}")
        user_states[message.from_user.id] = 'get_top_artists'
        sp = authSp.get_sp_token(message.from_user.id)
        try:
            user_top_read = sp.current_user_top_artists(limit=number, time_range=time_range, offset=0)
            # bot.send_message(message.chat.id, "Your top artists: ")
            time_range_readable = ''
            if time_range == 'short_term':
                time_range_readable = 'month'
            elif time_range == 'medium_term':
                time_range_readable = 'half year'
            elif time_range == 'long_term':
                time_range_readable = 'all time'
            info = f'Your top {number} artists for {time_range_readable}:\n\n'
            additional_info, artist_photo = messageUtils.show_songs_artists(user_top_read['items'], 'artist_top')
            info += additional_info
            messageUtils.send_long_message_with_photo(message.chat.id, info, artist_photo)
        except SpotifyException as e:
            if e.http_status == 403 and 'User not registered in the Developer Dashboard' in str(e):
                bot.send_message(message.chat.id,
                                 "Error: User not registered in the Dashboard(your email is not approved). Please change your /email")
            else:
                bot.send_message(message.chat.id, f"An error occurred: {e}")

    def get_recomendation_artists_by_basis(self, message, time_range):
        if user_states.get(message.chat.id) == 'get_recomendation_artists_by_basis':
            return
        print(f"{datetime.now()} - Getting recomendation artists by basis by {message.from_user.id} {message.from_user.username}")
        user_states[message.from_user.id] = 'get_recomendation_artists_by_basis'
        sp = authSp.get_sp_token(message.from_user.id)
        try:
            if time_range == 'last_added':
                user_top_read = sp.current_user_saved_tracks(limit=10, offset=0)
                artists_id = []
                for track in user_top_read['items']:
                    for artist in track['track']['artists']:
                        artists_id.append(artist['id'])
            else:
                user_top_read = sp.current_user_top_artists(limit=10, time_range=time_range, offset=0)
                artists_id = []
                for artist in user_top_read['items']:
                    artists_id.append(artist['id'])
            recomendation_data = []
            for i in range(0, len(artists_id), 5):
                if i + 5 < len(artists_id):
                    artists_id_part = artists_id[i:i + 5]
                    recomendation = sp.recommendations(seed_artists=artists_id_part, limit=5)
                    recomendation_data.extend(recomendation['tracks'])
                else:
                    artists_id_part = artists_id[i:]
                    recomendation = sp.recommendations(seed_artists=artists_id_part, limit=5)
                    recomendation_data.extend(recomendation['tracks'])
            info = 'Recomendation artists for you:\n'
            additional_info, artist_photo = messageUtils.show_songs_artists(recomendation_data, 'artist')
            info += additional_info
            messageUtils.send_long_message_with_photo(message.chat.id, info, artist_photo)
        except SpotifyException as e:
            if e.http_status == 403 and 'User not registered in the Developer Dashboard' in str(e):
                bot.send_message(message.chat.id,
                                 "Error: User not registered in the Dashboard(your email is not approved). Please change your /email")
            else:
                bot.send_message(message.chat.id, f"An error occurred: {e}")

    def get_recomendation_tracks_by_basis(self, message, time_range):
        if user_states.get(message.chat.id) == 'get_recomendation_tracks_by_basis':
            return
        print(f"{datetime.now()} - Getting recomendation tracks by basis by {message.from_user.id} {message.from_user.username}")
        user_states[message.from_user.id] = 'get_recomendation_tracks_by_basis'
        sp = authSp.get_sp_token(message.from_user.id)
        sp._session.timeout = 5
        try:
            if time_range == 'last_added':
                user_top_read = sp.current_user_saved_tracks(limit=25, offset=0)
                tracks_id = []
                for track in user_top_read['items']:
                    tracks_id.append(track['track']['id'])
            else:
                user_top_read = sp.current_user_top_tracks(limit=25, time_range=time_range, offset=0)
                tracks_id = []
                for track in user_top_read['items']:
                    tracks_id.append(track['id'])
            recomendation_data = []
            for i in range(0, len(tracks_id), 5):
                if i + 5 < len(tracks_id):
                    tracks_id_part = tracks_id[i:i + 5]
                else:
                    tracks_id_part = tracks_id[i:]
                try:
                    recomendation = sp.recommendations(seed_tracks=tracks_id_part, limit=5)
                    recomendation_data.extend(recomendation['tracks'])
                except requests.exceptions.Timeout:
                    bot.send_message(message.chat.id, "Timeout error. Please try again", reply_markup=main_keyboard)

                    return
            return recomendation_data

        except SpotifyException as e:
            if e.http_status == 403 and 'User not registered in the Developer Dashboard' in str(e):
                bot.send_message(message.chat.id,
                                 "Error: User not registered in the Dashboard(your email is not approved). Please change your /email",
                                 reply_markup=main_keyboard)
            elif e.http_status == 429:
                bot.send_message(message.chat.id, "Too many requests. Please try again later",
                                 reply_markup=main_keyboard)
            else:
                bot.send_message(message.chat.id, f"An error occurred: {e}")

    def get_recently_played(self, message, number):
        if user_states.get(message.chat.id) == 'get_recently_played':
            return
        user_states[message.from_user.id] = 'get_recently_played'
        sp = authSp.get_sp_token(message.from_user.id)
        try:
            # Get the current time

            # Get the user's recently played tracks in the last 10 minutes
            # recently_played_tracks = sp.current_user_recently_played(limit=50, after=after_timestamp)
            user_top_read = sp.current_user_recently_played(limit=number)
            info = 'Your recently played tracks:\n\n'
            additional_info, track_photo = messageUtils.show_songs_artists(user_top_read['items'], 'recently_played')
            info += additional_info
            messageUtils.send_long_message_with_photo(message.chat.id, info, track_photo)
            # bot.reply_to(message, "You also can add playlist with these songs to your library!", reply_markup=main_keyboard)
        except SpotifyException as e:
            if e.http_status == 403 and 'User not registered in the Developer Dashboard' in str(e):
                bot.send_message(message.chat.id,
                                 "Error: User not registered in the Dashboard(your email is not approved). Please change your /email",
                                 reply_markup=main_keyboard)
            elif e.http_status == 429:
                bot.send_message(message.chat.id, "Too many requests. Please try again later",
                                 reply_markup=main_keyboard)
            else:
                bot.send_message(message.chat.id, f"An error occurred: {e}")

    def add_playlist(self, message, recomendation_data):
        if user_states.get(message.chat.id) == 'add_playlist':
            return
        print(f"{datetime.now()} - Adding playlist by {message.from_user.id} {message.from_user.username}")
        user_states[message.from_user.id] = 'add_playlist'
        if message.text.lower() == 'add playlist':
            sp = authSp.get_sp_token(message.from_user.id)
            playlist_name = f"Recomendation by wrapped.stats"
            playlist = sp.user_playlist_create(sp.me()['id'], playlist_name)
            track_ids = [track['id'] for track in recomendation_data]
            sp.playlist_add_items(playlist['id'], track_ids)
            playlist_link = playlist['external_urls']['spotify']
            bot.send_message(message.chat.id, f"Playlist added successfully. [Link to playlist]({playlist_link})", reply_markup=main_keyboard, parse_mode='Markdown')


    def get_top_artists(self, message, time_range, number):
        print(f"{datetime.now()} - Getting top artists by {message.from_user.id} {message.from_user.username}")
        if user_states.get(message.chat.id) == 'get_top_artists':
            return
        user_states[message.from_user.id] = 'get_top_artists'
        sp = authSp.get_sp_token(message.from_user.id)
        try:
            user_top_read = sp.current_user_top_artists(limit=number, time_range=time_range, offset=0)
            # bot.send_message(message.chat.id, "Your top artists: ")
            time_range_readable = ''
            if time_range == 'short_term':
                time_range_readable = 'month'
            elif time_range == 'medium_term':
                time_range_readable = 'half year'
            elif time_range == 'long_term':
                time_range_readable = 'all time'
            info = f'Your top {number} artists for {time_range_readable}:\n\n'
            additional_info, artist_photo =  messageUtils.show_songs_artists(user_top_read['items'], 'artist_top')
            info += additional_info
            messageUtils.send_long_message_with_photo(message.chat.id, info, artist_photo)
        except SpotifyException as e:
            if e.http_status == 403 and 'User not registered in the Developer Dashboard' in str(e):
                bot.send_message(message.chat.id,
                                 "Error: User not registered in the Dashboard(your email is not approved). Please change your /email")
            else:
                bot.send_message(message.chat.id, f"An error occurred: {e}")

    def get_currently_playing(self, message, user_id):
        print(f"{datetime.now()} - Getting currently playing by {user_id}")
        if user_states.get(message.chat.id) == 'get_currently_playing':
            return
        user_states[message.from_user.id] = 'get_currently_playing'
        sp = authSp.get_sp_token(user_id)
        try:
            currently_playing = sp.current_playback()
            if currently_playing is None:
                user_states[message.from_user.id] = 'none'
                return False
            else:
                track = currently_playing['item']
                artist_names = ', '.join(
                    [f"[{artist['name'].replace('[', '').replace(']', '')}]({artist['external_urls']['spotify']})"
                     for artist in track['artists']])
                track_name = track['name'].replace('[', '').replace(']', '')
                track_photo = track['album']['images'][0]['url']
                track_link = track['external_urls']['spotify']
                info = f"Currently playing: {artist_names} - [{track_name}]({track_link})"
                bot.send_photo(message.chat.id, track_photo, info, reply_markup=functions_keyboard,
                               parse_mode='Markdown')
                user_states[message.from_user.id] = 'none'
                return True
        except SpotifyException as e:
            user_states[message.from_user.id] = 'none'
            return

    def get_top_tracks(self, message, time_range, number):
        if user_states.get(message.chat.id) == 'get_top_tracks':
            return
        user_states[message.from_user.id] = 'get_top_tracks'
        sp = authSp.get_sp_token(message.from_user.id)
        try:
            user_top_read = sp.current_user_top_tracks(limit=number, time_range=time_range, offset=0)
            it = 1
            time_range_readable = ''
            if time_range == 'short_term':
                time_range_readable = 'month'
            elif time_range == 'medium_term':
                time_range_readable = 'half year'
            elif time_range == 'long_term':
                time_range_readable = 'all time'

            info = f'Your top {number} tracks for {time_range_readable}:\n\n'
            additional_info, track_photo =  messageUtils.show_songs_artists(user_top_read['items'], 'track')
            info += additional_info
            messageUtils.send_long_message_with_photo(message.chat.id, info, track_photo)

        except SpotifyException as e:
            if e.http_status == 403 and 'User not registered in the Developer Dashboard' in str(e):
                bot.send_message(message.chat.id,
                                 "Error: User not registered in the Dashboard(your email is not approved). "
                                 "Please change your /email")
            else:
                bot.send_message(message.chat.id, f"An error occurred: {e}")

    def update_users_listened(self):
        print (f"{datetime.now()} - Updating listened tracks")
        users = authSp.get_all_users()
        for user in users:
            sp = authSp.get_sp_token(user[0])
            try:
                now = datetime.now()
                ten_minutes_ago = now - timedelta(hours=3)
                after_timestamp = int(time.mktime(ten_minutes_ago.timetuple())) * 1000
                user_top_read = sp.current_user_recently_played(limit=50, after=after_timestamp)
                listened_tracks = {}
                it = 0
                for track in user_top_read['items']:
                    track_id = track['track']['id']
                    it += 1
                    if track_id in listened_tracks:
                        listened_tracks[track_id] += 1
                    else:
                        listened_tracks[track_id] = 1

                authSp.add_listened_track(user[0], listened_tracks)
                print(f"{datetime.now()} - Updated listened tracks for {user[0]}. Added {it} tracks")
                bot.send_message(ADMIN_ID, f"Updated listened tracks for {user[0]}. Added {it} tracks")

            except SpotifyException as e:
                if e.http_status == 403 and 'User not registered in the Developer Dashboard' in str(e):
                    bot.send_message(user[0],
                                     "Error: User not registered in the Dashboard(your email is not approved). Please change your /email")
                elif e.http_status == 429:
                    bot.send_message(user[0], "Too many requests. Please try again later")
                else:
                    bot.send_message(user[0], f"An error occurred: {e}")
            except Exception as e:
                bot.send_message(user[0], f"An error occurred: {e}")
            time.sleep(1)
    def song_of_the_day(self):
        print (f"{datetime.now()} - Getting song of the day")
        users = authSp.get_all_users()
        it = 0
        while True:
            random_user = random.choice(users)
            sp = authSp.get_sp_token(random_user[0])
            try:
                user_top_read = sp.current_user_top_tracks(limit=15, time_range='short_term', offset=0)
                if(len(user_top_read['items']) == 0):
                    it += 1
                    if it > 100:
                        return None
                    continue
                random_track = random.choice(user_top_read['items'])
                if random_track['id'] is not None:
                    return random_track['id']
                it += 1
                if it > 100:
                    return None
            except SpotifyException as e:
                return None
    def getInfoById(self, user_id, track_id, sp):
        sp = authSp.get_sp_token(user_id)
        try:
            track = sp.track(track_id)
            artist_names = ', '.join(
                [f"[{artist['name'].replace('[', '').replace(']', '')}]({artist['external_urls']['spotify']})"
                 for artist in track['artists']])
            track_name = track['name'].replace('[', '').replace(']', '')
            track_photo = track['album']['images'][0]['url']
            track_link = track['external_urls']['spotify']
            info = f"{artist_names} - [{track_name}]({track_link})"
            return info, track_photo
        except SpotifyException as e:
            return

    def getInfoByIds(self, tracks_id, sp_token, is_photo):
        try:
            tracks = sp_token.tracks(tracks_id)
            info = []
            track_photo = None
            all_artists_names = []
            for track in tracks['tracks']:
                artists_name_url_list = []
                for artist in track['artists']:
                    artist_name = f"{artist['name'].replace('[', '').replace(']', '')}"
                    artist_name_url = f"[{artist_name}]({artist['external_urls']['spotify']})"
                    all_artists_names.append(artist_name_url)
                    artists_name_url_list.append(artist_name_url)
                artists_names = ', '.join(artists_name_url_list)

                track_name = track['name'].replace('[', '').replace(']', '')
                track_link = track['external_urls']['spotify']
                if is_photo is True:
                    track_photo = track['album']['images'][0]['url']
                    is_photo = False
                info.append(f"{artists_names} - [{track_name}]({track_link})")
            return info, track_photo, all_artists_names
        except SpotifyException as e:
            print(e)
            return None, None, None