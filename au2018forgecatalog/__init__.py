import os
from pyramid.config import Configurator


def main(global_config, **settings):
    flc_tenant_id = os.environ.get('FLC_TENANT_ID')
    settings['flc_tenant_id'] = flc_tenant_id
    flc_user_id = os.environ.get('FLC_USER_ID')
    settings['flc_user_id'] = flc_user_id
    flc_password = os.environ.get('FLC_PASSWORD')
    settings['flc_password'] = flc_password
    forge_client = os.environ.get('FORGE_CLIENT')
    settings['forge_client'] = forge_client
    forge_secret = os.environ.get('FORGE_SECRET')
    settings['forge_secret'] = forge_secret
    forge_bucket_key = os.environ.get('FORGE_BUCKET_KEY')
    settings['forge_bucket_key'] = forge_bucket_key
    """ This function returns a Pyramid WSGI application.
    """
    with Configurator(settings=settings) as config:
        config.include('pyramid_jinja2')
        config.include('.routes')
        config.scan()
    return config.make_wsgi_app()
