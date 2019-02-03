from aiohttp import web
from aiohttp_graphql import GraphQLView
import argparse
import logging
from graphql.execution.executors.asyncio import AsyncioExecutor as GQLAIOExecutor
from graphql_ws.aiohttp import AiohttpSubscriptionServer

from .graphql import Schema
from .model import Model
from .views import all_routes


def main():
    p = argparse.ArgumentParser()
    args = p.parse_args()
    logging.basicConfig(level=logging.DEBUG)
    app = get_app()
    web.run_app(app)


def get_app():
    model = Model()
    app = web.Application()
    app.router.add_routes(all_routes)
    app['model'] = model
    GraphQLView.attach(
        app,
        route_path='/api/graphql',
        schema=Schema,
        graphiql=True,
        enable_async=True,
        executor=GQLAIOExecutor())

    subscription_server = AiohttpSubscriptionServer(Schema)

    async def subscriptions(request):
        ws = web.WebSocketResponse(protocols=('graphql-ws',))
        await ws.prepare(request)
        await subscription_server.handle(ws)
        return ws

    app.router.add_get('/api/subscriptions', subscriptions)
    return app
