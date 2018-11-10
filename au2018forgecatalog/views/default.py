from pyramid.view import view_config
import os, requests

# ////////////////////////////////////////////////////////////////////////////
# Helper Functions
# ////////////////////////////////////////////////////////////////////////////

# Get Credentials From Settings
def getCredentials(settings, software):
    if software == "Forge":
        credentials = {
            "id": os.environ[settings["forge_client"]],
            "secret": os.environ[settings["forge_secret"]],
        }
    if software == "FLC":
        credentials = {
            "tenant": os.environ[settings["flc_tenant_id"]],
            "id": os.environ[settings["flc_user_id"]],
            "secret": os.environ[settings["flc_password"]],
        }
    return credentials


# Get Forge Token from Forge Identity Service
def getForgeToken(client_id, client_secret):
    base_url = "https://developer.api.autodesk.com"
    url_auth = base_url + "/authentication/v1/authenticate"

    data = {
        "grant_type": "client_credentials",
        "client_secret": client_secret,
        "client_id": client_id,
        "scope": "viewables:read",
    }

    r = requests.post(url_auth, data=data)

    if 200 == r.status_code:
        return r.json()

    return None


# Get FLC Token from FLC
def getFLCToken(tenant, client_id, client_secret):
    base_url = "https://" + tenant + ".autodeskplm360.net"
    url_auth = base_url + "/rest/auth/1/login"

    data = {"userID": client_id, "password": client_secret}

    r = requests.post(url_auth, data=data)

    if 200 == r.status_code:
        return r.json()

    return None


# ////////////////////////////////////////////////////////////////////////////
# Views
# ////////////////////////////////////////////////////////////////////////////

# @view_config(route_name='home', renderer='../templates/mytemplate.jinja2')
@view_config(route_name="home", renderer="../templates/bootstraptest.jinja2")
def my_view(request):
    return {"project": "au2018forgecatalog"}


# /forge/token
@view_config(route_name="forge-token", renderer="json")
def forge_token(request):
    credentials = getCredentials(request.registry.settings, "Forge")
    return getForgeToken(credentials["id"], credentials["secret"])


# /flc/token
@view_config(route_name="flc-token", render="json")
def flc_token(request):
    credentials = getCredentials(request.registry.settings, "FLC")
    return getFLCToken(credentials["tenant"], credentials["id"], credentials["secret"])

