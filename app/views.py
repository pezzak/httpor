from aiohttp_jinja2 import template
import aiohttp

@template('index.jinja')
async def index(request):
    """
    This is the view handler for the "/" url.

    :param request: the request object see http://aiohttp.readthedocs.io/en/stable/web_reference.html#request
    :return: context for the template.
    """
    # Note: we return a dict not a response because of the @template decorator
    return {
        'title': request.app['alarm_status'],
        'intro': "Success! you've setup a basic aiohttp app.",
    }

async def get_resources(request):
    resources = request.app['settings'].enabled_resources
    return aiohttp.web.json_response(resources)
