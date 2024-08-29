import os
import re
from datetime import datetime

import telebot
from dotenv import load_dotenv
load_dotenv()

BOT_TOKEN = str(os.getenv("BOT_TOKEN"))
bot = telebot.TeleBot(BOT_TOKEN)
main_keyboard = telebot.types.ReplyKeyboardMarkup(True)
main_keyboard.row('/main')
main_keyboard.row('/options')

class messageUtils:
    def convertTime(self, time):
        played_at_datetime = datetime.strptime(time, '%Y-%m-%dT%H:%M:%S.%fZ')
        current_time = datetime.utcnow()
        time_difference = current_time - played_at_datetime
        minutes_ago = time_difference.total_seconds() / 60
        hours_ago = time_difference.total_seconds() / 3600
        days_ago = time_difference.total_seconds() / 86400
        if days_ago >= 1:
            return f'{int(days_ago)} days ago'
        elif hours_ago >= 1:
            return f'{int(hours_ago)} hours ago'
        elif minutes_ago >= 1:
            return f'{int(minutes_ago)} minutes ago'
        else:
            return f'Just now'

    def send_long_message_with_photo(self, message_id, text, photo_url):
        parts = text.split('\n')
        buffer = ""
        for part in parts:
            if self.len_without_links(buffer) + self.len_without_links(part) > 1000:
                if photo_url is not None:
                    bot.send_photo(message_id, photo_url, buffer, reply_markup=main_keyboard,
                                   parse_mode='Markdown')
                    photo_url = None
                else:
                    bot.send_message(message_id, buffer, reply_markup=main_keyboard, parse_mode='Markdown')
                buffer = part + '\n'
            else:
                buffer += part + '\n'
        if buffer:
            if photo_url is not None:
                bot.send_photo(message_id, photo_url, buffer, reply_markup=main_keyboard, parse_mode='Markdown')
            else:
                bot.send_message(message_id, buffer, reply_markup=main_keyboard, parse_mode='Markdown')

    def len_without_links(self, text):

        text = re.sub(r'\(https?:\/\/.*?\)', '', text)
        length = sum(len(match) for match in text)

        return length

    def show_songs_artists(self, recomendation_data, type):
        it = 1
        item_photo = None
        info = ''
        for item in recomendation_data:
            if it == 1 and type == 'track':
                item_photo = item['album']['images'][0]['url']
            elif it == 1 and type == "artist_top":
                item_photo = item['images'][0]['url']
            elif it == 1 and type == "recently_played":
                item_photo = item['track']['album']['images'][0]['url']
            if type == "artist":
                artist_name = item['artists'][0]['name'].replace('[', '').replace(']', '')
                artist_link = item['artists'][0]['external_urls']['spotify']
                info += f"{it}. [{artist_name}]({artist_link})\n"
            elif type == "track":
                artist_names = ', '.join(
                    [f"[{artist['name'].replace('[', '').replace(']', '')}]({artist['external_urls']['spotify']})" for
                     artist in item['artists']])
                track_name = item['name'].replace('[', '').replace(']', '')
                track_link = item['external_urls']['spotify']
                info += f"{it}. {artist_names} - [{track_name}]({track_link})\n"
            elif type == "artist_top":
                artist_name = item['name'].replace('[', '').replace(']', '')
                artist_link = item['external_urls']['spotify']
                info += f"{it}. [{artist_name}]({artist_link})\n"
            elif type == "recently_played":
                # also add time of playing
                artist_names = ', '.join(
                    [f"[{artist['name'].replace('[', '').replace(']', '')}]({artist['external_urls']['spotify']})"
                     for artist in item['track']['artists']])
                track_name = item['track']['name'].replace('[', '').replace(']', '')
                track_link = item['track']['external_urls']['spotify']
                played_at = item['played_at']
                when_played = self.convertTime(played_at)

                info += f"{it}. {artist_names} - [{track_name}]({track_link})\n Time: {when_played}\n"
            it = it + 1
            info += '\n'
        return info, item_photo