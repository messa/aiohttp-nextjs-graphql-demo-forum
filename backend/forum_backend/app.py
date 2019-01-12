from aiohttp import web
from aiohttp_graphql import GraphQLView
import argparse
import logging

from .views import all_routes
from .graphql import Schema


def main():
    p = argparse.ArgumentParser()
    args = p.parse_args()
    logging.basicConfig(level=logging.DEBUG)
    app = get_app()
    web.run_app(app)


def get_app():
    app = web.Application()
    app.router.add_routes(all_routes)
    GraphQLView.attach(app, schema=Schema, graphiql=True, route_path='/api/graphql')
    # schema: The GraphQLSchema object that you want the view to execute when it gets a valid request.
    return app
