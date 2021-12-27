# -*- coding: utf-8 -*-

from abc import ABC, abstractmethod


class InterfaceApiConnection(ABC):

    @abstractmethod
    def __init__(self):
        """
            ***************************************
            Object initialization for connection
            to the technology provider
            ***************************************
        """


class InterfaceApiMethods(ABC):

    @abstractmethod
    def upload(self):
        """
            ***************************************
            Method that manages the sending of the
            file to the technology provider
            ***************************************
        """

    @abstractmethod
    def download(self):
        """
            ***************************************
            Method that manages the query of billing
            information
            ***************************************
        """

    @abstractmethod
    def validate_status(self):
        """
            ***************************************
            method to manage the status of
            an issued document
            ***************************************
        """
