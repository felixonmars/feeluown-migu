import logging

import time
import requests
from fuocore.models import SearchType

logger = logging.getLogger(__name__)


class Singleton(type):
    """ singleton metaclass """
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class MiguApi(object, metaclass=Singleton):
    """ kuwo music API class """
    HEADERS = {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip,deflate',
        'Accept-Language': 'zh-CN,zh;q=0.8,gl;q=0.6,zh-TW;q=0.4',
        'Referer': 'http://music.migu.cn/v3',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/81.0.4044.138 Safari/537.36',
        'Host': 'migu.cn',
    }

    TIMEOUT = 30
    API_HOST = 'http://m.music.migu.cn/migu'
    SEARCH_TYPES = {
        SearchType.so: 2,
        SearchType.al: 4,
        SearchType.ar: 1,
        SearchType.pl: 6,
    }

    session: requests.Session

    def __init__(self):
        self.session = requests.session()

    def __del__(self):
        try:
            if self.session:
                self.session.close()
        except:
            pass

    def search(self, keyword: str, search_type: SearchType=SearchType.so, page=1, limit=20):
        uri = MiguApi.API_HOST + f'/remoting/scr_search_tag?keyword={keyword}' \
                                 f'&type={MiguApi.SEARCH_TYPES[search_type]}&pgc={page}&rows={limit}'
        response = self.session.get(uri)
        return response.json()

    def get_song(self, sid):
        uri = f'http://app.c.nf.migu.cn/MIGUM2.0/v2.0/content/listen-url?netType=01&resourceType=E&songId={sid}' \
              f'&toneFlag=HQ&dataType=2'
        response = self.session.get(uri, headers={
            'channel': '0146951',
            'uid': '123',
            'referer': 'http://music.migu.cn/v3/music/player/audio',
        })
        return response.json()
