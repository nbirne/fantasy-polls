# Do more testing
# Decide whether to use <>
# Merge into main branch
# Set up Heroku

# Change to correct subreddit
# Link to correct account
# Add a bio
# Make polls public

import praw
import requests
import time
from config import api_key, client_id, client_secret, username, password

SUBREDDIT = 'test'
TRIGGER = '!fantasypoll'

def main():
    reddit = praw.Reddit(client_id=client_id, 
        client_secret=client_secret, 
        user_agent=f'Fantasy Baseball Polling Bot (by u/{username})', 
        username=username, 
        password=password,
    )

    # Scan all inbox messages -   
        # If only mentions were scanned, this would exclude instances when 
        # the bot is mentioned in a reply to a comment or post made by the bot
    stream = reddit.subreddit(SUBREDDIT).stream.comments()
    
    while True:
        # Try/Except deals with issues like outages, making sure bot keeps going (https://www.reddit.com/r/redditdev/comments/a8egy4/praw_how_to_make_subreddit_streams_as_robust_as/eca2nyk?utm_source=share&utm_medium=web2x&context=3)
        try:
            for comment in stream:
                text = comment.body
                print(text)
                # Save comments after response, to eliminate duplication on restart (stream picks up 100 most recent)
                if TRIGGER in text.lower() and not comment.saved:
                    poll_choices = get_choices(text)
                    poll_url = make_poll(poll_choices)
                    comment.reply(f'[Here\'s your poll!]({poll_url})')
                    comment.save()
                    
        except Exception as error:
            print(error)
        time.sleep(60)

# Isolate just the choices, which are found after the bot is called
def get_choices(text):
    # Extract the substring with the choices
    trigger_loc = text.lower().find(TRIGGER)
    if '<' in text[trigger_loc:] and '>' in text[trigger_loc:]:
        start = text.find('<', trigger_loc) + 1
        stop = text.find('>', trigger_loc)
    else:
        start = trigger_loc + len(TRIGGER) + 1
        stop = text.find('\n', start)
        if stop == -1:
            stop = None
    text = text[start:stop]

    # Turn the choices into a list - split on ',' instead of ', ' in case users forget spaces
    choices = text.split(',')
    poll_choices = [choice.strip() for choice in choices]
    
    return poll_choices

def make_poll(choices):
    data = {
        'poll': {
            'title': 'Fantasy Baseball Poll',
            'answers': choices,
            'priv': False,
            'co': False
        }   
    }
    poll = requests.post('https://strawpoll.com/api/poll', json=data, headers={'API-KEY': api_key}).json()
    return 'https://strawpoll.com/' + poll['content_id']

if __name__ == "__main__":
    # main()
    text = 'Hey, here\'s a question: !fantasypoll <Juan Soto,Ronald Acuna,David Ortiz> More text'
    print(get_choices(text))
