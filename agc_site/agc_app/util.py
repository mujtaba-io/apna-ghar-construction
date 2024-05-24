
# TODO: THIS FILE DOES NOT SERVE ANY PURPOSE FOR NOW.

# This file is written to modularize some functions we are going to use.

import enum


class FileUsage(enum.Enum):
    USAGE_PROFILE_PHOTO = 10,
    USAGE_SERVICE_PHOTO = 11,
    USAGE_OTHER_PHOTOS = 12,


def upload_file(by_user, usage, file):
    with open('user_content/' + by_user.username + '/' + usage + '.', 'wb+') as destination:
        for chunk in file.chunks():
            destination.write(chunk)
