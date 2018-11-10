def includeme(config):
    config.add_static_view("static", "static", cache_max_age=3600)
    config.add_route("home", "/")
    config.add_route("category", "/category/{category}")
    config.add_route("product", "/product/{dmsId}")
    config.add_route("forge-token", "/forge/token")
    config.add_route("flc-token", "/flc/token")
