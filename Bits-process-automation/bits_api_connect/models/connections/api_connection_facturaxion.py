# coding: utf-8
import base64
import logging
import os
import pytz
import socket
import re
import time
from abc import ABC, abstractmethod
from datetime import datetime
from hashlib import sha256
from odoo import _
from zeep import Client, Plugin, helpers, Settings, Transport
from zeep.wsdl.utils import etree_to_string
from lxml import etree
from zeep.exceptions import Fault
from zeep.wsse.username import UsernameToken

from lxml import etree

from io import BytesIO

from .api_connection import ApiConnectionRequest, ApiConnectionException
from odoo import tools
from odoo.tools import misc, mute_logger

_logger = logging.getLogger(__name__)

_TYPES = {
    'out_invoice': 'F',
    'out_refund': 'C',
    'out_refund_credit': 'C',
    'out_refund_debit': 'D',
}

_ERRORS = {
    '00': 'Error inesperado',
    '01': 'Éxito',
    '02': 'Emisor no activo',
    '03': 'Certificado no vigente',
    '04': 'llave no correcta',
    '05': 'Formato incorrecto',
    '06': 'Folio y/o serie no valido',
    '07': 'Factura enviada previamente',
    '08': 'Error validacion DIAN',
    '09': 'Error catálogos',
    '10': 'Documento enviado fuera de tiempo',
    '11': 'Emisor incorrecto',
    '12': (
        'Factura generada correctamente, si embargo no ha sido enviada'
        + ' a la DIAN'),
    '13': 'Los datos de la solicitud no coinciden con el documento'
}

class ApiConnectionPlugin(Plugin):

    def egress(self, envelope, http_headers, operation, binding_options):
        self.log(envelope, 'ApiConnection_request')
        return envelope, http_headers

    def ingress(self, envelope, http_headers, operation):
        self.log(envelope, 'ApiConnection_response')
        return envelope, http_headers

    def log(self, xml, func):
        _logger.debug('%s with\n%s' % (func, etree.tostring(xml, encoding='utf-8', xml_declaration=True, pretty_print=True)))


class ApiConnectionUsernameToken(UsernameToken):
    def _create_password_digest(self):
        res = super(ApiConnectionUsernameToken, self)._create_password_digest()
        res[0].attrib['Type'] = res[0].attrib['Type'].replace('PasswordDigest', 'PasswordText')
        return res


class ApiConnectionRequestFacturaxion(ApiConnectionRequest):

    def upload(self, _type, filename, file, attachments):
        result = dict()
        # Data Required
        # cuenta: xsd:string,
        # empresa: xsd:string, usuario: xsd:string,
        # Documento: xsd:base64Binary, tipoDocumento: xsd:string)
        # Response
        # cufe: xsd:string, cadenaQR: xsd:string, transaccionID: xsd:string,
        # numeroDocumento: xsd:string, codigo: xsd:string,
        # descripcion: xsd:string,
        # Error: {Campo: xsd:string, Descripcion: xsd:string}
        try:
            _logger.error('Here starts the last function')
            _logger.error(attachments)
            _logger.error(file)
            _logger.error(_type)
            zeep_object = self.get_zeep_object(_type, file, attachments)
            input_dict = helpers.serialize_object(zeep_object, dict)
            _logger.error(input_dict)
            # Verificar con el codigo y enviar error True
            result['codigo'] = input_dict.get('codigo', '')
            _logger.error(result['codigo'])
            if input_dict.get('codigo', '') == '01':
                result['status'] = 'accepted'
            else:
                result['status'] = 'rejected'
            _logger.error(input_dict)
            result['descripcion'] = input_dict.get('descripcion', '')
            result['error'] = input_dict.get('Error', '')
            _logger.error('This is the input dict')
            _logger.error(input_dict)
            for element in input_dict['_raw_elements']:
                field = element.tag.replace("{http://www.b2bsite.com.co.fe.ol}", "")
                if field == 'Error':
                    result['error_msg'] = ''
                    items = list(element)
                    if len(items):
                        for item in items:
                            result['error_msg'] += item.tag + ": " + (item.text or '')
                            result['error_msg'] += "<br/>" if item.tag == "Descripcion" else " "
                elif not result.get(field, False):
                    result[field] = element.text or ''
            if input_dict.get('codigo') != '01':
                if not result.get('error_msg', False):
                    result['error_msg'] = ''
                result['error_msg'] += (
                    _ERRORS.get(input_dict.get('codigo'), '')
                )
        except Fault as fault:
            _logger.error(fault)
            raise ApiConnectionException(fault)
        except socket.timeout as e:
            _logger.error(e)
            raise ApiConnectionException(
                _('Connection to ApiConnection timed out. Their API is probably down.'))

        return result

    def download(self, _type, idTransaccion):
        exception = False
        result = dict()
        input_dict = dict()
        try:
            response = self.client.service.executeB2BSITEbpCOLapl_O2C_ConsultaEmisionWS(
                tipoDocumento=_TYPES.get(_type, ''),
                empresa=self.company,
                cuenta=self.password,
                usuario=self.username,
                idTransaccion=idTransaccion
            )
            input_dict = helpers.serialize_object(response, dict)
            code = input_dict.get('codigoRespuesta', '')
            result['codigo'] = code
            result['descripcion'] = input_dict.get('descripcionRespuesta', '')
            if code != '01':
                return input_dict, result, True

            docs = input_dict.get('Documento', [])
            if len(docs):
                result['response'] = docs[0]
            else:
                for element in input_dict.get('_raw_elements', []):
                    field = element.tag.replace(
                        "{http://www.b2bsite.com.co.fe.consulta.response}", "")
                    items = list(element)
                    if len(items):
                        result[field] = {}
                        for item in items:
                            result[field][item.tag] = item.text or ''
                    else:
                        result[field] = element.text or ''
                result['response'] = result.get('Documento', {})
            exception = True if not result.get('response', {}) else False
        except:
            exception = True
        return input_dict, result, exception

    def get_zeep_object(self, _type, file, attachments):
        _logger.error(attachments)
        _logger.error(self.password)
        _logger.error(self.username)
        _logger.error(file)
        files_support = list()
        zeep_object = self.client.service.executeB2BSitebpCOLapl_O2C_ProcesarFacturaOLv2LiteWS(
            cuenta=self.password,
            empresa=self.company,
            usuario=self.username,
            Documento=file,
            tipoDocumento=_TYPES.get(_type, '')
        ) if not attachments else False

        if attachments:
            for attach in attachments:
                _logger.error('launch the type of data')

                _logger.error(attach.mimetype)
                type = (
                    'txt' if 'text/plain' in attach.mimetype else
                    attach.mimetype.split('/')[-1]
                )
                files_support.append(
                    {
                        'docSustento': attach.datas,
                        'extensionDocSustento': type,
                    }
                )

            zeep_object = self.client.service.\
                executeB2BSITEbpCOLapl_O2C_ProcesarFacturaOLv2DocRel(
                    cuenta=self.password,
                    empresa=self.company,
                    usuario=self.username,
                    Documento=file,
                    tipoDocumento=_TYPES.get(_type, ''),
                    documentosSustento=files_support,
                )
        return zeep_object

    def validate_status(self, _type, idTransaccion):
        exception = False
        result = dict()
        input_dict = dict()
        try:
            response = self.client.service.executeB2BSITEbpCOLapl_O2C_ConsultaEmisionWS(
                tipoDocumento=_TYPES.get(_type, ''),
                empresa=self.company,
                cuenta=self.password,
                usuario=self.username,
                idTransaccion=idTransaccion
            )
            input_dict = helpers.serialize_object(response, dict)
            code = input_dict.get('codigoRespuesta', '')
            result['codigo'] = code
            result['descripcion'] = input_dict.get('descripcionRespuesta', '')
            _logger.error('This is the input dict')
            _logger.error(input_dict)
            if code != '01':
                return False

            docs = input_dict.get('Documento', [])
            if len(docs):
                result['response'] = docs[0]
                res = docs[0]
                return res.get('estatusDocumento', False)
            else:
                for element in input_dict.get('_raw_elements', []):
                    field = element.tag.replace(
                        "{http://www.b2bsite.com.co.fe.consulta.response}", "")
                    items = list(element)
                    if len(items):
                        result[field] = {}
                        for item in items:
                            result[field][item.tag] = item.text or ''
                    else:
                        result[field] = element.text or ''
                res = result.get('Documento', {})
                return res.get('estatusDocumento', False)
        except:
            _logger.error(
                "An error occurred while trying to get acceptance status"
            )
        _logger.error('pass for here')
        return False


class ApiConnectionRequestFacturaxionPayroll(ApiConnectionRequest):

    def upload(self, _type, filename, file, attachments):
        result = dict()
        # Data Required
        # cuenta: xsd:string,
        # empresa: xsd:string, usuario: xsd:string,
        # Documento: xsd:base64Binary, tipoDocumento: xsd:string)
        # Response
        # cufe: xsd:string, cadenaQR: xsd:string, transaccionID: xsd:string,
        # numeroDocumento: xsd:string, codigo: xsd:string,
        # descripcion: xsd:string,
        # Error: {Campo: xsd:string, Descripcion: xsd:string}
        try:
            zeep_object = self.get_zeep_object(_type, file, attachments)
            input_dict = helpers.serialize_object(zeep_object, dict)
            # Verificar con el codigo y enviar error True
            result['codigo'] = input_dict.get('codigo', '')
            if input_dict.get('codigo', '') == '01':
                result['status'] = 'accepted'
            else:
                result['status'] = 'rejected'
            result['descripcion'] = input_dict.get('descripcion', '')
            result['error'] = input_dict.get('Error', '')
            result['input_dict'] = input_dict
            """for element in input_dict['_raw_elements']:
                field = element.tag.replace("{http://www.b2bsite.com.co.fe.ol.nominaRqt}", "")
                if field == 'Error':
                    result['error_msg'] = ''
                    items = list(element)
                    if len(items):
                        for item in items:
                            result['error_msg'] += item.tag + ": " + (item.text or '')
                            result['error_msg'] += "<br/>" if item.tag == "Descripcion" else " "
                elif not result.get(field, False):
                    result[field] = element.text or ''
            if input_dict.get('codigo') != '01':
                if not result.get('error_msg', False):
                    result['error_msg'] = ''
                result['error_msg'] += (
                    _ERRORS.get(input_dict.get('codigo'), '')
                )
        except Fault as fault:
            _logger.error(fault)
            raise ApiConnectionException(fault)
        except socket.timeout as e:
            _logger.error(e)
            raise ApiConnectionException(
                _('Connection to ApiConnection timed out. Their API is probably down.'))"""
        except Fault as fault:
            raise ApiConnectionException(fault)
    
        return result

    def download(self, idTransaccion, numbers):
        exception = False
        result = dict()
        input_dict = dict()
        try:
            response = self.client.service.ConsultaDetalleNomina(
                empresa=self.company,
                cuenta=self.password,
                usuario=self.username,
                numeros=numbers,
                idTransaccion=idTransaccion
            )
            input_dict = helpers.serialize_object(response, dict)
            code = input_dict.get('codigo', '')
            result['code'] = code
            result['description'] = input_dict.get('descripcion', '')
            result['details_payslip'] = input_dict.get('detalleNominas', '')
            return input_dict, result, False
        except:
            exception = True
        return input_dict, result, exception
    
    def download_results(self, idTransaccion, type):
        exception = False
        result = dict()
        input_dict = dict()
        try:
            response = self.client.service.ConsultaResultadosNomina(
                empresa=self.company,
                cuenta=self.password,
                usuario=self.username,
                tipo=type,
                idTransaccion=idTransaccion
            )
            input_dict = helpers.serialize_object(response, dict)
            code = input_dict.get('codigo', '')
            result['code'] = code
            result['description'] = input_dict.get('descripcion', '')
            result['type'] = input_dict.get('tipo', '')
            result['qty'] = input_dict.get('cantidad', '')
            result['results_payslip'] = input_dict.get('resultadoNominas', '')
            return input_dict, result, False
        except:
            exception = True
        return input_dict, result, exception
    
    def download_totals(self, idTransaccion):
        exception = False
        result = dict()
        input_dict = dict()
        try:
            response = self.client.service.ConsultaTotalesNomina(
                empresa=self.company,
                cuenta=self.password,
                usuario=self.username,
                idTransaccion=idTransaccion
            )
            input_dict = helpers.serialize_object(response, dict)
            code = input_dict.get('codigo', '')
            result['code'] = code
            result['description'] = input_dict.get('descripcion', '')
            result['totals_payslip'] = input_dict.get('NominaTotales', '')
            return input_dict, result, False
        except:
            exception = True
        return input_dict, result, exception

    def get_zeep_object(self, _type, file, attachments):
        files_support = list()
        object_methods = [method_name for method_name in dir(self.client.service)]
        zeep_object = self.client.EmitirNomina(
            cuenta=self.password,
            empresa=self.company,
            usuario=self.username,
            Documento=file,
            tipoDocumento=_TYPES.get(_type, '')
        ) if not attachments else False
        if attachments:
            """for attach in attachments:
                type = (
                    'txt' if 'text/plain' in attach.mimetype else
                    attach.mimetype.split('/')[-1]
                )
                files_support.append(
                    {
                        'docSustento': attach.datas,
                        'extensionDocSustento': type,
                    }
                )"""
            tipoDocumento = 'N'
            zeep_object = self.client.service.\
                EmitirNomina(
                    cuenta=self.password,
                    empresa=self.company,
                    usuario=self.username,
                    Documento=file,
                    tipoDocumento=tipoDocumento,
                    #documentosSustento=files_support,
                )
        return zeep_object

    def validate_status(self, _type, idTransaccion):
        exception = False
        result = dict()
        input_dict = dict()
        try:
            response = self.client.service.executeB2BSITEbpCOLapl_O2C_ConsultaEmisionWS(
                tipoDocumento=_TYPES.get(_type, ''),
                empresa=self.company,
                cuenta=self.password,
                usuario=self.username,
                idTransaccion=idTransaccion
            )
            input_dict = helpers.serialize_object(response, dict)
            code = input_dict.get('codigoRespuesta', '')
            result['codigo'] = code
            result['descripcion'] = input_dict.get('descripcionRespuesta', '')
            if code != '01':
                return False

            docs = input_dict.get('Documento', [])
            if len(docs):
                result['response'] = docs[0]
                res = docs[0]
                return res.get('estatusDocumento', False)
            else:
                for element in input_dict.get('_raw_elements', []):
                    field = element.tag.replace(
                        "{http://www.b2bsite.com.co.fe.consulta.response}", "")
                    items = list(element)
                    if len(items):
                        result[field] = {}
                        for item in items:
                            result[field][item.tag] = item.text or ''
                    else:
                        result[field] = element.text or ''
                res = result.get('Documento', {})
                return res.get('estatusDocumento', False)
        except:
            _logger.error(
                "An error occurred while trying to get acceptance status"
            )
        return False
