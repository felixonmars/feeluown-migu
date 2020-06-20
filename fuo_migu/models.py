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


class MiguBaseModel(BaseModel):
    _api: MiguApi = provider.api

    class Meta:
        fields = ['rid']
        provider = provider


class MiguLyricModel(LyricModel, MiguBaseModel):
    pass


class MiguMvModel(MvModel, MiguBaseModel):
    pass


class MiguSongModel(SongModel, MiguBaseModel):
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


class MiguArtistModel(ArtistModel, MiguBaseModel):
    class Meta:
        allow_get = True
        allow_create_albums_g = True
        allow_create_songs_g = True
        fields = ['_songs', '_albums', 'info']

    @classmethod
    def get(cls, identifier):
        data = cls._api.get_artist_info(identifier)
        return _deserialize(data.get('data'), MiguArtistSchema)


class MiguAlbumModel(AlbumModel, MiguBaseModel):
    class Meta:
        allow_get = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @classmethod
    def get(cls, identifier):
        data_album = cls._api.get_album_info(identifier)
        return _deserialize(data_album.get('data'), MiguAlbumSchema)


class MiguPlaylistModel(PlaylistModel, MiguBaseModel):
    class Meta:
        allow_get = True
        allow_create_songs_g = True

    @classmethod
    def get(cls, identifier):
        pass

    def create_songs_g(self):
        pass


class MiguSearchModel(SearchModel, MiguBaseModel):
    pass


def search_song(keyword: str):
    data_songs = provider.api.search(keyword, search_type=SearchType.so)
    songs = []
    for data_song in data_songs.get('musics', []):
        song = _deserialize(data_song, MiguSearchSongSchema)
        songs.append(song)
    return MiguSearchModel(songs=songs)


def search_artist(keyword: str):
    data_artists = provider.api.search(keyword, search_type=SearchType.ar)
    artists = []
    for data_artist in data_artists.get('artists', []):
        artist = _deserialize(data_artist, MiguSearchArtistSchema)
        artists.append(artist)
    return MiguSearchModel(artists=artists)


def search_album(keyword: str):
    data_albums = provider.api.search(keyword, search_type=SearchType.al)
    albums = []
    for data_album in data_albums.get('albums', []):
        album = _deserialize(data_album, MiguSearchAlbumSchema)
        albums.append(album)
    return MiguSearchModel(albums=albums)


def search_playlist(keyword: str):
    data_playlists = provider.api.search(keyword, search_type=SearchType.pl)
    playlists = []
    for data_playlist in data_playlists.get('songLists', []):
        playlist = _deserialize(data_playlist, MiguSearchPlaylistSchema)
        playlists.append(playlist)
    return MiguSearchModel(playlists=playlists)


def search(keyword: str, **kwargs) -> MiguSearchModel:
    type_ = SearchType.parse(kwargs['type_'])
    if type_ == SearchType.so:
        return search_song(keyword)
    if type_ == SearchType.ar:
        return search_artist(keyword)
    if type_ == SearchType.al:
        return search_album(keyword)
    if type_ == SearchType.pl:
        return search_playlist(keyword)


from .schemas import (
    MiguSearchSongSchema, MiguAlbumSchema, MiguSongSchema, MiguSearchArtistSchema, MiguSearchAlbumSchema,
    MiguSearchPlaylistSchema,
)
