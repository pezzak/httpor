import base64
from pathlib import Path

import aiohttp_jinja2
import jinja2
from aiohttp import web

import aiohttp_session
from aiohttp_session.cookie_storage import EncryptedCookieStorage

from .settings import Settings
from .views import index

from .workers.httporworker import HttporWorker
import asyncio

THIS_DIR = Path(__file__).parent
BASE_DIR = THIS_DIR.parent


def setup_routes(app):
    app.router.add_get('/', index, name='index')

# async def startup(app: web.Application):
#     app['httpor_worker'] = 'on'

# async def cleanup(app: web.Application):
#     app['httpor_worker'] = 'off'

# class WorkerMixin(object):
#     async def init_backgroud_worker(self, app):
#         app['background_worker'] = app.loop.create_task(self._create_background_worker(app))

#     async def cleanup_backgroud_worker(self, app):
#         app['background_worker'].cancel()
#         await app['background_worker']

#     async def _create_background_worker(self, app):
#         httpor_worker = HttporWorker(app)
#         try:
#             await httpor_worker.run()
#         except asyncio.CancelledError:
#             pass

# class Main(WorkerMixin):
#     def __init__(self):
#         self.app = web.Application()
#         settings = Settings()
#         self.app.update(
#             name='httpor',
#             settings=settings
#         )
#         self.app.on_startup.append(self.init_backgroud_worker)
#         # self.app.on_startup.append(self._create_background_worker)
#         setup_routes(self.app)

#     def app(self):
#         return self.app

# def create_app():
#     main = Main()
#     return main.app()

async def background_worker(app):
    httpor_worker = HttporWorker(app)
    try:
        await httpor_worker.run()
    except asyncio.CancelledError:
        pass


async def start_background_tasks(app):
    app['background_worker'] = app.loop.create_task(background_worker(app))

async def cleanup_background_tasks(app):
    app['background_worker'].cancel()
    await app['background_worker']

def create_app():
    app = web.Application()
    settings = Settings()
    app.update(
        settings=settings
    )

    jinja2_loader = jinja2.FileSystemLoader(str(THIS_DIR / 'templates'))
    aiohttp_jinja2.setup(app, loader=jinja2_loader)

    secret_key = base64.urlsafe_b64decode(settings.COOKIE_SECRET)
    aiohttp_session.setup(app, EncryptedCookieStorage(secret_key))

    app.on_startup.append(start_background_tasks)
    app.on_cleanup.append(cleanup_background_tasks)

    setup_routes(app)
    return app
