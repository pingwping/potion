import re
from flask import url_for
from flask.ext.potion.schema import Schema
from flask.ext.potion.util import route_from


class Resolver(object):
    pass

    def schema(self, resource):
        raise NotImplementedError()


class RefResolver(Resolver):
    def schema(self, resource):
        resource_url = url_for(resource.endpoint)
        return {
            "type": "object",
            "properties": {
                "$ref": {
                    "type": "string",
                    "format": "uri",
                    "pattern": "^{}".format(re.escape(resource_url))
                }
            },
            "required": ["$ref"]
        }

    def format(self, resource, item):
        return {"$ref": resource.get_item_url(item)}

    def resolve(self, resource, value):
        endpoint, args = route_from(value["$ref"])
        # XXX verify endpoint is correct (it should be)
        assert resource.endpoint == endpoint
        return resource.get_item_from_id(args['id'])


class PropertyResolver(Resolver):
    def __init__(self, property):
        self.property = property

    def schema(self, resource):
        return resource.schema[self.property].response_schema

    def format(self, resource, item):
        return resource.schema[self.property].output(self.property, item)

    def resolve(self, resource, value):
        raise NotImplementedError()


class PropertiesResolver(Resolver):
    def __init__(self, *properties):
        self.properties = properties

    def schema(self, resource):
        return {
            "type": "array",
            "items": [resource.schema[p].response_schema for p in self.properties]
        }

    def format(self, resource, item):
        return [resource.schema[p].output(p, item) for p in self.properties]

    def resolve(self, resource, value):
        raise NotImplementedError()


class IDResolver(Resolver):
    def __init__(self):
        raise NotImplementedError()

    def schema(self, resource):
        return resource.meta.id_field.response_schema

    def format(self, resource, item):
        return resource.meta.id_field.output(resource.meta.id_attribute, item)

    def resolve(self, resource, value):
        return resource.get_item_from_id(value)
