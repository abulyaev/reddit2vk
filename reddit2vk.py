import praw
import requests
import json
import time

# Create vk token. Google vk part.
user_token = 'Your user token here'

# See https://www.reddit.com/dev/api/
# Create an app and copy information to here.
# Your app information will be located here https://www.reddit.com/prefs/apps


def init_reddit(reddit_client_id, reddit_client_secret, reddit_username, reddit_password, reddit_user_agent):
    reddit_init = praw.Reddit(client_id=reddit_client_id,  # Your client id here
                              client_secret=reddit_client_secret,  # Your client secret here
                              username=reddit_username,  # Your Reddit username here
                              password=reddit_password,  # Your Reddit password here
                              user_agent=reddit_user_agent)  # Your user agent here (see example)
    return reddit_init


def upload_from_reddit(reddit, subreddit_name):
    link = []
    text = []
    subreddit = reddit.subreddit(subreddit_name)  # Subreddit name
    hot = subreddit.hot(limit=70)  # Get 70 hot posts
    for submission in hot:
        if not submission.stickied:
            link.append(submission.url)
            text.append(submission.title)
    return link, text


def upload_to_vk(content_link, content_text, timer, delay):
    for images, texts in zip(content_link, content_text):
        timer = int(timer + delay)
        params = (
            ('owner_id', '-your owner id here (minus is mandatory)'),
            ('access_token', user_token),
            ('v', '5.92'),
        )
        UploadServer = requests.get('https://api.vk.com/method/photos.getWallUploadServer', params=params)
        link = json.loads(UploadServer.text)
        UploadServer = link["response"]["upload_url"]

        # It's an image
        if images.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif')):
            try:
                image = requests.get(images, stream=True)
            except ConnectionError:
                continue
            data = ("image.jpg", image.raw, image.headers['Content-Type'])
            meta = requests.post(UploadServer, files={'photo': data}).json()

            params = (
                ('owner_id', '- your owner id here (minus is mandatory)'),
                ('access_token', user_token),
                ('server', meta["server"]),
                ('hash', meta["hash"]),
                ('photo', meta["photo"]),
                ('v', '5.92'),
            )
            resp = requests.get('https://api.vk.com/method/photos.saveWallPhoto', params=params)
            jsonResponse = json.loads(resp.text)
            try:
                photoOwner_id = jsonResponse['response'][0]['owner_id']
                photo_id = jsonResponse['response'][0]['id']
            except KeyError:
                continue

            params = (
                ('owner_id', '-your owner id here (minus is mandatory)'),
                ('from_group', '1'),
                ('message', texts),
                ('attachments', 'photo' + str(photoOwner_id) + "_" + str(photo_id)),
                ('publish_date', timer),
                ('access_token', user_token),
                ('v', '5.92'),
            )
            try:
                response = requests.get('https://api.vk.com/method/wall.post', params=params)
            except ConnectionError:
                continue
            if response.status_code == 200:
                print("Image " + str(images) + " done.\n")
            time.sleep(1)
        else:  # It's an article
            params = (
                ('owner_id', '-your owner id here (minus is mandatory)'),
                ('from_group', '1'),
                ('message', texts),
                ('attachments', images),
                ('publish_date', timer),
                ('access_token', user_token),
                ('v', '5.92'),
            )
            try:
                response = requests.get('https://api.vk.com/method/wall.post', params=params)
            except ConnectionError:
                continue
            if response.status_code == 200:
                print("Article " + str(images) + " posted.\n")
            time.sleep(1)


def post_to_vk(reddit, subreddit, delay):
    link, text = upload_from_reddit(reddit, subreddit)
    # 1800 is 30 minutes
    timer = time.time() + delay
    upload_to_vk(link, text, timer, delay)


# See arguments in 'init_reddit'
reddit = init_reddit('client id',
                     'secret id',
                     'username',
                     'password',
                     'reddit2vk:v0.1 (by /u/username)')

post_to_vk(reddit, 'subreddit name here', 3600)
post_to_vk(reddit, 'another subreddit name', 1800)
