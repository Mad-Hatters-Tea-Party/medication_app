from typing import List, Any

from fastapi import Depends
from sqlalchemy import delete
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError

from models.data_access_schemas import SideEffectCreate
from models.data_models import SideEffect
from storage.database import get_db


class DataAccessOperations:
    def __ini__(self):
        self.db = Depends(get_db)

    async def insert_side_effect(self, incoming_side_effect: SideEffectCreate):

        data_to_insert = SideEffect(**incoming_side_effect.dict())
        return self.insert_to_db(data_to_insert)

    async def read_side_effects_for_user(self, user_id: str):
        return self.query_db(select(SideEffect).where(SideEffect.user_id == user_id))

    async def read_side_effects_for_medication(self, medication_id: str):
        return self.query_db(select(SideEffect).where(SideEffect.medication_id == medication_id))

    async def delete_side_effect(self, side_effect_id: int):
        return self.delete_from_db(delete(SideEffect).where(SideEffect.side_effect_id == side_effect_id))

    async def insert_to_db(self, data_to_insert: dict):
        try:
            self.db.add(data_to_insert)
            await self.db.commit()
            await self.db.refresh(data_to_insert)

            return DataAccessOperations.DataAccessResult(success=True, result_data=[data_to_insert])

        except SQLAlchemyError as e:
            await self.db.rollback()
            return DataAccessOperations.DataAccessResult(success=False, result_data=None)

    async def query_db(self, query: Any):
        try:
            result = await self.db.execute(query)
            return DataAccessOperations.DataAccessResult(success=True, result_data=result.scalars().all())
        except SQLAlchemyError as e:
            return DataAccessOperations.DataAccessResult(success=False, result_data=None)

    async def delete_from_db(self, query: Any):
        try:
            result = await self.db.execute(query)
            await self.db.commit()

            if result.rowcount > 0:
                return DataAccessOperations.DataAccessResult(success=True, result_data=None)
            else:
                return DataAccessOperations.DataAccessResult(success=False, result_data=None)
        except SQLAlchemyError as e:
            await self.db.rollback()
            return DataAccessOperations.DataAccessResult(success=False, result_data=None)

    # POPO representing status of data access operations
    class DataAccessResult:
        def __init__(self, success: bool, result_data: List = None):
            self.success = success
            self.result_data = result_data
