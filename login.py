from functools import wraps
from models import Admin

# NOTREGISTERED = 9


def login_required(f):
    @wraps(f)
    def wrap(update, context, *args, **kwargs):
        admin = Admin.get_by_username(update.message.from_user.username)
        if admin:
            return f(update, context, *args, **kwargs)
        else:
            update.message.reply_text('دسترسی مقدور نیست')
            # return NOTREGISTERED
    return wrap


def super_login_required(f):
    @wraps(f)
    def wrap(update, context, *args, **kwargs):
        admin = Admin.get_by_username(update.message.from_user.username)
        if admin.is_super:
            return f(update, context, *args, **kwargs)
        else:
            update.message.reply_text('دسترسی مقدور نیست')
            # return NOTREGISTERED
    return wrap
