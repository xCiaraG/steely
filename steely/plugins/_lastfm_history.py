#!/usr/bin/env python3


from plugins._lastfm_helpers import *
from operator import itemgetter
from formatting import *


def time_or_now(track):
    if 'date' in track:
        return parsed_time(track['date']['#text'])
    return 'now'


def parsed_time(time_string):
    return time_string.split(', ')[1]


def parsed_response(response):
    if not 'recenttracks' in response:
        raise NameError('user not found')
    for track in response['recenttracks']['track']:
        yield time_or_now(track), \
              track['artist']['#text'], \
              track['name']


def gen_reply_string(response):
    if not response:
        raise KeyError('no tracks found')
    yield ''
    for time, artist, track in response:
        yield f'{time:>5} {artist:<15.15} {track:.25}'


def main(bot, author_id, message_parts, thread_id, thread_type, **kwargs):
    def send_message(message):
        bot.sendMessage(message, thread_type=thread_type, thread_id=thread_id)
    if message_parts:
        username = message_parts[0]
    else:
        username = USERDB.get(USER.id == author_id)['username']
    try:
        response = get_lastfm_request('user.getRecentTracks', user=username, limit=8).json()
        clean_response = list(parsed_response(response))
        reply_lines = list(gen_reply_string(clean_response))
        reply_body = '\n'.join(reply_lines)
        send_message(code_block(reply_body))
    except (NameError, KeyError) as exc:
        send_message(exc)
