# reddit2vk

This script allows you post to vk community from reddit subreddits.

Reddit API documentation: https://www.reddit.com/dev/api/

VK API documentation: https://vk.com/dev/methods

After you setup your tokens and id's you just need to specify subreddit and delay, i.e. if you want post to your vk community posts from AskReddit with 1 hour delay your should call

``` python
post_to_vk(reddit, 'AskReddit', 3600)
```
