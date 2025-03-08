#(©)Codexbotz
#rymme





from aiohttp import web

routes = web.RouteTableDef()

@routes.get("/", allow_head=True)
async def root_route_handler(request):
    return web.json_response("The bot has restarted successfully. Return to the channel to find the series you want to watch")
