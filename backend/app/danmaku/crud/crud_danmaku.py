from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy_crud_plus import CRUDPlus

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


class CRUDDanmakuMessage(CRUDPlus[DanmakuMessage]):
    async def create(self, db: AsyncSession, obj: DanmakuMessage) -> None:
        db.add(obj)
        await db.flush()

    async def get_by_room(self, db: AsyncSession, room_id: int, limit: int = 100) -> Select:
        return await self.select_order('timestamp', 'desc', room_id=room_id, limit=limit)


class CRUDInteractWord(CRUDPlus[InteractWord]):
    async def create(self, db: AsyncSession, obj: InteractWord) -> None:
        db.add(obj)
        await db.flush()

    async def get_by_room(self, db: AsyncSession, room_id: int, limit: int = 100) -> Select:
        return await self.select_order('timestamp', 'desc', room_id=room_id, limit=limit)


class CRUDGuardBuy(CRUDPlus[GuardBuy]):
    async def create(self, db: AsyncSession, obj: GuardBuy) -> None:
        db.add(obj)
        await db.flush()

    async def get_by_room(self, db: AsyncSession, room_id: int, limit: int = 100) -> Select:
        return await self.select_order('timestamp', 'desc', room_id=room_id, limit=limit)


class CRUDSuperChatMessage(CRUDPlus[SuperChatMessage]):
    async def create(self, db: AsyncSession, obj: SuperChatMessage) -> None:
        db.add(obj)
        await db.flush()

    async def get_by_room(self, db: AsyncSession, room_id: int, limit: int = 100) -> Select:
        return await self.select_order('timestamp', 'desc', room_id=room_id, limit=limit)


class CRUDSendGift(CRUDPlus[SendGift]):
    async def create(self, db: AsyncSession, obj: SendGift) -> None:
        db.add(obj)
        await db.flush()

    async def get_by_room(self, db: AsyncSession, room_id: int, limit: int = 100) -> Select:
        return await self.select_order('timestamp', 'desc', room_id=room_id, limit=limit)


class CRUDOnlineCount(CRUDPlus[OnlineCount]):
    async def create(self, db: AsyncSession, obj: OnlineCount) -> None:
        db.add(obj)
        await db.flush()

    async def get_by_room(self, db: AsyncSession, room_id: int, limit: int = 100) -> Select:
        return await self.select_order('timestamp', 'desc', room_id=room_id, limit=limit)


class CRUDRoomBlockMsg(CRUDPlus[RoomBlockMsg]):
    async def create(self, db: AsyncSession, obj: RoomBlockMsg) -> None:
        db.add(obj)
        await db.flush()

    async def get_by_room(self, db: AsyncSession, room_id: int, limit: int = 100) -> Select:
        return await self.select_order('timestamp', 'desc', room_id=room_id, limit=limit)


class CRUDAnchorLotStart(CRUDPlus[AnchorLotStart]):
    async def create(self, db: AsyncSession, obj: AnchorLotStart) -> None:
        db.add(obj)
        await db.flush()

    async def get_by_room(self, db: AsyncSession, room_id: int, limit: int = 100) -> Select:
        return await self.select_order('timestamp', 'desc', room_id=room_id, limit=limit)


class CRUDAnchorLotAward(CRUDPlus[AnchorLotAward]):
    async def create(self, db: AsyncSession, obj: AnchorLotAward) -> None:
        db.add(obj)
        await db.flush()

    async def get_by_room(self, db: AsyncSession, room_id: int, limit: int = 100) -> Select:
        return await self.select_order('timestamp', 'desc', room_id=room_id, limit=limit)


danmaku_message_dao = CRUDDanmakuMessage(DanmakuMessage)
interact_word_dao = CRUDInteractWord(InteractWord)
guard_buy_dao = CRUDGuardBuy(GuardBuy)
super_chat_message_dao = CRUDSuperChatMessage(SuperChatMessage)
send_gift_dao = CRUDSendGift(SendGift)
online_count_dao = CRUDOnlineCount(OnlineCount)
room_block_msg_dao = CRUDRoomBlockMsg(RoomBlockMsg)
anchor_lot_start_dao = CRUDAnchorLotStart(AnchorLotStart)
anchor_lot_award_dao = CRUDAnchorLotAward(AnchorLotAward)
