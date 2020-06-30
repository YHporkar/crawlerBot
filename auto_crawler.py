import datetime
import time
import sched

from models import Channel, Post

from crawler import *


s1 = sched.scheduler(time.time, time.sleep)


def crawl_channels(channels):
    rep = 0
    print(datetime.datetime.now().time(), ' Updating...')
    for channel in channels:
        index = 50
        print(channel.username)
        post_store = []
        post_store = Post.get_urls_by_channel(
            channel.username.replace('@', ''))
        root_url = 'https://t.me/' + channel.username.replace('@', '') + '/'
        # start = Channel.update_start(
        #     channel, get_last_post_url(channel.username))
        start = 875
        i = start
        while(i >= start - index and i != 0):
            print(root_url + str(i))
            # if post is not already in database
            if root_url + str(i) in post_store:
                print('duplicate')
                i -= 1
                # break
                continue
            soup = get_soup(root_url + str(i))
            if is_there_post(soup):
                # store in database
                Post(caption=get_caption(soup), raw_caption=caption_normalization(get_caption(soup)),
                     channel_name=channel.name, views=float_to_int(get_views(soup)), url=root_url + str(i),
                     date=get_date(soup), format=get_format(soup), duration=get_duration(soup)).add()
                print('added')

                # skip album posts
                if is_grouped(soup):
                    lai = get_album_last_index(soup)
                    print(lai)
                    i -= i - lai
                    print(i)
                    index += i - lai
                    if rep == lai:
                        i -= 1
                    rep = lai
            i -= 1
            time.sleep(0.3)

    s1.enter(6000, 1, crawl_channels, (channels,))
    print(datetime.datetime.now().time(), ' Everything is up to date.')


s1.enter(0, 1, crawl_channels, (Channel.get_all(),))

s1.run()
