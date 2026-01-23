import asyncio

from bilibili_api import Credential, login_v2
from bilibili_api.login_v2 import QrCodeLoginChannel, QrCodeLoginEvents
from bilibili_api.utils.picture import Picture


class LoginService:
    """B站登录服务类"""

    def __init__(self) -> None:
        self._qrcode_login: login_v2.QrCodeLogin | None = None
        self._credential: Credential | None = None

    @property
    def credential(self) -> Credential | None:
        return self._credential

    @credential.setter
    def credential(self, value: Credential | None) -> None:
        self._credential = value

    async def generate_qrcode(self, platform: QrCodeLoginChannel = QrCodeLoginChannel.WEB) -> Picture:
        """
        生成登录二维码

        :param platform: 登录平台，默认为 WEB
        :return: 二维码 Picture 对象
        """
        self._qrcode_login = login_v2.QrCodeLogin(platform=platform)
        await self._qrcode_login.generate_qrcode()
        return self._qrcode_login.get_qrcode_picture()

    def get_qrcode_terminal(self) -> str:
        """
        获取终端二维码字符串，用于终端展示

        :raises ValueError: 二维码未生成时抛出
        """
        if not self._qrcode_login or not self._qrcode_login.has_qrcode():
            raise ValueError('二维码未生成，请先调用 generate_qrcode')
        return self._qrcode_login.get_qrcode_terminal()

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
            await asyncio.sleep(poll_interval)

        return self.get_credential()


login_service: LoginService = LoginService()
