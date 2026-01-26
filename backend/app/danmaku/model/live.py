import json
import time

from enum import Enum
from typing import Any, Self

import sqlalchemy as sa

from sqlalchemy.orm import Mapped, mapped_column

from backend.common.model import DataClassBase, id_key


class GuardLevel(int, Enum):
    """舰长等级: 0非舰长 1总督 2提督 3舰长"""

    NONE = 0
    GOVERNOR = 1
    LIEUTENANT = 2
    CAPTAIN = 3

    @classmethod
    def get_name(cls, level: int) -> str:
        level_map = {
            cls.NONE.value: '非舰长',
            cls.GOVERNOR.value: '总督',
            cls.LIEUTENANT.value: '提督',
            cls.CAPTAIN.value: '舰长',
        }
        return level_map.get(level, '未知等级')


class InteractType(int, Enum):
    """互动类型: 1进场 2关注 3分享"""

    ENTER = 1
    FOLLOW = 2
    SHARE = 3


class DanmakuMessage(DataClassBase):
    """弹幕消息表"""

    __tablename__ = 'danmaku_message'

    id: Mapped[id_key] = mapped_column(init=False)
    room_id: Mapped[int] = mapped_column(sa.BigInteger, index=True, comment='房间 ID')
    user_mid: Mapped[int] = mapped_column(sa.BigInteger, index=True, comment='用户 ID')
    user_name: Mapped[str] = mapped_column(sa.Text, index=True, comment='用户名')
    message: Mapped[str] = mapped_column(sa.Text, index=True, comment='弹幕内容')
    timestamp: Mapped[int] = mapped_column(sa.BigInteger, index=True, comment='UNIX 毫秒时间戳')
    user_face: Mapped[str] = mapped_column(sa.Text, default='', comment='用户头像')
    fans_medal_name: Mapped[str] = mapped_column(sa.Text, default='', comment='粉丝勋章')
    fans_medal_level: Mapped[int] = mapped_column(default=0, comment='粉丝勋章等级')
    guard_level: Mapped[GuardLevel] = mapped_column(sa.Enum(GuardLevel), default=GuardLevel.NONE, comment='舰队等级')
    reply_mid: Mapped[int] = mapped_column(sa.BigInteger, default=0, comment='回复用户 ID')
    reply_uname: Mapped[str] = mapped_column(sa.Text, default='', comment='回复用户名')
    emotion: Mapped[dict] = mapped_column(sa.JSON, default_factory=dict, comment='表情信息')
    pic_emoticon: Mapped[str] = mapped_column(sa.Text, default='', comment='图片表情')

    @classmethod
    def parse(cls, event_data: dict[str, Any]) -> Self:
        room_id = int(event_data['room_display_id'])
        if 'data' not in event_data or 'info' not in event_data['data']:
            return cls(room_id=room_id, user_mid=0, user_name='', message='', timestamp=0)

        info = event_data['data']['info']
        message = info[1]
        timestamp = info[0][4]
        user_mid = info[2][0]
        user_name = info[2][1]

        user_face = ''
        emotion: dict[str, str] = {}
        reply_mid = 0
        reply_uname = ''
        fans_medal_name = ''
        fans_medal_level = 0
        guard_level = GuardLevel.NONE
        pic_emoticon = ''

        extra = json.loads(info[0][15].get('extra', '{}'))
        emots = extra.get('emots', {})
        if emots:
            for k, v in emots.items():
                emotion[k] = v.get('url', '')
        if extra.get('show_reply', False):
            reply_mid = extra.get('reply_mid', 0)
            reply_uname = extra.get('reply_uname', '')

        if info[0][15]:
            user_face = info[0][15].get('user', {}).get('base', {}).get('face', '')

        if info[3]:
            fans_medal_name = info[3][1]
            fans_medal_level = info[3][0]
            guard_level = GuardLevel(info[3][10])

        pic_emoticon_data = info[0][13]
        if isinstance(pic_emoticon_data, dict):
            pic_emoticon = pic_emoticon_data.get('url', '')

        return cls(
            room_id=room_id,
            user_mid=user_mid,
            user_name=user_name,
            message=message,
            timestamp=timestamp,
            user_face=user_face,
            fans_medal_name=fans_medal_name,
            fans_medal_level=fans_medal_level,
            guard_level=guard_level,
            reply_mid=reply_mid,
            reply_uname=reply_uname,
            emotion=emotion,
            pic_emoticon=pic_emoticon,
        )

    def __str__(self) -> str:
        result = ''
        if self.guard_level.value:
            result += f'[{GuardLevel.get_name(self.guard_level.value)}]'
        if self.fans_medal_name and self.fans_medal_level:
            result += f'[{self.fans_medal_name}({self.fans_medal_level})]'
        result += f'{self.user_name}:{self.message}'
        return result


class InteractWord(DataClassBase):
    """互动消息表"""

    __tablename__ = 'interact_word'

    id: Mapped[id_key] = mapped_column(init=False)
    room_id: Mapped[int] = mapped_column(sa.BigInteger, index=True, comment='房间 ID')
    user_mid: Mapped[int] = mapped_column(sa.BigInteger, index=True, comment='用户 ID')
    user_name: Mapped[str] = mapped_column(sa.Text, index=True, comment='用户名')
    timestamp: Mapped[int] = mapped_column(sa.BigInteger, index=True, comment='UNIX 毫秒时间戳')
    msg_type: Mapped[InteractType] = mapped_column(
        sa.Enum(InteractType), default=InteractType.ENTER, comment='互动类型'
    )

    @classmethod
    def parse(cls, event_data: dict[str, Any]) -> Self:
        data = event_data['data']['data']
        return cls(
            room_id=int(event_data['room_display_id']),
            user_mid=data['uid'],
            user_name=data['uname'],
            msg_type=InteractType(data['msg_type']),
            timestamp=data['timestamp'],
        )


class GuardBuy(DataClassBase):
    """舰长购买表"""

    __tablename__ = 'guard_buy'

    id: Mapped[id_key] = mapped_column(init=False)
    room_id: Mapped[int] = mapped_column(sa.BigInteger, index=True, comment='房间 ID')
    user_mid: Mapped[int] = mapped_column(sa.BigInteger, index=True, comment='用户 ID')
    user_name: Mapped[str] = mapped_column(sa.Text, index=True, comment='用户名')
    timestamp: Mapped[int] = mapped_column(sa.BigInteger, index=True, comment='UNIX 毫秒时间戳')
    guard_level: Mapped[GuardLevel] = mapped_column(sa.Enum(GuardLevel), default=GuardLevel.CAPTAIN, comment='舰队等级')
    num: Mapped[int] = mapped_column(default=0, comment='购买数量')
    price: Mapped[int] = mapped_column(default=0, comment='购买价格 CNY*1000')

    @classmethod
    def parse(cls, event_data: dict[str, Any]) -> Self:
        data = event_data['data']['data']
        return cls(
            room_id=int(event_data['room_display_id']),
            user_mid=data['uid'],
            user_name=data['username'],
            guard_level=GuardLevel(data['guard_level']),
            num=data['num'],
            price=data['price'],
            timestamp=int(time.time() * 1000),
        )


class SuperChatMessage(DataClassBase):
    """SuperChat 消息表"""

    __tablename__ = 'super_chat_message'

    id: Mapped[id_key] = mapped_column(init=False)
    room_id: Mapped[int] = mapped_column(sa.BigInteger, index=True, comment='房间 ID')
    user_mid: Mapped[int] = mapped_column(sa.BigInteger, index=True, comment='用户 ID')
    user_name: Mapped[str] = mapped_column(sa.Text, index=True, comment='用户名')
    timestamp: Mapped[int] = mapped_column(sa.BigInteger, index=True, comment='UNIX 毫秒时间戳')
    price: Mapped[int] = mapped_column(default=0, comment='CNY 价值')
    message: Mapped[str] = mapped_column(sa.Text, default='', comment='消息内容')
    duration: Mapped[int] = mapped_column(default=0, comment='消息持续时间')
    fans_medal_name: Mapped[str] = mapped_column(sa.Text, default='', comment='粉丝勋章')
    fans_medal_level: Mapped[int] = mapped_column(default=0, comment='粉丝勋章等级')
    guard_level: Mapped[GuardLevel] = mapped_column(sa.Enum(GuardLevel), default=GuardLevel.NONE, comment='舰队等级')
    user_face: Mapped[str] = mapped_column(sa.Text, default='', comment='用户头像')

    @classmethod
    def parse(cls, event_data: dict[str, Any]) -> Self:
        data = event_data['data']['data']
        return cls(
            room_id=int(event_data['room_display_id']),
            user_mid=data['uid'],
            user_name=data['user_info']['uname'],
            price=data['price'],
            message=data['message'],
            duration=data.get('time', 0),
            fans_medal_name=data['medal_info']['medal_name'],
            fans_medal_level=data['medal_info']['medal_level'],
            guard_level=GuardLevel(data['medal_info']['guard_level']),
            user_face=data['user_info']['face'],
            timestamp=int(time.time() * 1000),
        )


class SendGift(DataClassBase):
    """礼物消息表"""

    __tablename__ = 'send_gift'

    id: Mapped[id_key] = mapped_column(init=False)
    room_id: Mapped[int] = mapped_column(sa.BigInteger, index=True, comment='房间 ID')
    user_mid: Mapped[int] = mapped_column(sa.BigInteger, index=True, comment='用户 ID')
    user_name: Mapped[str] = mapped_column(sa.Text, index=True, comment='用户名')
    timestamp: Mapped[int] = mapped_column(sa.BigInteger, index=True, comment='UNIX 毫秒时间戳')
    gift_name: Mapped[str] = mapped_column(sa.Text, default='', comment='礼物名称')
    gift_num: Mapped[int] = mapped_column(default=0, comment='礼物数量')
    gift_price: Mapped[int] = mapped_column(default=0, comment='礼物价格 CNY*1000')

    @classmethod
    def parse(cls, event_data: dict[str, Any]) -> Self:
        data = event_data['data']['data']
        return cls(
            room_id=int(event_data['room_display_id']),
            user_mid=data['uid'],
            user_name=data['uname'],
            gift_name=data['giftName'],
            gift_num=data['num'],
            gift_price=data['price'],
            timestamp=int(time.time() * 1000),
        )


class OnlineCount(DataClassBase):
    """在线人数表"""

    __tablename__ = 'online_count'

    id: Mapped[id_key] = mapped_column(init=False)
    room_id: Mapped[int] = mapped_column(sa.BigInteger, index=True, comment='房间 ID')
    timestamp: Mapped[int] = mapped_column(sa.BigInteger, index=True, comment='UNIX 毫秒时间戳')
    online_count: Mapped[int] = mapped_column(default=0, comment='在线人数')

    @classmethod
    def parse(cls, event_data: dict[str, Any]) -> Self:
        data = event_data['data']['data']
        return cls(
            room_id=int(event_data['room_display_id']),
            online_count=data['count'],
            timestamp=int(time.time() * 1000),
        )


class RoomBlockMsg(DataClassBase):
    """房间禁言表"""

    __tablename__ = 'room_block_msg'

    id: Mapped[id_key] = mapped_column(init=False)
    room_id: Mapped[int] = mapped_column(sa.BigInteger, index=True, comment='房间 ID')
    user_mid: Mapped[int] = mapped_column(sa.BigInteger, index=True, comment='用户 ID')
    user_name: Mapped[str] = mapped_column(sa.Text, index=True, comment='用户名')
    timestamp: Mapped[int] = mapped_column(sa.BigInteger, index=True, comment='UNIX 毫秒时间戳')

    @classmethod
    def parse(cls, event_data: dict[str, Any]) -> Self:
        data = event_data['data']['data']
        return cls(
            room_id=int(event_data['room_display_id']),
            user_mid=data['uid'],
            user_name=data['uname'],
            timestamp=int(time.time() * 1000),
        )


class AnchorLotStart(DataClassBase):
    """天选之人开始表"""

    __tablename__ = 'anchor_lot_start'

    id: Mapped[id_key] = mapped_column(init=False)
    room_id: Mapped[int] = mapped_column(sa.BigInteger, index=True, comment='房间 ID')
    lot_id: Mapped[int] = mapped_column(sa.BigInteger, index=True, comment='天选 ID')
    timestamp: Mapped[int] = mapped_column(sa.BigInteger, index=True, comment='UNIX 毫秒时间戳')
    danmaku: Mapped[str] = mapped_column(sa.Text, default='', comment='弹幕')
    gift_name: Mapped[str] = mapped_column(sa.Text, default='', comment='礼物名称')
    gift_num: Mapped[int] = mapped_column(default=0, comment='礼物数量')
    require_text: Mapped[str] = mapped_column(sa.Text, default='', comment='要求文本')

    @classmethod
    def parse(cls, event_data: dict[str, Any]) -> Self:
        data = event_data['data']['data']
        return cls(
            room_id=int(event_data['room_display_id']),
            lot_id=data['id'],
            danmaku=data['danmu'],
            gift_name=data['gift_name'],
            gift_num=data['gift_num'],
            require_text=data['require_text'],
            timestamp=int(time.time() * 1000),
        )


class AnchorLotAward(DataClassBase):
    """天选之人中奖表"""

    __tablename__ = 'anchor_lot_award'

    id: Mapped[id_key] = mapped_column(init=False)
    room_id: Mapped[int] = mapped_column(sa.BigInteger, index=True, comment='房间 ID')
    lot_id: Mapped[int] = mapped_column(sa.BigInteger, index=True, comment='天选 ID')
    user_mid: Mapped[int] = mapped_column(sa.BigInteger, index=True, comment='用户 ID')
    user_name: Mapped[str] = mapped_column(sa.Text, index=True, comment='用户名')
    timestamp: Mapped[int] = mapped_column(sa.BigInteger, index=True, comment='UNIX 毫秒时间戳')
    award_name: Mapped[str] = mapped_column(sa.Text, default='', comment='奖励名称')
    award_num: Mapped[int] = mapped_column(default=0, comment='奖励数量')

    @classmethod
    def parse(cls, event_data: dict[str, Any]) -> Self:
        data = event_data['data']['data']
        return cls(
            room_id=int(event_data['room_display_id']),
            lot_id=event_data['data']['id'],
            user_mid=data['user_info']['uid'],
            user_name=data['user_info']['uname'],
            award_name=data['award_name'],
            award_num=data['award_num'],
            timestamp=int(time.time() * 1000),
        )
