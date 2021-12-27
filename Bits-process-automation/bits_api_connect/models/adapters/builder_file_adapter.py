# -*- coding: utf-8 -*-
from .adapter_facturaxion import AdapterFacturaxion


class BuilderToFile():

    @classmethod
    def prepare_file_for_submission(
        cls, type_file, provider, data, separator
    ):
        result = Adapter.prepare_file_for_submission(
            type_file, provider, data, separator
        )
        return result


class Adapter(BuilderToFile):

    @classmethod
    def prepare_file_for_submission(
        cls, type_file, provider, data, separator
    ):
        if provider in globals():
            function_provider = eval(
                'globals()[provider].prepare_file_to_' + type_file.lower()
            )
            result = function_provider(type_file, provider, data, separator)
            return result
        return False
