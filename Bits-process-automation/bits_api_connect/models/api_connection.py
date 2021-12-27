# -*- coding: utf-8 -*-

from zeep import Client, Settings, Transport
from .connections.api_connection_facturaxion import\
    ApiConnectionRequestFacturaxion
from .connections.api_connection_facturaxion import\
    ApiConnectionRequestFacturaxionPayroll


class ApiConnection():

    @classmethod
    def prepare_connection(cls, provider, connection_url=False):
        result = Adapter.prepare_connection(
            provider,
            provider.url_download\
                if connection_url == False else connection_url
        )
        return result


class Adapter(ApiConnection):

    @classmethod
    def prepare_connection(cls, provider, connection_url):
        if provider.connection_adapter in globals():
            function_connection = eval(
                'globals()[provider.connection_adapter]'
            )
            result = function_connection(
                company=provider.code,
                username=provider.username,
                password=provider.password,
                url_connection=connection_url
            )
            return result
        return False
