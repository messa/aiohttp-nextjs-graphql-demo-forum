from aiohttp import web
from aiohttp_graphql import GraphQLView
import argparse
import logging
from graphql.execution.executors.asyncio import AsyncioExecutor as GQLAIOExecutor
from graphql_ws.aiohttp import AiohttpSubscriptionServer

from .graphql import Schema
from .model import Model
from .views import all_routes


logger = logging.getLogger(__name__)


def main():
    p = argparse.ArgumentParser()
    args = p.parse_args()
    logging.basicConfig(level=logging.DEBUG)
    app = get_app()
    web.run_app(app)


def patch_gql_ws():
    # https://github.com/graphql-python/graphql-ws/pull/10
    from graphql_ws.base import BaseSubscriptionServer
    from graphql import graphql
    assert BaseSubscriptionServer.execute
    def patched_execute(self, request_context, params):
        logger.info('Executing %r', params)
        try:
            return graphql(
                self.schema,
                #**dict(params, allow_subscriptions=True))
                **dict(params, context_value=request_context, allow_subscriptions=True))
        except BaseException as e:
            logger.exception('XXX Failed: %r', e)
            raise e
    BaseSubscriptionServer.execute = patched_execute


patch_gql_ws()


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
        try:
            ws = web.WebSocketResponse(protocols=('graphql-ws',))
            await ws.prepare(request)
            await subscription_server.handle(ws, {'request': request})
            return ws
        except Exception as e:
            logger.exception('subscriptions failed: %r', e)
            raise e

    app.router.add_get('/api/subscriptions', subscriptions)
    return app
