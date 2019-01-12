from aiohttp import web
import argparse

from .views import all_routes


def main():
    p = argparse.ArgumentParser()
    args = p.parse_args()
    app = get_app()
    web.run_app(app)


def get_app():
    app = web.Application()
    app.router.add_routes(all_routes)
    return app
