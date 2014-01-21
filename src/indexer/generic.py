import time
from indexer.base.block import BaseBlockModel
from indexer.base.fields import IntegerField, LongLongField, UuidField, CharField, CharArrayField
from indexer.base.indexes import InfiniteIndex


class SocialEventListBlockModel(BaseBlockModel):
    _fields = \
        [ ('user_id',  UuidField())
        , ('post_id',  UuidField())
        , ('id',       IntegerField())
        , ('prev_p',   IntegerField())
        , ('next_p',   IntegerField())
        , ('skip',     CharField())
        ]


class SocialEventList(InfiniteIndex):

    def __init__(self, **kwargs):
        kwargs.pop('block_class', None)
        super(SocialEventList, self).__init__(SocialEventListBlockModel, **kwargs)

    def __repr__(self):
        return 'Block: id=%d' % self.id

    def append(self, user_id, post_id, last_post_id=0, bytes=False):
        block = self.block_class(user_id, post_id, self.p_end + 1, last_post_id, 0, '\0', _bytes=bytes)
        return super(SocialEventList, self).append(block)

    def search_by_user_ids(self, user_last_post, start_p):
        user_last_post.sort(key=lambda v: v[1])
        col_offset = self.get_field('').padding
