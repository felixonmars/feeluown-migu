import logging
import time

from fuocore.media import Media
from fuocore.models import BaseModel, SongModel, ModelStage, SearchModel, ArtistModel, AlbumModel, MvModel, LyricModel, \
    SearchType, PlaylistModel

from .api import MiguApi
from .provider import provider

logger = logging.getLogger(__name__)


def _deserialize(data, schema_class, gotten=True):
    """ deserialize schema data to model

    :param data: data to be deserialize
    :param schema_class: schema class
    :param gotten:
    :return:
    """
    schema = schema_class()
    obj = schema.load(data)
    if gotten:
        obj.stage = ModelStage.gotten
    return obj


class KuwoBaseModel(BaseModel):
    _api: MiguApi = provider.api

    class Meta:
        fields = ['rid']
        provider = provider


class KuwoLyricModel(LyricModel, BaseModel):
    pass


class KuwoMvModel(MvModel, KuwoBaseModel):
    pass


class MiguSongModel(SongModel, KuwoBaseModel):
    class Meta:
        allow_get = True
        support_multi_quality = True
        fields = ['lrc', 'qualities', 'link']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @classmethod
    def get(cls, identifier):
        data = cls._api.get_song(identifier)
        return _deserialize(data.get('data'), MiguSongSchema)

    @property
    def url(self):
        if self.link is None:
            song = self.get(self.identifier)
            self.link = song.link
        return self.link

    @url.setter
    def url(self, value):
        self.link = value

    def list_quality(self):
        return self.qualities

    def get_media(self, quality):
        if quality == 'lq':
            return Media(self.url,
                         format=MiguApi.QUALITIES[quality][1],
                         bitrate=MiguApi.QUALITIES[quality][0])
        data_song = self._api.get_song(self.identifier, quality=quality)
        url = data_song.get('data', {}).get('url')
        return Media(url, format=MiguApi.QUALITIES[quality][1], bitrate=MiguApi.QUALITIES[quality][0])\
            if url is not None else None


class MiguArtistModel(ArtistModel, KuwoBaseModel):
    class Meta:
        allow_get = True
        allow_create_albums_g = True
        allow_create_songs_g = True
        fields = ['_songs', '_albums', 'info']

    @classmethod
    def get(cls, identifier):
        data = cls._api.get_artist_info(identifier)
        return _deserialize(data.get('data'), MiguArtistSchema)


class MiguAlbumModel(AlbumModel, KuwoBaseModel):
    class Meta:
        allow_get = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @classmethod
    def get(cls, identifier):
        data_album = cls._api.get_album_info(identifier)
        return _deserialize(data_album.get('data'), MiguAlbumSchema)


class KuwoPlaylistModel(PlaylistModel, KuwoBaseModel):
    class Meta:
        allow_get = True
        allow_create_songs_g = True

    @classmethod
    def get(cls, identifier):
        data_album = cls._api.get_playlist_info(identifier)
        return _deserialize(data_album.get('data'), KuwoPlaylistSchema)

    def create_songs_g(self):
        pass


class MiguSearchModel(SearchModel, KuwoBaseModel):
    pass


def search_song(keyword: str):
    data_songs = provider.api.search(keyword, search_type=SearchType.so)
    songs = []
    for data_song in data_songs.get('musics', []):
        song = _deserialize(data_song, MiguSearchSongSchema)
        songs.append(song)
    return MiguSearchModel(songs=songs)


def search(keyword: str, **kwargs) -> MiguSearchModel:
    type_ = SearchType.parse(kwargs['type_'])
    if type_ == SearchType.so:
        return search_song(keyword)


from .schemas import (
    MiguSearchSongSchema, MiguAlbumSchema, MiguSongSchema,
)
