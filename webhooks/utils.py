def route_to_name(route):
    route = route.strip("/")
    service, resource, action = route.split("/")
    return "".join([service.capitalize(), resource.capitalize(), action.capitalize()])
