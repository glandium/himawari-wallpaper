#!/usr/bin/env python

# This is a very crude script. It could be better and user friendly, but
# it does what /I/ need it to do for now, so I didn't go the extra mile(s).

# It grabs the tiles used on http://himawari8.nict.go.jp/ to create an
# image that can be used as a wallpaper.
# The timestamp for the latest imaging available is taken from
#   http://himawari8.nict.go.jp/img/D531106/latest.json
# The corresponding tiles are available from
#   http://himawari8.nict.go.jp/img/D531106/<TILE_NUMBERS>d/550/<year>/<month>/<day>/<hh><mm><ss>_<x>_<y>.png
# where:
# - TILE_NUMBERS can be 2, 4, 8, 16 or 20. The bigger the number the more
#   detail in the tiles.
# - year, month, day, hh, mm, ss correspond to the timestamp
# - x and y are horizontal and vertical tile index, between 0 and
#   TILE_NUMBERS - 1.

# The adjustable parameters are:
# - HORIZONTAL: a range of tile numbers to use horizontally
# - VERTICAL: a range of tile numbers to use vertically
# - TIME_NUMBERS: see above.
# - SCALE: the size each tile is scaled to
# - IMAGE_PATH: the path where the aggregated image will be stored and updated.

import os
import requests
import time
import Image

HORIZONTAL = tuple(range(3, 12))
VERTICAL = tuple(range(0, 6))
TILE_NUMBERS = 16
SCALE = 350
IMAGE = 'D531106'
HIMAWARI = 'himawari8.nict.go.jp'

IMAGE_PATH = '/tmp/Himawari.png'
IMAGE_TMP_PATH = '%s_%s' % os.path.splitext(IMAGE_PATH)

BASE_URL = 'http://%s/img/%s' % (HIMAWARI, IMAGE)

last_date = None

while True:
    session = requests.Session()
    try:
        response = session.get('%s/latest.json' % (BASE_URL))
        if response.status_code != 200:
            continue

        date = response.json().get('date')
    except:
        continue
    if date == last_date:
        time.sleep(60)
        continue

    print date
    last_date = date

    date = date.replace('-', '/').replace(' ', '/').replace(':', '')

    image = Image.new('RGB', tuple(SCALE * len(n)
                                   for n in (HORIZONTAL, VERTICAL)))

    for x, h in enumerate(HORIZONTAL):
        for y, v in enumerate(VERTICAL):
            try:
                response = session.get('%s/%dd/550/%s_%d_%d.png' %
                                       (BASE_URL, TILE_NUMBERS, date, h, v),
                                       stream=True)
                if response.status_code != 200:
                    continue
                tile = Image.open(response.raw)
            except:
                continue
            image.paste(tile.resize((SCALE, SCALE), Image.BILINEAR),
                        tuple(n * SCALE for n in (x, y)))

    image.save(IMAGE_TMP_PATH)
    os.rename(IMAGE_TMP_PATH, IMAGE_PATH)
