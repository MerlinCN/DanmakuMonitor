import sqlalchemy as sa

from sqlalchemy.orm import Mapped, mapped_column

from backend.common.model import DataClassBase, id_key


class DanmakuMessage(DataClassBase):
    """弹幕消息表"""

    __tablename__ = 'danmaku_message'

    id: Mapped[id_key] = mapped_column(init=False)
    room_id: Mapped[int] = mapped_column(sa.BigInteger, index=True, comment='房间 ID')
    user_mid: Mapped[int] = mapped_column(sa.BigInteger, index=True, comment='用户 ID')
    user_name: Mapped[str] = mapped_column(sa.Text, index=True, comment='用户名')
    message: Mapped[str] = mapped_column(sa.Text, index=True, comment='弹幕内容')
    timestamp: Mapped[int] = mapped_column(sa.BigInteger, index=True, comment='发送时的 UNIX 毫秒时间戳')
    user_face: Mapped[str] = mapped_column(sa.Text, default='', comment='用户头像')
    fans_medal_name: Mapped[str] = mapped_column(sa.Text, default='', comment='粉丝勋章')
    fans_medal_level: Mapped[int] = mapped_column(default=0, comment='粉丝勋章等级')
    guard_level: Mapped[int] = mapped_column(default=0, comment='舰队等级')
    reply_mid: Mapped[int] = mapped_column(sa.BigInteger, default=0, comment='回复用户 ID')
    reply_uname: Mapped[str] = mapped_column(sa.Text, default='', comment='回复用户名')
    emotion: Mapped[dict] = mapped_column(sa.JSON, default_factory=dict, comment='表情相关信息')
    pic_emoticon: Mapped[str] = mapped_column(sa.Text, default='', comment='图片表情')
