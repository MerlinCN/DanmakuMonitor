import asyncio
import sys

from collections.abc import Callable
from io import StringIO
from typing import Any, TypeVar

import qrcode

from bilibili_api import Credential, live, login_v2
from bilibili_api.login_v2 import QrCodeLoginChannel, QrCodeLoginEvents
from bilibili_api.utils.picture import Picture
from loguru import logger

from backend.app.danmaku.crud.crud_credential import credential_dao
from backend.app.danmaku.crud.crud_danmaku import (
    anchor_lot_award_dao,
    anchor_lot_start_dao,
    danmaku_message_dao,
    guard_buy_dao,
    interact_word_dao,
    online_count_dao,
    room_block_msg_dao,
    send_gift_dao,
    super_chat_message_dao,
)
from backend.app.danmaku.model import (
    AnchorLotAward,
    AnchorLotStart,
    DanmakuMessage,
    GuardBuy,
    InteractWord,
    OnlineCount,
    RoomBlockMsg,
    SendGift,
    SuperChatMessage,
)
from backend.core.conf import settings
from backend.database.db import async_db_session

# 默认终端二维码版本（1-40，数字越小二维码越小）
DEFAULT_QR_VERSION = 1
# 默认边框宽度
DEFAULT_QR_BORDER = 1
T = TypeVar('T')


class RoomHandler:
    def __init__(self, room_id: int, credential: Credential) -> None:
        self.room = live.LiveDanmaku(room_id, credential=credential, max_retry=sys.maxsize)
        self.room.logger = logger
        self.room_id = room_id

    @property
    def on(self) -> Any:
        """
        获取房间的事件处理器

        :return: 房间的事件处理器对象
        """
        return self.room.on

    async def connect(self) -> None:
        await self.room.connect()

    async def disconnect(self) -> None:
        await self.room.disconnect()


class Monitor:
    def __init__(self, credential: Credential) -> None:
        self.credential = credential
        self.rooms = [
            RoomHandler(room_id, credential=self.credential) for room_id in settings.BILIBILI_MONITOR_ROOM_IDS
        ]

    def on(self, event_type: str) -> Callable[[Callable[[dict], Any]], Callable[[dict], Any]]:
        """
        注册事件处理器的装饰器工厂

        :param event_type: 事件类型
        :return: 装饰器函数
        """

        def decorator(func: Callable[[dict], Any]) -> Callable[[dict], Any]:
            async def wrapper(event: dict) -> None:
                try:
                    await func(event)
                except Exception:
                    import traceback

                    logger.error(f'{event_type} 处理错误:\n{traceback.format_exc()}\n事件数据: {event}')

            # 为所有房间注册事件处理函数
            for room in self.rooms:
                room.on(event_type)(wrapper)
            return func

        return decorator

    async def run(self) -> None:
        """
        运行监控器，连接所有房间并保持运行直到停止

        使用 asyncio.Event 来优雅地等待停止信号，而不是轮询
        """
        # logger.info(f"开始连接房间: {', '.join([str(room.room_id) for room in self.rooms])}")
        await asyncio.gather(*[room.connect() for room in self.rooms])
        # await self._stop_event.wait()

    async def stop(self) -> None:
        """
        停止监控器，断开所有房间连接

        设置停止事件来通知 run 方法退出
        """
        logger.info(f'停止监控房间: {", ".join([str(room.room_id) for room in self.rooms])}')
        await asyncio.gather(*[room.disconnect() for room in self.rooms])


class BilibiliService:
    """B站登录服务类"""

    def __init__(self) -> None:
        self._qrcode_login: login_v2.QrCodeLogin | None = None
        self._credential: Credential | None = None
        self._qr_url: str | None = None  # 保存二维码 URL 用于自定义生成
        self._monitor: Monitor | None = None

    async def generate_qrcode(self, platform: QrCodeLoginChannel = QrCodeLoginChannel.WEB) -> Picture:
        """
        生成登录二维码

        :param platform: 登录平台，默认为 WEB
        :return: 二维码 Picture 对象
        """
        self._qrcode_login = login_v2.QrCodeLogin(platform=platform)
        await self._qrcode_login.generate_qrcode()
        self._qr_url = getattr(self._qrcode_login, '_QrCodeLogin__qr_link', None)
        return self._qrcode_login.get_qrcode_picture()

    def get_qrcode_terminal(self, version: int = DEFAULT_QR_VERSION, border: int = DEFAULT_QR_BORDER) -> str:
        """
        获取终端二维码字符串，用于终端展示

        :param version: 二维码版本 1-40，数字越小二维码越小，默认为 1
        :param border: 边框宽度，默认为 1
        :raises ValueError: 二维码未生成时抛出
        """
        if not self._qrcode_login or not self._qrcode_login.has_qrcode() or not self._qr_url:
            raise ValueError('二维码未生成，请先调用 generate_qrcode')

        qr = qrcode.QRCode(version=version, border=border)
        qr.add_data(self._qr_url)
        qr.make(fit=True)

        f = StringIO()
        qr.print_ascii(out=f, invert=True)
        return f.getvalue()

    async def check_state(self) -> QrCodeLoginEvents:
        """
        检查二维码扫描状态

        :raises ValueError: 二维码未生成时抛出
        """
        if not self._qrcode_login:
            raise ValueError('二维码未生成，请先调用 generate_qrcode')
        return await self._qrcode_login.check_state()

    def has_done(self) -> bool:
        if not self._qrcode_login:
            return False
        return self._qrcode_login.has_done()

    def get_credential(self) -> Credential:
        """
        获取登录凭证

        :raises ValueError: 登录未完成时抛出
        """
        if not self._qrcode_login or not self._qrcode_login.has_done():
            raise ValueError('登录未完成，无法获取凭证')
        self._credential = self._qrcode_login.get_credential()
        return self._credential

    def get_cookies(self) -> dict[str, str]:
        """
        获取登录后的 cookies

        :raises ValueError: 登录未完成时抛出
        """
        credential = self.get_credential()
        return credential.get_cookies()

    def clear(self) -> None:
        self._qrcode_login = None
        self._credential = None
        self._qr_url = None

    async def login_by_qrcode(
        self,
        platform: QrCodeLoginChannel = QrCodeLoginChannel.WEB,
        poll_interval: float = 1.0,
    ) -> Credential:
        """
        二维码登录完整流程，在终端打印二维码并轮询等待扫码

        :param platform: 登录平台
        :param poll_interval: 轮询间隔（秒）
        """

        await self.generate_qrcode(platform)
        print(self.get_qrcode_terminal())

        while not self.has_done():
            state = await self.check_state()
            if state == QrCodeLoginEvents.TIMEOUT:
                raise TimeoutError('二维码已过期')
            logger.debug(f'二维码扫描状态: {state}')
            await asyncio.sleep(poll_interval)

        return self.get_credential()

    async def auto_login(self) -> Credential:
        """
        自动登录：优先从数据库加载凭证，否则进行二维码登录并保存
        """
        async with async_db_session.begin() as db:
            db_credential = await credential_dao.get(db)
            if db_credential:
                self._credential = Credential(
                    sessdata=db_credential.sessdata,
                    bili_jct=db_credential.bili_jct,
                    buvid3=db_credential.buvid3,
                    buvid4=db_credential.buvid4,
                    dedeuserid=db_credential.dedeuserid,
                    ac_time_value=db_credential.ac_time_value,
                )
                if await self._credential.check_refresh():
                    await self._credential.refresh()
                return self._credential

            api_credential = await self.login_by_qrcode()
            self._credential = api_credential
            await credential_dao.upsert(
                db,
                sessdata=api_credential.sessdata or '',
                bili_jct=api_credential.bili_jct or '',
                buvid3=api_credential.buvid3,
                buvid4=api_credential.buvid4,
                dedeuserid=api_credential.dedeuserid,
                ac_time_value=api_credential.ac_time_value,
            )
            return api_credential

    def _create_event_handler(self, model_class: type[T], dao: Any) -> Callable[[dict], Any]:
        """
        创建通用的事件处理器

        :param model_class: 模型类，需要有 parse 类方法
        :param dao: DAO 对象，需要有 create 方法
        :return: 事件处理函数
        """

        async def handler(event: dict) -> None:
            obj = model_class.parse(event)
            async with async_db_session.begin() as db:
                await dao.create(db, obj)

        return handler

    async def register_event_handler(self) -> None:
        """
        注册所有事件处理器

        :raises ValueError: 如果未登录则抛出
        """
        if self._monitor is not None:
            await self._monitor.stop()
        if self._credential is None:
            raise ValueError('请先登录')
        self._monitor = Monitor(self._credential)

        # 事件类型到模型类和DAO的映射
        event_handlers = [
            ('DANMU_MSG', DanmakuMessage, danmaku_message_dao),
            ('INTERACT_WORD', InteractWord, interact_word_dao),
            ('GUARD_BUY', GuardBuy, guard_buy_dao),
            ('SUPER_CHAT_MESSAGE', SuperChatMessage, super_chat_message_dao),
            ('SEND_GIFT', SendGift, send_gift_dao),
            ('ONLINE_COUNT', OnlineCount, online_count_dao),
            ('ROOM_BLOCK_MSG', RoomBlockMsg, room_block_msg_dao),
            ('ANCHOR_LOT_START', AnchorLotStart, anchor_lot_start_dao),
            ('ANCHOR_LOT_AWARD', AnchorLotAward, anchor_lot_award_dao),
        ]

        for event_type, model_class, dao in event_handlers:
            handler = self._create_event_handler(model_class, dao)
            self._monitor.on(event_type)(handler)

    async def start(self) -> None:
        """
        启动监控器
        """
        await self.auto_login()
        await self.register_event_handler()
        await self._monitor.run()

    async def stop(self) -> None:
        """
        停止监控器
        """
        await self._monitor.stop()


bilibili_service: BilibiliService = BilibiliService()
