from sqlalchemy.future import select
from sqlalchemy.orm import class_mapper
from sqlalchemy import update, insert, delete
from src.core.db.session import session, set_session_context, reset_session_context


class DataProcessing:
    def __init__(self):
        self.session = session
        self.set_session_context = set_session_context
        self.reset_session_context = reset_session_context

    async def save_data(self, model, data):
        context = self.set_session_context("some_context")
        try:
            async with self.session() as db:
                insert_stmt = insert(model).values(**data)
                await db.execute(insert_stmt)
                await db.commit()
        finally:
            self.reset_session_context(context)

    async def get_data_from_model_filter(self, model, **kwargs):
        context = self.set_session_context("some_context")
        try:
            async with self.session() as db:
                query = select(model)
                for field_name, field_value in kwargs.items():
                    if hasattr(model, field_name):
                        query = query.where(getattr(model, field_name) == field_value)
                    else:
                        # Handle unsupported fields
                        raise ValueError(f"Unsupported field: {field_name}")
                result = await db.execute(query)
                record = result.scalars().first()
                return record
        finally:
            self.reset_session_context(context)

    async def get_data_all_from_model_filter(self, model, **kwargs):
        context = self.set_session_context("some_context")
        try:
            async with self.session() as db:
                query = select(model)
                for field_name, field_value in kwargs.items():
                    if hasattr(model, field_name):
                        query = query.where(getattr(model, field_name) == field_value)
                    else:
                        raise ValueError(f"Unsupported field: {field_name}")
                result = await db.execute(query)
                records = result.scalars().all()
                return records
        finally:
            self.reset_session_context(context)

    async def get_data_from_model_all(self, model):
        context = self.set_session_context("some_context")
        try:
            async with self.session() as db:
                query = select(model)
                result = await db.execute(query)
                records = result.scalars().all()
                return records
        finally:
            self.reset_session_context(context)

    async def update_data(self, model, update_data, **kwargs):
        context = self.set_session_context("some_context")
        try:
            async with self.session() as db:
                mapper = class_mapper(model)
                query = update(model).values(update_data)
                for field_name, field_value in kwargs.items():
                    if field_name in mapper.columns:
                        query = query.where(getattr(model, field_name) == field_value)
                    else:
                        raise ValueError(f"Unsupported field: {field_name}")
                await db.execute(query)
                await db.commit()
        finally:
            self.reset_session_context(context)

    async def delete_data(self, model, **kwargs):
        context = self.set_session_context("some_context")
        try:
            async with self.session() as db:
                mapper = class_mapper(model)
                query = delete(model)
                for field_name, field_value in kwargs.items():
                    if field_name in mapper.columns:
                        query = query.where(getattr(model, field_name) == field_value)
                    else:
                        # Handle unsupported fields
                        raise ValueError(f"Unsupported field: {field_name}")

                await db.execute(query)
                await db.commit()
        finally:
            self.reset_session_context(context)
