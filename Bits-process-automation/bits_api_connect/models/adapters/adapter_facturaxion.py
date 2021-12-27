# -*- coding: utf-8 -*-
import datetime
import base64
from io import BytesIO


class AdapterFacturaxion():

    @classmethod
    def prepare_file_to_txt(cls, type_file, provider, data, separator):
        res = ''
        if not isinstance(data, list):
            return False
        for section in data:
            str_data = cls._generate_values(
                type_file, provider, section, separator)
            res += f'{str_data}'

        res = res.replace('\r\n\r\n', '\r\n')
        return bytes(res, 'utf-8')

    @classmethod
    def prepare_file_to_xml(cls, type_file, provider, data, separator):
        for x in range(1, 4):
            data += data + separator
        return data

    @classmethod
    def validate_fields_date(cls, data):
        if isinstance(data['value'], datetime.date):
            data['value'] = data['value'].strftime('%Y-%m-%d')
    
    @classmethod
    def _generate_value_detail(cls, type_file, provider, row, separator):
        res = ''
        value = row.get('value', '')
        if isinstance(value, str):
            value = value.replace('\n', '')
        if isinstance(value, datetime.date):
            value = value.strftime('%Y-%m-%d')
        res += (f'{separator}{value}')
        return res

    @classmethod
    def _generate_values_detail(cls, type_file, provider, lines, separator):
        res = ''
        for row in lines:
            res += cls._generate_value_detail(
                type_file, provider, row, separator)
        return res

    @classmethod
    def _generate_values(cls, type_file, provider, section, separator):
        res = ''
        lines = section.get('lines', [])
        if len(lines) == 0:
            return res
        value = section.get('head', '')
        res += f'{value}'
        row_index = 0
        for line in lines:
            if row_index > 0:
                res += f'{value}'
            if isinstance(line, dict):
                res += cls._generate_value_detail(
                    type_file, provider, line, separator)
                continue
            row_index += 1
            for row in line:
                extra_value = row.get('head', '')
                if extra_value == '':
                    res += cls._generate_value_detail(
                        type_file, provider, row, separator)
                    continue
                res += f'\r\n'
                res += f'{extra_value}'
                extra_line = row.get('lines', [])
                detail = cls._generate_values_detail(
                    type_file, provider, extra_line, separator)
                res += f'{detail}'
            res += f'\r\n'
        res += f'\r\n'
        return res
