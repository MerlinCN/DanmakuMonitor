"""黑名单模型"""

import uuid

from datetime import datetime

import sqlalchemy as sa

from sqlalchemy.orm import Mapped, mapped_column

from backend.common.model import DataClassBase, TimeZone
from backend.core.conf import settings
from backend.utils.timezone import timezone


class Blacklist(DataClassBase):
    """黑名单表"""

    __tablename__ = 'blacklist'
    __table_args__ = (
        sa.CheckConstraint(
            '(bilibili_uid IS NOT NULL) OR (qq_uid IS NOT NULL)',
            name='check_at_least_one_uid',
        ),
        {'schema': settings.QQ_GROUP_SCHEMA, 'comment': '黑名单表'},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        sa.UUID(as_uuid=True),
        primary_key=True,
        init=False,
        insert_default=uuid.uuid4,
        comment='主键 ID',
    )
    bilibili_uid: Mapped[int | None] = mapped_column(
        sa.BigInteger,
        index=True,
        default=None,
        comment='B站用户ID',
    )
    qq_uid: Mapped[int | None] = mapped_column(
        sa.BigInteger,
        index=True,
        default=None,
        comment='QQ用户ID',
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
