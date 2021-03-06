from html import unescape

from marshmallow import Schema, fields, post_load, EXCLUDE


class BaseSchema(Schema):
    class Meta:
        unknown = EXCLUDE


Schema = BaseSchema


class MiguSongItemSchema(Schema):
    identifier = fields.Int(data_key='songId', required=True)
    title = fields.Str(data_key='songName', required=True)
    albumid = fields.Int(data_key='albumId', required=False)
    album = fields.Str(data_key='album', required=False)
    covers = fields.List(fields.Dict, data_key='albumImgs', required=False)
    artists = fields.List(fields.Dict, data_key='artists', required=False)
    lrc = fields.Str(data_key='lrcUrl', required=False)
    top_quality = fields.Str(data_key='topQuality', required=False)


class MiguSongSchema(Schema):
    # ['name', 'cover', 'songs', 'artists', 'desc', 'type']
    song_item = fields.Nested(MiguSongItemSchema, data_key='songItem')
    url = fields.Str(data_key='url', required=False)
    format_type = fields.Str(data_key='formatType', required=False)

    @post_load
    def create_model(self, data, **kwargs):
        artists = []
        album = None
        if data.get('song_item').get('albumid'):
            cover = data.get('song_item').get('covers')[0] or None
            if cover:
                cover = cover.get('img')
            album = MiguAlbumModel(identifier=data.get('song_item').get('albumid'),
                                   name=data.get('song_item').get('album'), cover=cover)
        if data.get('song_item', {}).get('artists'):
            for artist in data.get('song_item').get('artists'):
                artists.append(MiguArtistModel(identifier=artist.get('id'), name=artist.get('name')))
        # qualities = ['lq']
        # top_q = data.get('song_item', {}).get('top_quality')
        # if top_q == 'SQ':
        #     qualities = ['sq', 'hq', 'lq']
        # elif top_q == 'HQ':
        #     qualities = ['hq', 'lq']
        return MiguSongModel(identifier=data.get('song_item').get('identifier'), title=data.get('song_item').get('title'),
                             link=data.get('url'), lrc=data.get('song_item').get('lrc'), album=album,
                             artists=artists, duration=10000)


class MiguSearchSongSchema(Schema):
    identifier = fields.Int(data_key='id', required=True)
    title = fields.Str(data_key='songName', required=True)
    albumid = fields.Str(data_key='albumId', required=False)
    album = fields.Str(data_key='albumName', required=False)
    cover = fields.Str(data_key='cover', required=False, default=None, allow_none=True)
    url = fields.Str(data_key='url', required=False)
    lrc = fields.Str(data_key='lyrics', required=False)
    artistid = fields.Str(data_key='singerId', required=False)
    artist = fields.Str(data_key='singerName', required=False)
    has_sq = fields.Str(data_key='hasSQqq', required=False, default='0', allow_none=True)
    has_hq = fields.Str(data_key='hasHQqq', required=False, default='0', allow_none=True)

    @post_load
    def create_model(self, data, **kwargs):
        album = None
        artists = []
        if data.get('albumid'):
            album = MiguAlbumModel(identifier=int(data.get('albumid')), name=data.get('album'), cover=data.get('cover'))
        if data.get('artistid'):
            artists_name = data.get('artist').split(', ')
            for i, aid in enumerate(data.get('artistid').split(', ')):
                artists.append(MiguArtistModel(identifier=int(aid), name=artists_name[i] or ''))
        qualities = ['lq']
        if data.get('has_sq') and int(data.get('has_sq')) == 1:
            qualities.append('sq')
        if data.get('has_hq') and int(data.get('has_hq')) == 1:
            qualities.append('hq')
        return MiguSongModel(identifier=data.get('identifier'), title=data.get('title'), duration=10000,
                             lrc=data.get('lrc'), album=album, artists=artists, qualities=reversed(qualities))


class MiguSearchArtistSchema(Schema):
    identifier = fields.Str(data_key='id', required=True)
    name = fields.Str(data_key='title', required=True)
    cover_l = fields.Str(data_key='artistPicL', required=False, default=None, allow_none=True)
    cover_m = fields.Str(data_key='artiicM', required=False, default=None, allow_none=True)
    cover_s = fields.Str(data_key='artistPicS', required=False, default=None, allow_none=True)

    @post_load
    def create_model(self, data, **kwargs):
        cover = None
        if data.get('cover_s'):
            cover = data.get('cover_s')
        if data.get('cover_m'):
            cover = data.get('cover_m')
        if data.get('cover_l'):
            cover = data.get('cover_l')
        return MiguArtistModel(identifier=int(data.get('identifier')), name=data.get('name'), cover=cover or '')


class _MiguSearchAlbumArtistsSchema(Schema):
    identifier = fields.Str(data_key='id', required=True)
    name = fields.Str(data_key='name', required=True)

    @post_load
    def create_model(self, data, **kwargs):
        return MiguArtistModel(identifier=int(data.get('identifier')), name=data.get('name'))


class MiguSearchAlbumSchema(Schema):
    identifier = fields.Str(data_key='id', required=True)
    name = fields.Str(data_key='title', required=True)
    cover_l = fields.Str(data_key='albumPicL', required=False)
    cover_m = fields.Str(data_key='albumPicM', required=False)
    cover_s = fields.Str(data_key='albumPicS', required=False)
    artists = fields.List(fields.Nested('_MiguSearchAlbumArtistsSchema'), data_key='singer')

    @post_load
    def create_model(self, data, **kwargs):
        cover = None
        if data.get('cover_s'):
            cover = data.get('cover_s')
        if data.get('cover_m'):
            cover = data.get('cover_m')
        if data.get('cover_l'):
            cover = data.get('cover_l')
        return MiguAlbumModel(identifier=int(data.get('identifier')), name=data.get('name'), cover=cover or '',
                              artists=data.get('artists'))


class MiguSearchPlaylistSchema(Schema):
    identifier = fields.Str(data_key='id', required=True)
    name = fields.Str(data_key='name', required=True)
    cover = fields.Str(data_key='img', required=False)

    @post_load
    def create_model(self, data, **kwargs):
        return MiguPlaylistModel(identifier=int(data.get('identifier')), name=data.get('name'), cover=data.get('cover'))


class MiguAlbumSchema(Schema):
    identifier = fields.Int(data_key='albumid', required=True)
    name = fields.Str(data_key='album', required=True)
    cover = fields.Str(data_key='pic', required=False)
    artist = fields.Str(data_key='artist', required=True)
    artistid = fields.Int(data_key='artistid', required=True)
    albuminfo = fields.Str(data_key='albuminfo', required=False)
    songs = fields.List(fields.Nested('MiguSongSchema'), data_key='musicList', allow_none=True, required=False)

    @post_load
    def create_model(self, data, **kwargs):
        return MiguAlbumModel(identifier=data.get('identifier'), name=unescape(data.get('name')),
                              artists=[MiguArtistModel(identifier=data.get('artistid'), name=data.get('artist'))],
                              desc=unescape(data.get('albuminfo', '')).replace('\n', '<br>'), cover=data.get('cover'), songs=[],
                              _songs=data.get('songs'))


class MiguArtistSchema(Schema):
    identifier = fields.Int(data_key='id', required=True)
    name = fields.Str(data_key='name', required=True)
    pic = fields.Str(data_key='pic', required=False)
    pic300 = fields.Str(data_key='pic300', required=False)
    desc = fields.Str(data_key='info', required=False)

    @post_load
    def create_model(self, data, **kwargs):
        return MiguArtistModel(identifier=data.get('identifier'), name=unescape(data.get('name')), cover=data.get('pic300'),
                               desc=data.get('desc'), info=data.get('desc'))


from .models import MiguSongModel, MiguAlbumModel, MiguArtistModel, MiguPlaylistModel
