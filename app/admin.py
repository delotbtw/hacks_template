from fastapi import FastAPI
from sqladmin import Admin, ModelView
from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request

from app.core.config import get_settings
from app.core.db import engine
from app.models.item import Item


class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        s = get_settings()
        if form.get("username") == s.admin_user and form.get("password") == s.admin_password:
            request.session.update({"admin": True})
            return True
        return False

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        return bool(request.session.get("admin"))


class ItemAdmin(ModelView, model=Item):
    column_list = [Item.id, Item.name, Item.created_at]


def setup_admin(app: FastAPI) -> None:
    auth = AdminAuth(secret_key=get_settings().admin_secret_key)
    admin = Admin(app, engine, authentication_backend=auth)
    admin.add_view(ItemAdmin)
