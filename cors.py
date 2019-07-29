from aiohttp import web

ALLOWED_HEADERS = ','.join((
    'content-type',
    'accept',
    'origin',
    'authorization',
    'x-requested-with',
    'x-csrftoken',
    ))


def set_cors_headers(request, response):
    response.headers['Access-Control-Allow-Origin'] = request.headers.get('Origin', '*')
    response.headers['Access-Control-Allow-Methods'] = request.method
    response.headers['Access-Control-Allow-Headers'] = ALLOWED_HEADERS
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    return response


@web.middleware
async def cors_factory(request, handler):
    if request.method == 'OPTIONS':
        return set_cors_headers(request, web.Response())
    else:
        return set_cors_headers(request, await handler(request))


