from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid.view import view_config
from pyramid.response import Response
from ..Memo import Memo
import requests, json, base64

# ////////////////////////////////////////////////////////////////////////////
# Helper Functions
# ////////////////////////////////////////////////////////////////////////////

# Get Credentials From Settings
def getCredentials(settings, software):
    if software == "Forge":
        credentials = {
            "id": settings["forge_client"],
            "secret": settings["forge_secret"],
        }
    if software == "FLC":
        credentials = {
            "tenant": settings["flc_tenant_id"],
            "id": settings["flc_user_id"],
            "secret": settings["flc_password"],
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
        "scope": "bucket:read data:read viewables:read data:write",
    }

    r = requests.post(url_auth, data=data)

    if 200 == r.status_code:
        return r.json()

    return None


# Memoize the Forge Token
@Memo(timeout=3580)
def getForgeTokenMemo(client_id, client_secret):
    return getForgeToken(client_id, client_secret)


# Get FLC Token from FLC
def getFLCToken(tenant, client_id, client_secret):
    base_url = "https://" + tenant + ".autodeskplm360.net"
    url_auth = base_url + "/rest/auth/1/login"

    data = {"userID": client_id, "password": client_secret}

    r = requests.post(url_auth, data=data)

    if 200 == r.status_code:
        return r.json()

    return None


# Memoize the FLC Token
@Memo(timeout=880)
def getFLCTokenMemo(tenant, client_id, client_secret):
    return getFLCToken(tenant, client_id, client_secret)


# Get FLC Categories from FLC
def getFLCPickList(token, pickListId):
    base_url = "https://" + token["customerToken"] + ".autodeskplm360.net"
    url_pick = base_url + "/api/rest/v1/setups/picklists"
    get_url = url_pick + "/" + pickListId

    headers = {
        "Cookie": "customer="
        + token["customerToken"]
        + ";JSESSIONID="
        + token["sessionid"]
    }

    r = requests.get(get_url, headers=headers)

    if 200 == r.status_code:
        return r.json()

    return None


# Get FLC Items
def getFLCProductsByCategory(token, category):
    base_url = "https://" + token["customerToken"] + ".autodeskplm360.net"
    get_url = (
        base_url + "/api/rest/v1/workspaces/65/items?includeRelationships=false&size=20"
    )

    headers = {
        "Cookie": "customer="
        + token["customerToken"]
        + ";JSESSIONID="
        + token["sessionid"]
    }

    r = requests.get(get_url, headers=headers)

    if 200 == r.status_code:
        products = r.json()
        matching_products = []
        if products["list"] is not None:
            for product in products["list"]["item"]:
                for field in product["metaFields"]["entry"]:
                    if (field["key"] == "PART_CATEGORY") and (
                        field["fieldData"]["label"] == category
                    ):
                        if (
                            product["details"]["workflowState"]["stateName"]
                            == "Released"
                        ):
                            matching_products.append(product)

        return matching_products
        # return products

    return None


# Get FLC Item
def getFLCProduct(token, dmsId):
    base_url = "https://" + token["customerToken"] + ".autodeskplm360.net"
    get_url = (
        base_url
        + "/api/rest/v1/workspaces/65/items/"
        + dmsId
        + "?includeRelationships=false"
    )

    headers = {
        "Cookie": "customer="
        + token["customerToken"]
        + ";JSESSIONID="
        + token["sessionid"]
    }

    r = requests.get(get_url, headers=headers)

    if 200 == r.status_code:
        return r.json()

    return None


# Get Forge Thumbnail
def getForgeThumbnail(token, urn):
    base_url = "https://developer.api.autodesk.com"
    get_url = base_url + "/modelderivative/v2/designdata/{}/thumbnail?{}"
    query = "width=400&height=400"
    headers = {"Authorization": "Bearer " + token["access_token"]}
    print(urn)
    print(get_url.format(urn, query))
    r = requests.get(get_url.format(urn, query), headers=headers)

    if 200 == r.status_code:
        return r.content

    return None


# ////////////////////////////////////////////////////////////////////////////
# Views
# ////////////////////////////////////////////////////////////////////////////

# @view_config(route_name='home', renderer='../templates/mytemplate.jinja2')
# @view_config(route_name="home", renderer="../templates/bootstraptest.jinja2")
# def my_view(request):
#    return {"project": "au2018forgecatalog"}


# /forge/token
@view_config(route_name="forge-token", renderer="json")
def forge_token(request):
    credentials = getCredentials(request.registry.settings, "Forge")
    return getForgeTokenMemo(credentials["id"], credentials["secret"])


# /flc/token
@view_config(route_name="flc-token", renderer="json")
def flc_token(request):
    credentials = getCredentials(request.registry.settings, "FLC")
    return getFLCTokenMemo(
        credentials["tenant"], credentials["id"], credentials["secret"]
    )


# /home
@view_config(route_name="home", renderer="../templates/home.jinja2")
# @view_config(route_name="home", renderer="json")
def home_view(request):
    try:
        credentials = getCredentials(request.registry.settings, "FLC")
        token = getFLCTokenMemo(
            credentials["tenant"], credentials["id"], credentials["secret"]
        )
        categories = getFLCPickList(token, "CUSTOM_LOOKUP_PART_CATEGORIES")

        if categories is None:
            raise HTTPNotFound()

        return categories

    except:
        raise HTTPNotFound()


# /category/{category}
@view_config(route_name="category", renderer="../templates/category.jinja2")
# @view_config(route_name="category", renderer="json")
def category_view(request):
    try:
        ret = {}
        category = request.matchdict["category"]
        credentials = getCredentials(request.registry.settings, "FLC")
        token = getFLCTokenMemo(
            credentials["tenant"], credentials["id"], credentials["secret"]
        )

        products = getFLCProductsByCategory(token, category)

        if products is None:
            raise HTTPNotFound()

        ret["category"] = category
        ret["products"] = products
        return ret

    except:
        raise HTTPNotFound()


# /product/{dmsId}
@view_config(route_name="product", renderer="../templates/product.jinja2")
# @view_config(route_name="product", renderer="json")
def product_view(request):
    try:
        dmsId = request.matchdict["dmsId"]
        credentials = getCredentials(request.registry.settings, "FLC")
        token = getFLCTokenMemo(
            credentials["tenant"], credentials["id"], credentials["secret"]
        )

        product = getFLCProduct(token, dmsId)

        if product is None:
            raise HTTPNotFound()
        ret = {}
        ret["token_url"] = "/forge/token"
        ret["product"] = product["item"]
        return ret

    except:
        raise HTTPNotFound()


# /forge/thumbnail?id
@view_config(route_name="forge-thumbnail")
def forge_thumbnail(request):
    try:
        urn = request.params["id"]
        credentials = getCredentials(request.registry.settings, "Forge")
        token = getForgeTokenMemo(credentials["id"], credentials["secret"])
        thumbnail = getForgeThumbnail(token, urn)

        return Response(thumbnail, content_type="image/png")

    except:

        return HTTPNotFound()
