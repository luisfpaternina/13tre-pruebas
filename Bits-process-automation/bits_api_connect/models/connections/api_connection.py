# coding: utf-8
from zeep import Client, Settings, Transport
from .interfaces_api import InterfaceApiConnection, InterfaceApiMethods
import logging
_logger = logging.getLogger(__name__)

class ApiConnectionException(Exception):
    pass


class ApiConnectionRequest(InterfaceApiConnection, InterfaceApiMethods):
    def __init__(self, company, username, password, url_connection):
        self.username = username
        self.password = password
        self.company = company
        self.url_connection = url_connection
        transport = Transport(timeout=60)
        settings = Settings(strict=False, xml_huge_tree=True)
        self.client = Client(self.url_connection, settings=settings, transport=transport)
