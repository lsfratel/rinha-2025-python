from restcraft.core import Application

from .api import urls


def create_app():
    app = Application(urls.urls)

    return app
