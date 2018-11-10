from pyramid.view import view_config


# @view_config(route_name='home', renderer='../templates/mytemplate.jinja2')
@view_config(route_name='home', renderer='../templates/bootstraptest.jinja2')
def my_view(request):
    return {'project': 'au2018forgecatalog'}
