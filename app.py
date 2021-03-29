# Make it respond to !FantasyPoll instead? Using comment stream in subreddit. Also save comments to keep track of responses, prevent duplicates.
# Set up venv
# Set up Heroku
# Do more testing

# Change to correct subreddit
# Make polls public

import praw
import requests
import time
from config import api_key, client_id, client_secret, username, password

SUBREDDIT = 'test'

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
    stream = reddit.inbox.stream(skip_existing=True)
    
    while True:
        # Try/Except deals with issues like outages, making sure bot keeps going (https://www.reddit.com/r/redditdev/comments/a8egy4/praw_how_to_make_subreddit_streams_as_robust_as/eca2nyk?utm_source=share&utm_medium=web2x&context=3)
        try:
            for item in stream:
                if item.subreddit == SUBREDDIT:
                    text = item.body
                    if f'u/{username.lower()}' in text.lower():
                        poll_choices = get_choices(text)
                        poll_url = make_poll(poll_choices)
                        item.reply(f'[Here\'s your poll!]({poll_url})')
        except Exception as error:
            print(error)
        time.sleep(60)

def get_choices(text):
    # Isolate just the choices, which are found after the bot is called
    word_list = text.split()
    for i, word in enumerate(word_list):
        if f'{username.lower()}' in word.lower():
            word_list = word_list[i+1:]
            break
    poll_choices = ' '.join(word_list).split(', ')
    return poll_choices

def make_poll(choices):
    data = {
        'poll': {
            'title': 'Fantasy Baseball Poll',
            'answers': choices,
            # 'priv': False,
            'co': False
        }   
    }
    poll = requests.post('https://strawpoll.com/api/poll', json=data, headers={'API-KEY': api_key}).json()
    return 'https://strawpoll.com/' + poll['content_id']

if __name__ == "__main__":
    main()
