from enum import StrEnum

from pydantic import ConfigDict, Field

from backend.app.danmaku.model.live import GuardLevel
from backend.common.schema import SchemaBase


class DanmakuSortField(StrEnum):
    TIMESTAMP = 'timestamp'
    FANS_MEDAL_LEVEL = 'fans_medal_level'
    GUARD_LEVEL = 'guard_level'


class SuperchatSortField(StrEnum):
    TIMESTAMP = 'timestamp'
    FANS_MEDAL_LEVEL = 'fans_medal_level'
    GUARD_LEVEL = 'guard_level'
    PRICE = 'price'


class SortOrder(StrEnum):
    ASC = 'asc'
    DESC = 'desc'


class DanmakuSearchFilters(SchemaBase):
    """弹幕搜索过滤参数"""

    start_date: int | None = Field(None, description='开始时间 (UNIX 毫秒时间戳)')
    end_date: int | None = Field(None, description='结束时间 (UNIX 毫秒时间戳)')
    user_mid: int | None = Field(None, description='用户 ID')
    user_name: str | None = Field(None, description='用户名 (模糊匹配)')
    message: str | None = Field(None, description='弹幕内容 (模糊匹配)')
    room_id: int | None = Field(None, description='房间 ID')
    fans_medal_name: str | None = Field(None, description='粉丝勋章名称 (模糊匹配)')
    guard_level: int | None = Field(None, description='舰长等级')
    fans_medal_level: int | None = Field(None, description='粉丝勋章等级 (大于等于)')
    sort_by: DanmakuSortField | None = Field(None, description='排序字段')
    sort_order: SortOrder | None = Field(None, description='排序方向')


class GetDanmakuDetail(SchemaBase):
    """弹幕详情"""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(description='弹幕 ID')
    room_id: int = Field(description='房间 ID')
    user_mid: int = Field(description='用户 ID')
    user_name: str = Field(description='用户名')
    message: str = Field(description='弹幕内容')
    user_face: str = Field(default='', description='用户头像')
    fans_medal_name: str = Field(default='', description='粉丝勋章')
    fans_medal_level: int = Field(default=0, description='粉丝勋章等级')
    guard_level: GuardLevel = Field(default=GuardLevel.NONE, description='舰队等级')
    reply_mid: int = Field(default=0, description='回复用户 ID')
    reply_uname: str = Field(default='', description='回复用户名')
    timestamp: int = Field(description='发送时的 UNIX 毫秒时间戳')
    emotion: dict[str, str] = Field(default_factory=dict, description='表情相关信息')
    pic_emoticon: str = Field(default='', description='图片表情')


class SuperchatSearchFilters(SchemaBase):
    """醒目留言搜索过滤参数"""

    start_date: int | None = Field(None, description='开始时间 (UNIX 毫秒时间戳)')
    end_date: int | None = Field(None, description='结束时间 (UNIX 毫秒时间戳)')
    user_mid: int | None = Field(None, description='用户 ID')
    user_name: str | None = Field(None, description='用户名 (模糊匹配)')
    message: str | None = Field(None, description='消息内容 (模糊匹配)')
    room_id: int | None = Field(None, description='房间 ID')
    sort_by: SuperchatSortField | None = Field(None, description='排序字段')
    sort_order: SortOrder | None = Field(None, description='排序方向')


class GetSuperchatDetail(SchemaBase):
    """醒目留言详情"""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(description='醒目留言 ID')
    room_id: int = Field(description='房间 ID')
    user_mid: int = Field(description='用户 ID')
    user_name: str = Field(description='用户名')
    user_face: str = Field(default='', description='用户头像')
    fans_medal_name: str = Field(default='', description='粉丝勋章')
    fans_medal_level: int = Field(default=0, description='粉丝勋章等级')
    guard_level: GuardLevel = Field(default=GuardLevel.NONE, description='舰队等级')
    message: str = Field(default='', description='消息内容')
    price: int = Field(default=0, description='价格 (CNY)')
    duration: int = Field(default=0, description='消息持续时间')
    timestamp: int = Field(description='发送时的 UNIX 毫秒时间戳')


class RoomBlockSortField(StrEnum):
    """房间禁言排序字段"""

    TIMESTAMP = 'timestamp'


class RoomBlockSearchFilters(SchemaBase):
    """房间禁言搜索过滤参数"""

    start_date: int | None = Field(None, description='开始时间 (UNIX 毫秒时间戳)')
    end_date: int | None = Field(None, description='结束时间 (UNIX 毫秒时间戳)')
    user_mid: int | None = Field(None, description='用户 ID')
    user_name: str | None = Field(None, description='用户名 (模糊匹配)')
    room_id: int | None = Field(None, description='房间 ID')
    sort_by: RoomBlockSortField | None = Field(None, description='排序字段')
    sort_order: SortOrder | None = Field(None, description='排序方向')


class GetRoomBlockDetail(SchemaBase):
    """房间禁言详情"""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(description='禁言记录 ID')
    room_id: int = Field(description='房间 ID')
    user_mid: int = Field(description='被禁言用户 ID')
    user_name: str = Field(description='被禁言用户名')
    timestamp: int = Field(description='禁言时的 UNIX 毫秒时间戳')
