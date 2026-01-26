import sqlalchemy as sa

from sqlalchemy.orm import Mapped, mapped_column

from backend.common.model import DataClassBase


class Credential(DataClassBase):
    """B站凭证表（单例，id固定为1）"""

    __tablename__ = 'bilibili_credential'

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True, insert_default=1, init=False)
    sessdata: Mapped[str] = mapped_column(sa.Text, comment='SESSDATA')
    bili_jct: Mapped[str] = mapped_column(sa.Text, comment='bili_jct')
    buvid3: Mapped[str | None] = mapped_column(sa.Text, default=None, comment='buvid3')
    buvid4: Mapped[str | None] = mapped_column(sa.Text, default=None, comment='buvid4')
    dedeuserid: Mapped[str | None] = mapped_column(sa.Text, default=None, comment='DedeUserID')
    ac_time_value: Mapped[str | None] = mapped_column(sa.Text, default=None, comment='ac_time_value')
