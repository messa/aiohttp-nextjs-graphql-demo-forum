from aiohttp import web


routes = web.RouteTableDef()


@routes.get('/')
async def index(request):
    return web.Response(text='Hello Aiohttp!')
