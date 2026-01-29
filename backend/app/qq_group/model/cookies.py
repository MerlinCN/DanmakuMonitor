"""B站 Cookies 模型"""

from datetime import datetime

import sqlalchemy as sa

from sqlalchemy.orm import Mapped, mapped_column

from backend.common.model import DataClassBase, TimeZone
from backend.core.conf import settings
from backend.utils.timezone import timezone


class Cookies(DataClassBase):
    """B站登录 Cookies 存储表（单例）"""

    __tablename__ = 'cookies'
    __table_args__ = (
        sa.CheckConstraint('id = 1', name='single_row'),
        {'schema': settings.QQ_GROUP_SCHEMA, 'comment': 'B站登录 Cookies 存储表（单例）'},
    )

    id: Mapped[int] = mapped_column(
        sa.Integer,
        primary_key=True,
        init=False,
        insert_default=1,
        comment='主键 ID（固定为1）',
    )
    sessdata: Mapped[str | None] = mapped_column(
        sa.Text,
        default=None,
        comment='B站 SESSDATA cookie',
    )
    bili_jct: Mapped[str | None] = mapped_column(
        sa.Text,
        default=None,
        comment='B站 bili_jct cookie',
    )
    buvid3: Mapped[str | None] = mapped_column(
        sa.Text,
        default=None,
        comment='B站 buvid3 cookie',
    )
    buvid4: Mapped[str | None] = mapped_column(
        sa.Text,
        default=None,
        comment='B站 buvid4 cookie',
    )
    dedeuserid: Mapped[str | None] = mapped_column(
        sa.Text,
        default=None,
        comment='B站用户ID',
    )
    ac_time_value: Mapped[str | None] = mapped_column(
        sa.Text,
        default=None,
        comment='B站 ac_time_value cookie',
    )
    created_at: Mapped[datetime] = mapped_column(
        TimeZone,
        init=False,
        default_factory=timezone.now,
        comment='创建时间',
    )
    updated_at: Mapped[datetime] = mapped_column(
        TimeZone,
        init=False,
        default_factory=timezone.now,
        onupdate=timezone.now,
        comment='更新时间',
    )
