import datetime
import time
import sched

from models import Post


s2 = sched.scheduler(time.time, time.sleep)


def delete_old_posts(date):
    for post in Post.get_old_posts(date):
        Post.delete(post)
    s2.enter(2592000, 1, delete_old_posts,
             ((datetime.datetime.today() - datetime.timedelta(days=30)).date(),))


s2.enter(2592000, 1, delete_old_posts,
         ((datetime.datetime.today() - datetime.timedelta(days=30)).date(),))
s2.run()
