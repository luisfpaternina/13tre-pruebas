# -*- coding: utf-8 -*-

from odoo.tests.common import TransactionCase
from odoo.addons.bits_api_connect.models.adapters.builder_file_adapter\
    import BuilderToFile

import datetime
import base64


class TestAdapterLibrary(TransactionCase):

    def setUp(self):
        self.data = [
            {
                "head": "CAB",
                "lines": [
                    {
                        "label": "NitEmisor",
                        "code": "COD001",
                        "value": ""
                    },
                    {
                        "label": "NitAdquiriente",
                        "code": "COD002",
                        "value": ""
                    },
                    {
                        "label": "TipoDocumento",
                        "code": "COD003",
                        "value": "out_invoice"
                    },
                    {
                        "label": "Version",
                        "code": "COD004",
                        "value": 2
                    },
                    {
                        "label": "AmbieteDestinoDocumento",
                        "code": "COD005",
                        "value": 2
                    }
                ]
            },
            {
                "head": "HDR",
                "lines": [
                    {
                        "label": "IdentificadorFactura",
                        "code": "COD006",
                        "value": 5
                    },
                    {
                        "label": "Serie",
                        "code": "COD007",
                        "value": ""
                    },
                    {
                        "label": "Folio",
                        "code": "COD008",
                        "value": ""
                    },
                    {
                        "label": "FechaEmision",
                        "code": "COD009",
                        "value": datetime.date(2020, 9, 21)
                    },
                    {
                        "label": "HoraEmision",
                        "code": "COD010",
                        "value": ""
                    },
                    {
                        "label": "TimeZone",
                        "code": "COD011",
                        "value": "America/Bogota"
                    },
                    {
                        "label": "TipoFactura",
                        "code": "COD012",
                        "value": "1"
                    },
                    {
                        "label": "FormaPago",
                        "code": "COD013",
                        "value": "1"
                    },
                    {
                        "label": "FechaInicioPago",
                        "code": "COD014",
                        "value": ""
                    },
                    {
                        "label": "FechaFinPago",
                        "code": "COD015",
                        "value": ""
                    },
                    {
                        "label": "MetodoPago",
                        "code": "COD016",
                        "value": "1"
                    },
                    {
                        "label": "TipoOperacion",
                        "code": "COD017",
                        "value": "10"
                    },
                    {
                        "label": "NumeroPartidas",
                        "code": "COD018",
                        "value": 2
                    }
                ]
            },
            {
                "head": "MON",
                "lines": [
                    {
                        "label": "Divisa",
                        "code": "COD019",
                        "value": ""
                    },
                    {
                        "label": "TipoCambio",
                        "code": "COD020",
                        "value": ""
                    },
                    {
                        "label": "Subtotal",
                        "code": "COD021",
                        "value": ""
                    },
                    {
                        "label": "Descuento",
                        "code": "COD022",
                        "value": ""
                    },
                    {
                        "label": "Cargos",
                        "code": "COD023",
                        "value": ""
                    },
                    {
                        "label": "Total",
                        "code": "COD024",
                        "value": ""
                    },
                    {
                        "label": "TotalImpuestosRetenidos",
                        "code": "COD025",
                        "value": ""
                    },
                    {
                        "label": "TotalImpuestosTrasladados",
                        "code": "COD026",
                        "value": ""
                    },
                    {
                        "label": "TotalPagoAnticipado",
                        "code": "COD027",
                        "value": ""
                    },
                    {
                        "label": "MontoAPagar",
                        "code": "COD028",
                        "value": ""
                    },
                    {
                        "label": "ObservacionesFactura",
                        "code": "COD029",
                        "value": ""
                    },
                    {
                        "label": "ImporteConLetras",
                        "code": "COD030",
                        "value": ""
                    },
                    {
                        "label": "FechaTasaCambio",
                        "code": "COD031",
                        "value": ""
                    },
                    {
                        "label": "TotalBaseImpuestos",
                        "code": "COD032",
                        "value": ""
                    },
                    {
                        "label": "TotalBrutoMasImpuestos",
                        "code": "COD033",
                        "value": ""
                    },
                    {
                        "label": "TotalImpuestosIVA",
                        "code": "COD034",
                        "value": ""
                    }
                ]
            },
            {
                "head": "DIR",
                "lines": [
                    {
                        "label": "Calificador",
                        "code": "COD035",
                        "value": ""
                    },
                    {
                        "label": "Nit",
                        "code": "COD036",
                        "value": ""
                    },
                    {
                        "label": "Nombre",
                        "code": "COD037",
                        "value": ""
                    },
                    {
                        "label": "Line",
                        "code": "COD038",
                        "value": ""
                    },
                    {
                        "label": "Departamento",
                        "code": "COD039",
                        "value": ""
                    },
                    {
                        "label": "Ciudad",
                        "code": "COD040",
                        "value": ""
                    },
                    {
                        "label": "CodigoPais",
                        "code": "COD041",
                        "value": ""
                    },
                    {
                        "label": "Pais",
                        "code": "COD042",
                        "value": ""
                    },
                    {
                        "label": "DigitoVerificador",
                        "code": "COD043",
                        "value": ""
                    },
                    {
                        "label": "TipoOrganizacionJuridica",
                        "code": "COD044",
                        "value": ""
                    },
                    {
                        "label": "ClaveIdentificadorTributario",
                        "code": "COD045",
                        "value": ""
                    },
                    {
                        "label": "NombreIdentificadorTributario",
                        "code": "COD046",
                        "value": ""
                    },
                    {
                        "label": "ObligacionesFiscales",
                        "code": "COD047",
                        "value": ""
                    },
                    {
                        "label": "RegimenFiscal",
                        "code": "COD048",
                        "value": ""
                    },
                    {
                        "label": "CodigoDepartamento",
                        "code": "COD049",
                        "value": ""
                    },
                    {
                        "label": "CodigoMunicipio",
                        "code": "COD050",
                        "value": ""
                    },
                    {
                        "label": "CodigoPostal",
                        "code": "COD051",
                        "value": ""
                    },
                    {
                        "label": "LenguajePais",
                        "code": "COD052",
                        "value": ""
                    },
                    {
                        "label": "TipoDocumentoIdentidad",
                        "code": "COD053",
                        "value": ""
                    }
                ]
            },
            {
                "head": "DIR2",
                "lines": [
                    {
                        "label": "Calificador",
                        "code": "COD054",
                        "value": ""
                    },
                    {
                        "label": "Nit",
                        "code": "COD055",
                        "value": ""
                    },
                    {
                        "label": "Nombre",
                        "code": "COD056",
                        "value": ""
                    },
                    {
                        "label": "Line",
                        "code": "COD057",
                        "value": ""
                    },
                    {
                        "label": "Departamento",
                        "code": "COD058",
                        "value": ""
                    },
                    {
                        "label": "Ciudad",
                        "code": "COD059",
                        "value": ""
                    },
                    {
                        "label": "CodigoPais",
                        "code": "COD060",
                        "value": ""
                    },
                    {
                        "label": "Pais",
                        "code": "COD061",
                        "value": ""
                    },
                    {
                        "label": "ContactoEmail",
                        "code": "COD062",
                        "value": ""
                    },
                    {
                        "label": "DigitoVerificador",
                        "code": "COD063",
                        "value": ""
                    },
                    {
                        "label": "TipoOrganizacionJuridica",
                        "code": "COD064",
                        "value": ""
                    },
                    {
                        "label": "ClaveIdentificadorTributario",
                        "code": "COD065",
                        "value": ""
                    },
                    {
                        "label": "NombreIdentificadorTributario",
                        "code": "COD066",
                        "value": ""
                    },
                    {
                        "label": "ObligacionesFiscales",
                        "code": "COD067",
                        "value": ""
                    },
                    {
                        "label": "RegimenFiscal",
                        "code": "COD068",
                        "value": ""
                    },
                    {
                        "label": "CodigoDepartamento",
                        "code": "COD069",
                        "value": ""
                    },
                    {
                        "label": "CodigoMunicipio",
                        "code": "COD070",
                        "value": ""
                    },
                    {
                        "label": "CodigoPostal",
                        "code": "COD071",
                        "value": ""
                    },
                    {
                        "label": "LenguajePais",
                        "code": "COD072",
                        "value": ""
                    },
                    {
                        "label": "TipoDocumentoIdentidad",
                        "code": "COD073",
                        "value": ""
                    }
                ]
            },
            {
                "head": "REF",
                "lines": [
                    {
                        "label": "Cantidad",
                        "code": "COD074",
                        "value": ""
                    },
                    {
                        "label": "UnidadDeMedida",
                        "code": "COD075",
                        "value": ""
                    },
                    {
                        "label": "Descripcion",
                        "code": "COD076",
                        "value": ""
                    },
                    {
                        "label": "ValorUnitario",
                        "code": "COD077",
                        "value": ""
                    },
                    {
                        "label": "Importe",
                        "code": "COD078",
                        "value": ""
                    },
                    {
                        "label": "ClaveCodigoUtilizado",
                        "code": "COD079",
                        "value": ""
                    },
                    {
                        "label": "CodigoProducto",
                        "code": "COD080",
                        "value": ""
                    }
                ]
            },
            {
                "head": "DET",
                "lines": [
                    {
                        "label": "MontoTotalImpuesto",
                        "code": "COD081",
                        "value": ""
                    },
                    {
                        "label": "BaseImponible",
                        "code": "COD082",
                        "value": ""
                    },
                    {
                        "label": "ValorImpuesto",
                        "code": "COD083",
                        "value": ""
                    },
                    {
                        "label": "TarifaImpuesto",
                        "code": "COD084",
                        "value": ""
                    },
                    {
                        "label": "ClaveImpuesto",
                        "code": "COD085",
                        "value": ""
                    },
                    {
                        "label": "NombreImpuesto",
                        "code": "COD086",
                        "value": ""
                    }
                ]
            },
            {
                "head": "TAX",
                "lines": [
                    {
                        "label": "MontoTotalImpuesto",
                        "code": "COD087",
                        "value": ""
                    },
                    {
                        "label": "BaseImponible",
                        "code": "COD088",
                        "value": ""
                    },
                    {
                        "label": "ValorImpuesto",
                        "code": "COD089",
                        "value": ""
                    },
                    {
                        "label": "TarifaImpuesto",
                        "code": "COD090",
                        "value": ""
                    },
                    {
                        "label": "ClaveImpuesto",
                        "code": "COD091",
                        "value": ""
                    },
                    {
                        "label": "NombreImpuesto",
                        "code": "COD092",
                        "value": ""
                    }
                ]
            },
            {
                "head": "END",
                "lines": [

                ]
            }
        ]

    def test_correct_prepare_file_for_submission(self):
        type_file = 'txt'
        provider_adapter = 'AdapterFacturaxion'
        separator = '|'
        response = BuilderToFile.prepare_file_for_submission(
            type_file, provider_adapter, self.data, separator
        )
        self.assertIsInstance(response, bytes)

    def test_incorrect_prepare_file_for_submission(self):
        type_file = 'txt'
        provider_adapter = 'AdapterTest'
        separator = '|'
        response = BuilderToFile.prepare_file_for_submission(
            type_file, provider_adapter, self.data, separator
        )
        self.assertFalse(response)

    def test_incorrect_type_data(self):
        type_file = 'txt'
        provider_adapter = 'AdapterFacturaxion'
        separator = '|'
        data_error = dict()
        response = BuilderToFile.prepare_file_for_submission(
            type_file, provider_adapter, data_error, separator
        )
        self.assertFalse(response)

    def test_prepare_file_to_xml(self):
        type_file = 'xml'
        provider_adapter = 'AdapterFacturaxion'
        separator = '|'
        data_xml = "hola"
        response = BuilderToFile.prepare_file_for_submission(
            type_file, provider_adapter, data_xml, separator
        )
