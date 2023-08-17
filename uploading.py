from copy import deepcopy
from datetime import datetime
import hashlib
import logging.config
import mimetypes
import random
import time
from pathlib import Path
from urllib.parse import urlencode
import requests
from login import login
logger = logging.getLogger()

UPLOAD_CHUNK_SIZE = 4 * 1024 * 1024
MEDIA_UPLOAD_SUCCEED = 'succeeded'
MEDIA_UPLOAD_FAIL = 'failed'
    
def upload_media(filename, session=None) -> int:
    if session == None:
        session = login(username=username, password=password)
    headers = {
        'authorization': 'Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA',
        'accept-encoding': 'gzip, deflate, br',
        'cookie': '; '.join(f'{k}={v}' for k, v in session.cookies.items()),
        'referer': 'https://twitter.com/',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36',
        'x-csrf-token': session.cookies.get('ct0'),
    }
    
    url = 'https://upload.twitter.com/i/media/upload.json'
    file = Path(filename)
    total_bytes = file.stat().st_size

    media_type = mimetypes.guess_type(file)[0]
    media_category = "tweet_video"

    data = {'command': 'INIT', 'media_type': media_type, 'total_bytes': total_bytes,
            'media_category': media_category}
    r = session.post(url=url, headers=headers, data=data)
    media_id = r.json()['media_id']

    with open(file, 'rb') as f:
        i = 0
        while chunk := f.read(UPLOAD_CHUNK_SIZE):  # todo: arbitrary max size for now
            data = {'command': 'APPEND', 'media_id': media_id, 'segment_index': i}
            files = {'media': chunk}
            r = session.post(url=url, headers=headers, data=data, files=files)
            if r.status_code < 200 or r.status_code > 299:
                logger.debug(f'{r.status_code} {r.text}')
                raise Exception('Upload failed')
            i += 1

    data = {'command': 'FINALIZE', 'media_id': media_id, 'allow_async': 'true'}
    r = session.post(url=url, headers=headers, data=data)

    logger.debug(f'processing, please wait...')
    processing_info = r.json().get('processing_info')
    while processing_info:
        state = processing_info['state']
        logger.debug(f'{processing_info = }')
        if state == MEDIA_UPLOAD_SUCCEED:
            break
        if state == MEDIA_UPLOAD_FAIL:
            raise Exception('Media processing failed')
        check_after_secs = processing_info.get('check_after_secs', random.randint(1, 5))
        time.sleep(check_after_secs)
        params = {'command': 'STATUS', 'media_id': media_id}
        r = session.get(url=url, headers=headers, params=params)
        processing_info = r.json().get('processing_info')
    logger.debug('processing complete')

    return media_id