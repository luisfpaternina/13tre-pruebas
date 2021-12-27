# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase
from odoo.exceptions import UserError
from datetime import datetime, timedelta, date
from odoo import _
import logging
from odoo.addons.l10n_co_e_payroll.models.browsable_object\
    import Payslips
from odoo.addons.bits_api_connect.models.connections.api_connection\
    import ApiConnectionException

from unittest.mock import patch, Mock
from unittest import TestCase
import requests


class TestFacturaxionReturns(TestCase):

    def __init__(self):
        super(TestFacturaxionReturns, self).__init__()
        self.condition = ""

    def upload(self, _type, filename, file, attachments):
        if self.condition == "upload_exception":
            raise ApiConnectionException(_('Connection to ApiConnection timed out. Their API is probably down.'))
        elif self.condition == "upload_rejected_one":
            return {
                'codigo': '01', 
                'status': 'rejected', 
                'descripcion': 'Solicitud de emisión de nomina rechazada.', 
                'error': '', 
                'input_dict': {
                    'codigo': '01', 
                    'descripcion': 'Solicitud de emisión de nomina rechazada.', 
                    'transaccionID': 'IDTN-0000003784', 
                    'Errores': {
                            'detalleError': [
                                {
                                    'segmento': 'TRA',
                                    'descripcionError': 'Descripcion Pruebas',
                                }
                            ]
                    }
                }
            }
        elif self.condition == "upload_rejected_multi":
            return {
                'codigo': '01', 
                'status': 'rejected', 
                'descripcion': 'Solicitud de emisión de nomina rechazada.', 
                'error': '', 
                'input_dict': {
                    'codigo': '01', 
                    'descripcion': 'Solicitud de emisión de nomina rechazada.', 
                    'transaccionID': 'IDTN-0000003784', 
                    'Errores': {
                            'detalleError': [
                                {
                                    'segmento': 'TRA',
                                    'descripcionError': 'Descripcion Pruebas',
                                },
                                {
                                    'segmento': 'TRA',
                                    'descripcionError': 'Descripcion Pruebas',
                                },
                            ]
                    }
                }
            }
        elif self.condition == "upload_accepted_without_cune":
            return {
                'codigo': '01', 
                'status': 'accepted', 
                'descripcion': 'Solicitud de emisión de nomina exitosa, nomina en proceso', 
                'error': '', 
                'input_dict': {
                    'codigo': '01', 
                    'descripcion': 'Solicitud de emisión de nomina exitosa, nomina en proceso', 
                    'Errores': None
                }
            }
        elif self.condition == "upload_accepted_without_tid":
            return {
                'codigo': '01', 
                'status': 'accepted', 
                'descripcion': 'Solicitud de emisión de nomina exitosa, nomina en proceso', 
                'error': '', 
                'input_dict': {
                    'codigo': '01', 
                    'descripcion': 'Solicitud de emisión de nomina exitosa, nomina en proceso', 
                    'Errores': None
                }
            }      
        else:
            return {
                'codigo': '01', 
                'status': 'accepted', 
                'descripcion': 'Solicitud de emisión de nomina exitosa, nomina en proceso', 
                'error': '', 
                'input_dict': {
                    'codigo': '01', 
                    'descripcion': 'Solicitud de emisión de nomina exitosa, nomina en proceso', 
                    'transaccionID': 'IDTN-0000003784', 
                    'Errores': None
                }
            }
    
    def download(self, idTransaccion, numbers):
        encode_file = 'Mjk0LTI5NSwgKE5PIFNFIFBVRURFIEdFTkVSQVIgRVhDRVBDSU9OKQozMzItPjM0MCwgCjMzMy0+MzM1LCAKMzM1LTMzOCwgCjM0MC0+MzQ1LCAKMzQxLT4zNDMsIAozNDctPjMyNSwgCjM2MC00NTEsIAo0OTAtPjQ2OSwgCjUwOS0+NTEwLCAKNTEwLTUyMywgCjU1MS0+NTUyLCAKNTUyLTU1OSwgCjU2NS0+ZXhpdCwgCjU2Ni0+NTY3LCAKNTY3LCAKNTgxLT42MDEsIAo1ODktPjYwMSwgCjYxMi0+NjA1LCAKNjE3LT42MTMsIAo2ODQtPjY4NSwgCjY4NS02ODYsIAo2ODctPjY4OSwgCjY4OS0+NjkwLCAKNjkwLCAKNjkxLT42OTIsIAo2OTIsIAo2OTQtPjcwNCwgCjY5OC0+Njk5LCAKNjk5LCAKNzA0LT43MDUsIAo3MDUtNzEzLCAKNzE0LT43MTUsIAo3MTUtNzIzCg=='

        if self.condition == "download_diff_results_types" and numbers == 'NORM0060':
            return (
                {
                    'codigo': '01', 
                    'descripcion': 'Exito', 
                    'detalleNominas': {
                        'DetalleNomina': [
                            {
                                'numero': 'NORM0060', 
                                'estatus': 'Aceptado', 
                                'appResponse': encode_file, 
                                'xmlFirmado': encode_file
                            }
                        ]
                    }
                }, 
                {
                    'code': '01', 
                    'description': 'Exito', 
                    'details_payslip': {
                        'DetalleNomina': [
                            {
                                'numero': 'NORM0060', 
                                'estatus': 'Aceptado', 
                                'appResponse': False, 
                                'xmlFirmado': False
                            }
                        ]
                    }
                }, 
                False
            )
        elif self.condition == "download_diff_results_types" and numbers == 'NORM0061':
            return (
                {
                    'codigo': '02', 
                    'descripcion': 'Fallido', 
                    'detalleNominas': {
                        'DetalleNomina': [
                            {
                                'numero': 'NORM0060', 
                                'estatus': 'Rechazado', 
                                'appResponse': False, 
                                'xmlFirmado': False
                            }
                        ]
                    }
                }, 
                {
                    'code': '02', 
                    'description': 'Fallido', 
                    'details_payslip': {
                        'DetalleNomina': [
                            {
                                'numero': 'NORM0060', 
                                'estatus': 'Rechazado', 
                                'appResponse': False, 
                                'xmlFirmado': False
                            }
                        ]
                    }
                }, 
                False
            )
        elif self.condition == "download_results_wo_res_2" and numbers == 'NORM0061':
            return (
                {
                    'codigo': '02', 
                    'descripcion': 'Fallido', 
                    'detalleNominas': {
                        'DetalleNomina': [
                            {
                                'numero': 'NORM0060', 
                                'estatus': 'Rechazado', 
                                'appResponse': False, 
                                'xmlFirmado': False
                            }
                        ]
                    }
                }, 
                {
                    'code': '02', 
                    'description': 'Fallido', 
                    'details_payslip': {
                        'DetalleNomina': [
                            {
                                'numero': 'NORM0060', 
                                'estatus': 'Rechazado', 
                                'appResponse': False, 
                                'xmlFirmado': False
                            }
                        ]
                    }
                }, 
                {
                    'codigo': '02', 
                    'descripcion': 'Fallido', 
                    'detalleNominas': {
                        'DetalleNomina': [
                            {
                                'numero': 'NORM0060', 
                                'estatus': 'Rechazado', 
                                'appResponse': False, 
                                'xmlFirmado': False
                            }
                        ]
                    }
                }
            )
        elif self.condition == "download_results_wo_details_payslip" and numbers == 'NORM0060':
            return (
                {
                    'codigo': '02', 
                    'descripcion': 'Fallido', 
                    'detalleNominas': {
                        'DetalleNomina': [
                            {
                                'numero': 'NORM0060', 
                                'estatus': 'Rechazado', 
                                'appResponse': False, 
                                'xmlFirmado': False
                            }
                        ]
                    }
                }, 
                {
                    'code': '02', 
                    'description': 'Fallido', 
                    'details_payslip': False
                }, 
                False
            )
        elif self.condition == "download_results_with_pdf" and numbers == 'NORM0060':
            return (
                {
                    'codigo': '02', 
                    'descripcion': 'Fallido', 
                    'detalleNominas': {
                        'DetalleNomina': [
                            {
                                'numero': 'NORM0060', 
                                'estatus': 'Rechazado', 
                                'appResponse': False, 
                                'xmlFirmado': False
                            }
                        ]
                    }
                }, 
                {
                    'code': '02', 
                    'description': 'Fallido', 
                    'details_payslip': {
                        'DetalleNomina': [
                            {
                                'numero': 'NORM0060', 
                                'estatus': 'Rechazado', 
                                'appResponse': False, 
                                'xmlFirmado': False,
                                'pdfNomina': "0010000000001010001000000000101000100000000010100010000000001010001000000000101000100000000010100101010001101000011010010111001100100000011010010111001100100000011000010010000001110100011001010111001101110100001000000101000001000100010001100010000001100100011011110110001101110101011011010110010101101110011101000010111000100000000010100100100101100110001000000111100101101111011101010010000001100011011000010110111000100000011100100110010101100001011001000010000001110100011010000110100101110011001011000010000001111001011011110111010100100000011010000110000101110110011001010010000001000001011001000110111101100010011001010010000001000001011000110111001001101111011000100110000101110100001000000101001001100101011000010110010001100101011100100010000001101001011011100111001101110100011000010110110001101100011001010110010000100000011011110110111000100000011110010110111101110101011100100010000001100011011011110110110101110000011101010111010001100101011100100010111000100000",
                            }
                        ]
                    }
                }, 
                False
            )
        else:
            return (
                {
                    'codigo': '01', 
                    'descripcion': 'Exito', 
                    'detalleNominas': {
                        'DetalleNomina': [
                            {
                                'numero': 'NORM0060', 
                                'estatus': 'Aceptado', 
                                'appResponse': encode_file, 
                                'xmlFirmado': encode_file
                            }
                        ]
                    }
                }, 
                {
                    'code': '01', 
                    'description': 'Exito', 
                    'details_payslip': {
                        'DetalleNomina': [
                            {
                                'numero': 'NORM0060', 
                                'estatus': 'Aceptado', 
                                'appResponse': encode_file, 
                                'xmlFirmado': encode_file
                            }
                        ]
                    }
                }, 
                False
            )
    
    def download_results(self, idTransaccion, type):
        if self.condition == "download_without_results":
            return (
                {
                    'codigo': '01', 
                    'descripcion': 'Exito', 
                    'tipo': 'Rechazadas', 
                    'cantidad': '11', 
                    'resultadoNominas': {
                    }
                }, 
                {
                    'code': '01', 
                    'description': 'Exito', 
                    'type': 'Aceptadas', 
                    'qty': '1', 
                    'results_payslip': None
                }, 
                False
            )
        elif self.condition == "download_diff_results_types":
            if type == 'A':
                return (
                    {
                        'codigo': '01', 
                        'descripcion': 'Exito', 
                        'tipo': 'Aceptadas', 
                        'cantidad': '1', 
                        'resultadoNominas': {
                            'ResultadoNomina': [
                                {
                                    'Numero': 'NORM0061', 
                                    'posicion': None, 
                                    'cune': None, 
                                    'resultado': 'DOCUMENTO ACEPTADO POR LA DIAN'
                                }
                            ]
                        }
                    }, 
                    {
                        'code': '01', 
                        'description': 'Exito', 
                        'type': 'Aceptadas', 
                        'qty': '1', 
                        'results_payslip': {
                            'ResultadoNomina': [
                                {
                                    'Numero': 'NORM0061', 
                                    'posicion': None, 
                                    'cune': None, 
                                    'resultado': 'DOCUMENTO ACEPTADO POR LA DIAN'
                                },
                            ]
                        }
                    }, 
                    False
                )
            elif type == 'R':
                return (
                    {
                        'codigo': '02', 
                        'descripcion': 'Fallida', 
                        'tipo': 'Rechazadas', 
                        'cantidad': '1', 
                        'resultadoNominas': {
                            'ResultadoNomina': [
                                {
                                    'Numero': 'NORM0060', 
                                    'posicion': None, 
                                    'cune': None, 
                                    'resultado': 'DOCUMENTO RECHAZADO POR LA DIAN'
                                },
                            ]
                        }
                    }, 
                    {
                        'code': '02', 
                        'description': 'Fallida', 
                        'type': 'Rechazadas', 
                        'qty': '1', 
                        'results_payslip': {
                            'ResultadoNomina': [
                                {
                                    'Numero': 'NORM0060', 
                                    'posicion': None, 
                                    'cune': None, 
                                    'resultado': 'DOCUMENTO RECHAZADO POR LA DIAN'
                                },
                            ]
                        }
                    }, 
                    False
                )
            elif type == 'E':
                return (
                    {
                        'codigo': '03', 
                        'descripcion': 'Exito', 
                        'tipo': 'En Espera', 
                        'cantidad': '11', 
                        'resultadoNominas': {
                            'ResultadoNomina': False
                        }
                    }, 
                    {
                        'code': '03', 
                        'description': 'Exito', 
                        'type': 'En Espera', 
                        'qty': '0', 
                        'results_payslip': None
                    }, 
                    False
                )
        else:
            return (
                {
                    'codigo': '01', 
                    'descripcion': 'Exito', 
                    'tipo': 'Rechazadas', 
                    'cantidad': '11', 
                    'resultadoNominas': {
                        'ResultadoNomina': [
                            {
                                'Numero': 'NORM0060', 
                                'posicion': None, 
                                'cune': None, 
                                'resultado': 'DOCUMENTO RECHAZADO POR LA DIAN'
                            }, 
                            {
                                'Numero': 'NORM0061', 
                                'posicion': None, 
                                'cune': None, 
                                'resultado': 'DOCUMENTO RECHAZADO POR LA DIAN'
                            }
                        ]
                    }
                }, 
                {
                    'code': '01', 
                    'description': 'Exito', 
                    'type': 'Aceptadas', 
                    'qty': '0', 
                    'results_payslip': {
                        'ResultadoNomina': [
                            {
                                'Numero': 'NORM0060', 
                                'posicion': None, 
                                'cune': None, 
                                'resultado': 'DOCUMENTO RECHAZADO POR LA DIAN'
                            }, 
                            {
                                'Numero': 'NORM0061', 
                                'posicion': None, 
                                'cune': None, 
                                'resultado': 'DOCUMENTO RECHAZADO POR LA DIAN'
                            }
                        ]
                    }
                }, 
                False
            )
    
    def download_totals(self, idTransaccion):
        if self.condition == "download_totals_with_res2":
            return (
                {
                    'codigo': '01', 
                    'descripcion': 'Exito', 
                    'NominaTotales': {
                        'RecibosNominasStatus': {
                            'ReciboNominaTotales': [
                                {
                                    'statusReciboNomina': 'Validas', 
                                    'cantidadReciboNomina': 11
                                }, 
                                {
                                    'statusReciboNomina': 'Erroneas', 
                                    'cantidadReciboNomina': 0
                                }, 
                                {
                                    'statusReciboNomina': 'Pendientes', 
                                    'cantidadReciboNomina': 0
                                }, 
                                {
                                    'statusReciboNomina': 'Aceptadas', 
                                    'cantidadReciboNomina': 0
                                }, 
                                {
                                    'statusReciboNomina': 'Rechazadas', 
                                    'cantidadReciboNomina': 11
                                }
                            ]
                        }, 
                        'statusNomina': 'Consulta Exitosa', 
                        'cantidadNomina': 11
                    }
                }, 
                {
                    'code': '01', 
                    'description': 'Exito', 
                    'totals_payslip': {
                        'RecibosNominasStatus': {
                            'ReciboNominaTotales': [
                                {
                                    'statusReciboNomina': 'Validas', 
                                    'cantidadReciboNomina': 11
                                }, 
                                {
                                    'statusReciboNomina': 'Erroneas', 
                                    'cantidadReciboNomina': 0
                                }, 
                                {
                                    'statusReciboNomina': 'Pendientes', 
                                    'cantidadReciboNomina': 0
                                }, 
                                {
                                    'statusReciboNomina': 'Aceptadas', 
                                    'cantidadReciboNomina': 0
                                }, 
                                {
                                    'statusReciboNomina': 'Rechazadas', 
                                    'cantidadReciboNomina': 11
                                }
                            ]
                        }, 
                    'statusNomina': 'Consulta Exitosa', 
                    'cantidadNomina': 11
                }
                }, 
                True
            )
        elif self.condition == "download_without_total":
            return (
                {
                    'codigo': '01', 
                    'descripcion': 'Exito', 
                    'NominaTotales': {
                        'RecibosNominasStatus': {
                            'ReciboNominaTotales': [
                                {
                                    'statusReciboNomina': 'Validas', 
                                    'cantidadReciboNomina': 11
                                }, 
                                {
                                    'statusReciboNomina': 'Erroneas', 
                                    'cantidadReciboNomina': 0
                                }, 
                                {
                                    'statusReciboNomina': 'Pendientes', 
                                    'cantidadReciboNomina': 0
                                }, 
                                {
                                    'statusReciboNomina': 'Aceptadas', 
                                    'cantidadReciboNomina': 0
                                }, 
                                {
                                    'statusReciboNomina': 'Rechazadas', 
                                    'cantidadReciboNomina': 11
                                }
                            ]
                        }, 
                        'statusNomina': 'Consulta Exitosa', 
                        'cantidadNomina': 11
                    }
                }, 
                {
                    'code': '01', 
                    'description': 'Exito', 
                    'totals_payslip': False
                }, 
                False
            )
        else:
            return (
                {
                    'codigo': '01', 
                    'descripcion': 'Exito', 
                    'NominaTotales': {
                        'RecibosNominasStatus': {
                            'ReciboNominaTotales': [
                                {
                                    'statusReciboNomina': 'Validas', 
                                    'cantidadReciboNomina': 11
                                }, 
                                {
                                    'statusReciboNomina': 'Erroneas', 
                                    'cantidadReciboNomina': 0
                                }, 
                                {
                                    'statusReciboNomina': 'Pendientes', 
                                    'cantidadReciboNomina': 0
                                }, 
                                {
                                    'statusReciboNomina': 'Aceptadas', 
                                    'cantidadReciboNomina': 0
                                }, 
                                {
                                    'statusReciboNomina': 'Rechazadas', 
                                    'cantidadReciboNomina': 11
                                }
                            ]
                        }, 
                        'statusNomina': 'Consulta Exitosa', 
                        'cantidadNomina': 11
                    }
                }, 
                {
                    'code': '01', 
                    'description': 'Exito', 
                    'totals_payslip': {
                        'RecibosNominasStatus': {
                            'ReciboNominaTotales': [
                                {
                                    'statusReciboNomina': 'Validas', 
                                    'cantidadReciboNomina': 11
                                }, 
                                {
                                    'statusReciboNomina': 'Erroneas', 
                                    'cantidadReciboNomina': 0
                                }, 
                                {
                                    'statusReciboNomina': 'Pendientes', 
                                    'cantidadReciboNomina': 0
                                }, 
                                {
                                    'statusReciboNomina': 'Aceptadas', 
                                    'cantidadReciboNomina': 0
                                }, 
                                {
                                    'statusReciboNomina': 'Rechazadas', 
                                    'cantidadReciboNomina': 11
                                }
                            ]
                        }, 
                    'statusNomina': 'Consulta Exitosa', 
                    'cantidadNomina': 11
                }
                }, 
                False
            )
    
    def get_zeep_object(self, _type, file, attachments):
        return False

    def validate_status(self, _type, idTransaccion):
        return False


class TestEPayroll(TransactionCase):

    def setUp(self):
        super(TestEPayroll, self).setUp()
        self.social_security = self.env['social.security']
        self.hr_contract = self.env['hr.contract']
        self.hr_payslip = self.env['hr.payslip']
        self.hr_payslip_run = self.env['hr.payslip.run']
        self.res_partner = self.env['res.partner']
        self.hr_employee = self.env['hr.employee']
        self.hr_salary_rule = self.env['hr.salary.rule']
        self.hr_payroll_structure = self.env['hr.payroll.structure']
        self.hr_payroll_structure_type = self.env['hr.payroll.structure.type']
        self.hr_salary_rule_category = self.env['hr.salary.rule.category']
        self.tech_provider = self.env['l10n_co.tech.provider']
        self.ir_sequence = self.env['ir.sequence']
        self.hr_payslip_line = ['hr.payslip.line']
        self.payment_method_class = self.env['payment.method']
        self.payment_way_class = self.env['payment.way']
        self.hr_payroll_news_stage = self.env['hr.payroll.news.stage']
        self.hr_payroll_new = self.env['hr.payroll.news']
        self.hr_payroll_holidays_history = self.env['hr.payroll.holidays.history']
        self.hr_payroll_holiday_lapse = self.env['hr.payroll.holiday.lapse']

        self.ir_sequence_1 = self.ir_sequence.create({
            'name': "Test sequence_1",
            'padding': 1,
            'number_increment': 1,
            'prefix': "PRE",
            'suffix': "SU",
            'number_next': 1
        })

        new_social_security = self.social_security.create({
            'code': '00',
            'name': 'Prueba de Ingreso de datos',
            'entity_type': 'arl'
        })

        self.tech_provider_1 = self.env.ref(
            'l10n_co_tech_provider_payroll.l10n_co_tech_provider_payroll_01')

        self.salary_rule_category = self.hr_salary_rule_category.create({
            'name': "Salary Category Test",
            'code': "SCT"
        })

        self.structure_type = self.hr_payroll_structure_type.create({
            'name': "Test Type",
            'wage_type': "monthly"
        })

        self.settlement_structure_type = self.hr_payroll_structure_type.create({
            'name': "Liquidación",
            'wage_type': "monthly"
        })

        self.contract = self.hr_contract.create({
            'name': "Contract Test",
            'date_start': datetime.now(),
            'date_end': datetime.now()+timedelta(days=365),
            'wage': 3150000,
            'structure_type_id': self.structure_type.id,
            'high_risk_pension': True,
            'contributor_type_id': new_social_security.id,
            'state': "open",
        })

        self.test_country = self.env.ref('base.co')

        self.test_state = self.env['res.country.state'].create(dict(
            name="State",
            code="ST",
            l10n_co_divipola="19",
            country_id=self.test_country.id))

        self.town = self.env['res.country.town'].create(dict(
            name="town",
            code="TW",
            l10n_co_divipola="19001",
            state_id=self.test_state.id,
            country_id=self.test_country.id))

        self.contact = self.res_partner.create({
            'name': 'partner name',
            'first_surname': 'partner name',
            'email': 'partner@name.com',
            'country_id': self.test_country.id,
            'town_id': self.town.id,
            'state_id': self.test_state.id
        })

        self.employee = self.hr_employee.create({
            'name': "Test Payroll News",
            'names': "Test Payroll News",
            'surnames': "Test Payroll News",
            'known_as': "Test Payroll News",
            'document_type': '13',
            'contract_id': self.contract.id,
            'contract_ids': [(6, 0, [self.contract.id])],
            'identification_id': "75395146",
            'address_home_id': self.contact.id,
            'high_risk_pension': True,
            'contributor_type': new_social_security.id,
            'contributor_subtype': new_social_security.id,
            'integral_salary': False,
        })

        self.employee._compute_contributor_type()

        self.payroll_structure = self.hr_payroll_structure.create({
            'name': "Structure Test",
            'sequence_id': self.ir_sequence_1.id,
            'type_id': self.structure_type.id,
        })

        self.settlement_payroll_structure = self.hr_payroll_structure.create({
            'name': "Settlement Structure Test",
            'sequence_id': self.ir_sequence_1.id,
            'type_id': self.settlement_structure_type.id,
        })

        self.salary_rule = self.hr_salary_rule.create({
            'name': "Clean Salary Rule",
            'code': "CLN",
            'sequence': 10,
            'struct_id': self.payroll_structure.id,
            'category_id': self.salary_rule_category.id,
            'condition_select': "none",
            'amount_select': "fix",
            'amount_fix': 3000,
            'quantity': 1,
        })

        self.salary_rule_afc = self.hr_salary_rule.create({
            'name': "ITEM BASE",
            'code': "001",
            'sequence': 100,
            'struct_id': self.payroll_structure.id,
            'category_id': self.salary_rule_category.id,
            'condition_select': "none",
            'amount_select': "fix",
            'amount_fix': 3000,
            'quantity': 1,
            'l10n_type_rule': 'ded_afc',
            'tech_provider_line_id': self.env.ref('l10n_co_tech_provider_payroll.l10n_co_tech_provider_payroll_line_headboard_38').id
        })

        parent_act_field_indicator = self.env.ref('l10n_co_tech_provider_payroll.l10n_co_tech_provider_payroll_line_headboard_37')

        self.salary_rule_parent_act_field = self.hr_salary_rule.create({
            'name': "TESTACTF",
            'code': "TESTACTF",
            'sequence': 150,
            'struct_id': self.payroll_structure.id,
            'category_id': self.salary_rule_category.id,
            'condition_select': "none",
            'amount_select': "fix",
            'amount_fix': 2500,
            'quantity': 1,
            'l10n_type_rule': 'ded_refund',
            'tech_provider_line_id': parent_act_field_indicator.id
        })

        act_field_false_indicator = self.env.ref('l10n_co_tech_provider.l10n_co_tech_provider_payroll_line_field_144')

        parent_parent_indicator = self.env.ref('l10n_co_tech_provider_payroll.l10n_co_tech_provider_payroll_line_headboard_33')

        self.salary_rule_act_field_false = self.hr_salary_rule.create({
            'name': "ACTFFALSE",
            'code': "ACTFFALSE",
            'sequence': 150,
            'struct_id': self.payroll_structure.id,
            'category_id': self.salary_rule_category.id,
            'condition_select': "none",
            'amount_select': "fix",
            'amount_fix': 2500,
            'quantity': 1,
            'tech_provider_line_id': act_field_false_indicator.id
        })

        lic_indicator = self.env.ref('l10n_co_tech_provider_payroll.l10n_co_tech_provider_payroll_line_headboard_18')
        lic_indicator.cardinality = '0_1'

        self.salary_rule_lic = self.hr_salary_rule.create({
            'name': 'LIC',
            'code': 'LIC',
            'sequence': 200,
            'struct_id': self.payroll_structure.id,
            'category_id': self.salary_rule_category.id,
            'affect_payslip': False,
            'constitutive_calculate': True,
            'quantity': 1.0,
            'amount_select': "percentage",
            'amount_percentage': 100.0,
            'amount_percentage_base': "contract.wage/30",
            'l10n_type_rule': 'lic_leave_maternity',
            'tech_provider_line_id': lic_indicator.id,
        })

        act_field_pat = self.env.ref('l10n_co_tech_provider.l10n_co_tech_provider_payroll_line_field_137')
        act_field_salario_integral = self.env.ref('l10n_co_payroll_act_fields.payroll_act_fields_029')
        act_field_salario_integral.condition_python = "result = 1"
        self.salary_rule_pat = self.hr_salary_rule.create({
            'name': 'PAT',
            'code': 'PAT',
            'sequence': 250,
            'struct_id': self.payroll_structure.id,
            'category_id': self.salary_rule_category.id,
            'affect_payslip': False,
            'constitutive_calculate': True,
            'quantity': 1.0,
            'amount_select': "percentage",
            'amount_percentage': 100.0,
            'amount_percentage_base': "contract.wage/30",
            'tech_provider_line_id': act_field_pat.id,
        })

        self.salary_rule_vac = self.hr_salary_rule.create({
            'name': 'VAC',
            'code': 'VAC',
            'sequence': 300,
            'struct_id': self.payroll_structure.id,
            'category_id': self.salary_rule_category.id,
            'affect_payslip': False,
            'constitutive_calculate': True,
            'quantity': 1.0,
            'amount_select': "percentage",
            'amount_percentage': 100.0,
            'amount_percentage_base': "holiday.compute_holidays(hour_extra_codes=['60','65','70','75'],comision_codes=['321'])",
            'l10n_type_rule': 'enjoyment_rule',
            'tech_provider_line_id': self.env.ref(
                'l10n_co_tech_provider_payroll.l10n_co_tech_provider_payroll_line_headboard_13'
            ).id
        })

        self.salary_rule_child_parent = self.hr_salary_rule.create({
            'name': "CHILDP",
            'code': "CHILDP",
            'sequence': 400,
            'struct_id': self.payroll_structure.id,
            'category_id': self.salary_rule_category.id,
            'condition_select': "none",
            'amount_select': "fix",
            'amount_fix': 2500,
            'quantity': 1,
            'tech_provider_line_id': parent_parent_indicator.id
        })

        self.payrol_news_stage = self.hr_payroll_news_stage.create({
            'name': "Stage Test"
        })

        self.payroll_new_pat = self.hr_payroll_new.create({
            'name': "Test Novelty PAT",
            'payroll_structure_id': self.payroll_structure.id,
            'salary_rule_id': self.salary_rule_pat.id,
            'stage_id': self.payrol_news_stage.id,
            'employee_payroll_news_ids': [
                [
                    0,
                    0,
                    {
                        'quantity': 1,
                        'employee_id': self.employee.id,
                        'amount': 5,
                        'total': 30
                    }
                ]
            ],
            'datetime_end': datetime.now(),
            'datetime_start': datetime.now()+timedelta(days=5),
        })

        self.payroll_new_pat_2 = self.hr_payroll_new.create({
            'name': "Test Novelty PAT 2",
            'payroll_structure_id': self.payroll_structure.id,
            'salary_rule_id': self.salary_rule_pat.id,
            'stage_id': self.payrol_news_stage.id,
            'employee_payroll_news_ids': [
                [
                    0,
                    0,
                    {
                        'quantity': 1,
                        'employee_id': self.employee.id,
                        'amount': 5,
                        'total': 30
                    }
                ]
            ],
            'datetime_end': datetime.now(),
            'datetime_start': datetime.now()+timedelta(days=5),
        })

        self.payroll_new_pat_3 = self.hr_payroll_new.create({
            'name': "Test Novelty PAT 3",
            'payroll_structure_id': self.payroll_structure.id,
            'salary_rule_id': self.salary_rule_pat.id,
            'stage_id': self.payrol_news_stage.id,
            'employee_payroll_news_ids': [
                [
                    0,
                    0,
                    {
                        'quantity': 1,
                        'employee_id': self.employee.id,
                        'amount': 5,
                        'total': 30
                    }
                ]
            ],
            'datetime_end': datetime.now(),
            'datetime_start': datetime.now()+timedelta(days=5),
        })

        self.payroll_new = self.hr_payroll_new.create({
            'name': "Test Novelty",
            'payroll_structure_id': self.payroll_structure.id,
            'salary_rule_id': self.salary_rule_lic.id,
            'stage_id': self.payrol_news_stage.id,
            'employee_payroll_news_ids': [
                [
                    0,
                    0,
                    {
                        'quantity': 1,
                        'employee_id': self.employee.id,
                        'amount': 5
                    }
                ]
            ],
            'datetime_end': datetime.now(),
            'datetime_start': datetime.now()+timedelta(days=5),
        })

        self.payroll_new_lic_2 = self.hr_payroll_new.create({
            'name': "Test Novelty",
            'payroll_structure_id': self.payroll_structure.id,
            'salary_rule_id': self.salary_rule_lic.id,
            'stage_id': self.payrol_news_stage.id,
            'employee_payroll_news_ids': [
                [
                    0,
                    0,
                    {
                        'quantity': 1,
                        'employee_id': self.employee.id,
                        'amount': 5
                    }
                ]
            ],
            'datetime_end': datetime.now(),
            'datetime_start': datetime.now()+timedelta(days=5),
        })

        self.holiday_lapse_vac = self.hr_payroll_holiday_lapse.create({
            'employee_id': self.employee.id,
            'begin_date': datetime.now()-timedelta(days=15),
            'end_date': datetime.now()+timedelta(days=15),
            'number_holiday_days': 30,
            'type_vacation': 'normal',
            'state': '2',
        })

        holiday_start_date = datetime.now()-timedelta(days=3)
        holiday_end_date = datetime.now()+timedelta(days=3)

        self.holiday_history_vac = self.hr_payroll_holidays_history.create({
            'name': "Test Vacations",
            'employee': self.employee.id,
            'holiday_lapse': self.holiday_lapse_vac.id,
            'enjoyment_start_date': holiday_start_date.strftime('%Y-%m-%d'),
            'enjoyment_end_date': holiday_end_date.strftime('%Y-%m-%d'),
            'enjoyment_days': 6,
            'compensated_days': 0,
            'payment_date': datetime.now(),
            'liquidated_period': 'month',
        })

        self.payroll_new_vac = self.hr_payroll_new.create({
            'name': "Test Vacations",
            'payroll_structure_id': self.payroll_structure.id,
            'salary_rule_id': self.salary_rule_vac.id,
            'stage_id': self.payrol_news_stage.id,
            'employee_payroll_news_ids': [
                (
                    0,
                    0,
                    {
                        'quantity': 1,
                        'employee_id': self.employee.id,
                        'amount': 5
                    }
                ),
            ],
            'holiday_history_id': self.holiday_history_vac.id,
            'datetime_end': datetime.now(),
            'datetime_start': datetime.now()+timedelta(days=5),
        })

        self.payroll_new_vac_2 = self.hr_payroll_new.create({
            'name': "Test Vacations 2",
            'payroll_structure_id': self.payroll_structure.id,
            'salary_rule_id': self.salary_rule_vac.id,
            'stage_id': self.payrol_news_stage.id,
            'employee_payroll_news_ids': [
                (
                    0,
                    0,
                    {
                        'quantity': 1,
                        'employee_id': self.employee.id,
                        'amount': 5
                    }
                ),
            ],
            'holiday_history_id': self.holiday_history_vac.id,
            'datetime_end': datetime.now(),
            'datetime_start': datetime.now()+timedelta(days=5),
        })

        self.payment_method = self.payment_method_class.create({
            'name': 'Payroll MC Test',
            'code': 'PMCTEST',
        })

        self.payment_way = self.payment_way_class.create({
            'name': 'Payroll WC Test',
            'code': 'PWCTEST',
        })

        self.payslip = self.hr_payslip.create({
            'name': "Payroll Test",
            'state': "done",
            'number': "SLIP-3243",
            'ep_status_message': 'Prueba',
            'employee_id': self.employee.id,
            'contract_id': self.contract.id,
            'struct_id': self.payroll_structure.id,
            'date_from': datetime.now()-timedelta(days=1),
            'date_to': datetime.now()+timedelta(days=30),
            'line_ids': [(0, 0, {
                'code': "TESTCODE",
                'salary_rule_id': self.salary_rule_afc.id,
                'name': "SALARIO BÁSICO",
                'note': "sueldo / 30 X  los dias laborados",
                'quantity': 3000,
                'rate': 100,
                'amount': 3000,
            }),
            (0, 0, {
                'code': "LIC",
                'salary_rule_id': self.salary_rule_lic.id,
                'name': "LIC",
                'note': "sueldo / 30",
                'quantity': 5,
                'rate': 100,
                'amount': 3000,
                'payroll_news_id': [(4, self.payroll_new.id)]
            }),
            (0, 0, {
                'code': "LIC_2",
                'salary_rule_id': self.salary_rule_lic.id,
                'name': "LIC_2",
                'note': "sueldo / 30",
                'quantity': 5,
                'rate': 100,
                'amount': 3000,
                'payroll_news_id': [(4, self.payroll_new_lic_2.id)]
            }),
            (0, 0, {
                'code': "VAC",
                'salary_rule_id': self.salary_rule_vac.id,
                'name': "VAC",
                'note': "sueldo / 30",
                'quantity': 5,
                'rate': 100,
                'amount': 3000,
                'payroll_news_id': [(4, self.payroll_new_vac.id)]
            }),
            (0, 0, {
                'code': "VAC2",
                'salary_rule_id': self.salary_rule_vac.id,
                'name': "VAC2",
                'note': "sueldo / 30",
                'quantity': 5,
                'rate': 100,
                'amount': 3000,
                'payroll_news_id': [(4, self.payroll_new_vac.id)]
            }),
            (0, 0, {
                'code': "VAC2",
                'salary_rule_id': self.salary_rule_vac.id,
                'name': "VAC2",
                'note': "sueldo / 30",
                'quantity': 5,
                'rate': 100,
                'amount': 3000,
                'payroll_news_id': [(4, self.payroll_new_vac_2.id)]
            }),
            (0, 0, {
                'code': "ACTF",
                'salary_rule_id': self.salary_rule_parent_act_field.id,
                'name': "ACTF",
                'note': "sueldo / 30",
                'quantity': 5,
                'rate': 100,
                'amount': 3000,
            }),
            (0, 0, {
                'code': "CLN",
                'salary_rule_id': self.salary_rule.id,
                'name': "CLN",
                'note': "sueldo / 30",
                'quantity': 5,
                'rate': 100,
                'amount': 3000,
            }),
            (0, 0, {
                'code': "ACTFFALSE",
                'salary_rule_id': self.salary_rule_act_field_false.id,
                'name': "ACTFFALSE",
                'note': "sueldo / 30",
                'quantity': 5,
                'rate': 100,
                'amount': 3000,
            }),
            (0, 0, {
                'code': "CHILDP",
                'salary_rule_id': self.salary_rule_child_parent.id,
                'name': "CHILDP",
                'note': "sueldo / 30",
                'quantity': 5,
                'rate': 100,
                'amount': 3000,
            }),
            (0, 0, {
                'code': "PAT",
                'salary_rule_id': self.salary_rule_pat.id,
                'name': "PAT",
                'note': "sueldo / 30",
                'quantity': 5,
                'rate': 100,
                'amount': 3000,
                'payroll_news_id': [(4, self.payroll_new_pat.id)]
            }), ],
            'payment_method_id': self.payment_method.id,
            'payment_way_id': self.payment_way.id,
        })
        
        self.payslip_2 = self.hr_payslip.create({
            'name': "Payroll Test",
            'state': "done",
            'number': "NORM-0060",
            'employee_id': self.employee.id,
            'contract_id': self.contract.id,
            'struct_id': self.settlement_payroll_structure.id,
            'date_from': datetime.now()-timedelta(days=1),
            'date_to': datetime.now()+timedelta(days=30),
            'line_ids': [(0, 0, {
                'code': "TESTCODE",
                'salary_rule_id': self.salary_rule_afc.id,
                'name': "SALARIO BÁSICO",
                'note': "sueldo / 30 X  los dias laborados",
                'quantity': 3000,
                'rate': 100,
                'amount': 3000,
            }),
            (0, 0, {
                'code': "LIC",
                'salary_rule_id': self.salary_rule_lic.id,
                'name': "LIC",
                'note': "sueldo / 30",
                'quantity': 5,
                'rate': 100,
                'amount': 3000,
                'payroll_news_id': [(4, self.payroll_new.id)]
            }),
            (0, 0, {
                'code': "LIC_2",
                'salary_rule_id': self.salary_rule_lic.id,
                'name': "LIC_2",
                'note': "sueldo / 30",
                'quantity': 5,
                'rate': 100,
                'amount': 3000,
                'payroll_news_id': [(4, self.payroll_new_lic_2.id)]
            }),
            (0, 0, {
                'code': "VAC",
                'salary_rule_id': self.salary_rule_vac.id,
                'name': "VAC",
                'note': "sueldo / 30",
                'quantity': 5,
                'rate': 100,
                'amount': 3000,
                'payroll_news_id': [(4, self.payroll_new_vac.id)]
            }),
            (0, 0, {
                'code': "VAC2",
                'salary_rule_id': self.salary_rule_vac.id,
                'name': "VAC2",
                'note': "sueldo / 30",
                'quantity': 5,
                'rate': 100,
                'amount': 3000,
                'payroll_news_id': [(4, self.payroll_new_vac.id)]
            }),
            (0, 0, {
                'code': "VAC2",
                'salary_rule_id': self.salary_rule_vac.id,
                'name': "VAC2",
                'note': "sueldo / 30",
                'quantity': 5,
                'rate': 100,
                'amount': 3000,
                'payroll_news_id': [(4, self.payroll_new_vac_2.id)]
            }),
            (0, 0, {
                'code': "ACTF",
                'salary_rule_id': self.salary_rule_parent_act_field.id,
                'name': "ACTF",
                'note': "sueldo / 30",
                'quantity': 5,
                'rate': 100,
                'amount': 3000,
            }),
            (0, 0, {
                'code': "CLN",
                'salary_rule_id': self.salary_rule.id,
                'name': "CLN",
                'note': "sueldo / 30",
                'quantity': 5,
                'rate': 100,
                'amount': 3000,
            }),
            (0, 0, {
                'code': "ACTFFALSE",
                'salary_rule_id': self.salary_rule_act_field_false.id,
                'name': "ACTFFALSE",
                'note': "sueldo / 30",
                'quantity': 5,
                'rate': 100,
                'amount': 3000,
            }),
            (0, 0, {
                'code': "CHILDP",
                'salary_rule_id': self.salary_rule_child_parent.id,
                'name': "CHILDP",
                'note': "sueldo / 30",
                'quantity': 5,
                'rate': 100,
                'amount': 3000,
            }),
            (0, 0, {
                'code': "PAT",
                'salary_rule_id': self.salary_rule_pat.id,
                'name': "PAT",
                'note': "sueldo / 30",
                'quantity': 5,
                'rate': 100,
                'amount': 3000,
                'payroll_news_id': [(4, self.payroll_new_pat_2.id)]
            }), ],
            'payment_method_id': self.payment_method.id,
            'payment_way_id': self.payment_way.id,
        })

        self.payslip_3 = self.hr_payslip.create({
            'name': "Payroll Test",
            'number': "NORM-0061",
            'employee_id': self.employee.id,
            'contract_id': self.contract.id,
            'struct_id': self.payroll_structure.id,
            'date_from': datetime.now()-timedelta(days=1),
            'date_to': datetime.now()+timedelta(days=30),
            'line_ids': [(0, 0, {
                'code': "TESTCODE",
                'salary_rule_id': self.salary_rule_afc.id,
                'name': "SALARIO BÁSICO",
                'note': "sueldo / 30 X  los dias laborados",
                'quantity': 3000,
                'rate': 100,
                'amount': 3000,
            }),
            (0, 0, {
                'code': "LIC",
                'salary_rule_id': self.salary_rule_lic.id,
                'name': "LIC",
                'note': "sueldo / 30",
                'quantity': 5,
                'rate': 100,
                'amount': 3000,
                'payroll_news_id': [(4, self.payroll_new.id)]
            }),
            (0, 0, {
                'code': "LIC_2",
                'salary_rule_id': self.salary_rule_lic.id,
                'name': "LIC_2",
                'note': "sueldo / 30",
                'quantity': 5,
                'rate': 100,
                'amount': 3000,
                'payroll_news_id': [(4, self.payroll_new_lic_2.id)]
            }),
            (0, 0, {
                'code': "VAC",
                'salary_rule_id': self.salary_rule_vac.id,
                'name': "VAC",
                'note': "sueldo / 30",
                'quantity': 5,
                'rate': 100,
                'amount': 3000,
                'payroll_news_id': [(4, self.payroll_new_vac.id)]
            }),
            (0, 0, {
                'code': "VAC2",
                'salary_rule_id': self.salary_rule_vac.id,
                'name': "VAC2",
                'note': "sueldo / 30",
                'quantity': 5,
                'rate': 100,
                'amount': 3000,
                'payroll_news_id': [(4, self.payroll_new_vac.id)]
            }),
            (0, 0, {
                'code': "VAC2",
                'salary_rule_id': self.salary_rule_vac.id,
                'name': "VAC2",
                'note': "sueldo / 30",
                'quantity': 5,
                'rate': 100,
                'amount': 3000,
                'payroll_news_id': [(4, self.payroll_new_vac_2.id)]
            }),
            (0, 0, {
                'code': "ACTF",
                'salary_rule_id': self.salary_rule_parent_act_field.id,
                'name': "ACTF",
                'note': "sueldo / 30",
                'quantity': 5,
                'rate': 100,
                'amount': 3000,
            }),
            (0, 0, {
                'code': "CLN",
                'salary_rule_id': self.salary_rule.id,
                'name': "CLN",
                'note': "sueldo / 30",
                'quantity': 5,
                'rate': 100,
                'amount': 3000,
            }),
            (0, 0, {
                'code': "ACTFFALSE",
                'salary_rule_id': self.salary_rule_act_field_false.id,
                'name': "ACTFFALSE",
                'note': "sueldo / 30",
                'quantity': 5,
                'rate': 100,
                'amount': 3000,
            }),
            (0, 0, {
                'code': "CHILDP",
                'salary_rule_id': self.salary_rule_child_parent.id,
                'name': "CHILDP",
                'note': "sueldo / 30",
                'quantity': 5,
                'rate': 100,
                'amount': 3000,
            }),
            (0, 0, {
                'code': "PAT",
                'salary_rule_id': self.salary_rule_pat.id,
                'name': "PAT",
                'note': "sueldo / 30",
                'quantity': 5,
                'rate': 100,
                'amount': 3000,
                'payroll_news_id': [(4, self.payroll_new_pat_3.id)]
            }), ],
            'payment_method_id': self.payment_method.id,
            'payment_way_id': self.payment_way.id,
            'state': "done",
        })

        self.payslip_4 = self.hr_payslip.create({
            'name': "Payroll Test",
            'number': "NORM-0061",
            'employee_id': self.employee.id,
            'contract_id': self.contract.id,
            'struct_id': self.payroll_structure.id,
            'date_from': datetime.now()-timedelta(days=1),
            'date_to': datetime.now()+timedelta(days=30),
            'line_ids': [(0, 0, {
                'code': "TESTCODE",
                'salary_rule_id': self.salary_rule_afc.id,
                'name': "SALARIO BÁSICO",
                'note': "sueldo / 30 X  los dias laborados",
                'quantity': 3000,
                'rate': 100,
                'amount': 3000,
            }),
            (0, 0, {
                'code': "LIC",
                'salary_rule_id': self.salary_rule_lic.id,
                'name': "LIC",
                'note': "sueldo / 30",
                'quantity': 5,
                'rate': 100,
                'amount': 3000,
                'payroll_news_id': [(4, self.payroll_new.id)]
            }),
            (0, 0, {
                'code': "LIC_2",
                'salary_rule_id': self.salary_rule_lic.id,
                'name': "LIC_2",
                'note': "sueldo / 30",
                'quantity': 5,
                'rate': 100,
                'amount': 3000,
                'payroll_news_id': [(4, self.payroll_new_lic_2.id)]
            }),
            (0, 0, {
                'code': "VAC",
                'salary_rule_id': self.salary_rule_vac.id,
                'name': "VAC",
                'note': "sueldo / 30",
                'quantity': 5,
                'rate': 100,
                'amount': 3000,
                'payroll_news_id': [(4, self.payroll_new_vac.id)]
            }),
            (0, 0, {
                'code': "VAC2",
                'salary_rule_id': self.salary_rule_vac.id,
                'name': "VAC2",
                'note': "sueldo / 30",
                'quantity': 5,
                'rate': 100,
                'amount': 3000,
                'payroll_news_id': [(4, self.payroll_new_vac.id)]
            }),
            (0, 0, {
                'code': "VAC2",
                'salary_rule_id': self.salary_rule_vac.id,
                'name': "VAC2",
                'note': "sueldo / 30",
                'quantity': 5,
                'rate': 100,
                'amount': 3000,
                'payroll_news_id': [(4, self.payroll_new_vac_2.id)]
            }),
            (0, 0, {
                'code': "ACTF",
                'salary_rule_id': self.salary_rule_parent_act_field.id,
                'name': "ACTF",
                'note': "sueldo / 30",
                'quantity': 5,
                'rate': 100,
                'amount': 3000,
            }),
            (0, 0, {
                'code': "CLN",
                'salary_rule_id': self.salary_rule.id,
                'name': "CLN",
                'note': "sueldo / 30",
                'quantity': 5,
                'rate': 100,
                'amount': 3000,
            }),
            (0, 0, {
                'code': "ACTFFALSE",
                'salary_rule_id': self.salary_rule_act_field_false.id,
                'name': "ACTFFALSE",
                'note': "sueldo / 30",
                'quantity': 5,
                'rate': 100,
                'amount': 3000,
            }),
            (0, 0, {
                'code': "CHILDP",
                'salary_rule_id': self.salary_rule_child_parent.id,
                'name': "CHILDP",
                'note': "sueldo / 30",
                'quantity': 5,
                'rate': 100,
                'amount': 3000,
            }),
            (0, 0, {
                'code': "PAT",
                'salary_rule_id': self.salary_rule_pat.id,
                'name': "PAT",
                'note': "sueldo / 30",
                'quantity': 5,
                'rate': 100,
                'amount': 3000,
                'payroll_news_id': [(4, self.payroll_new_pat_3.id)]
            }), ],
            'payment_method_id': self.payment_method.id,
            'payment_way_id': self.payment_way.id,
        })

        self.payslip_without_lines = self.hr_payslip.create({
            'name': "Payroll Test",
            'state': "done",
            'number': "paytest-003",
            'employee_id': self.employee.id,
            'contract_id': self.contract.id,
            'struct_id': self.payroll_structure.id,
            'date_from': datetime.now()-timedelta(days=1),
            'date_to': datetime.now()+timedelta(days=30),
            'payment_method_id': self.payment_method.id,
            'payment_way_id': self.payment_way.id,
        })

        emp_indicator = self.env.ref('l10n_co_tech_provider_payroll.l10n_co_tech_provider_payroll_line_headboard_02')

        self.payment_way = self.env['payment.way'].create({
            'name': 'Payment Test',
            'code': 'PT',
        })

        self.payment_method = self.env['payment.method'].create({
            'name': 'Payment Method Test',
            'code': 'PMT',
        })

        self.payslip_run = self.hr_payslip_run.create({
            'name': "Payslip Lot Test 1",
            'date_start': datetime.now()-timedelta(days=1),
            'date_end': datetime.now()+timedelta(days=30),
            'payment_way_id': self.payment_way.id,
            'payment_method_id': self.payment_method.id,
            'payment_date': datetime.now()+timedelta(days=30),
            'slip_ids': [(4, self.payslip.id), ]
        })

        self.multi_payslip_run = self.hr_payslip_run.create({
            'name': "Multi Payslip Lot Test 1",
            'date_start': datetime.now()-timedelta(days=1),
            'date_end': datetime.now()+timedelta(days=30),
            'payment_way_id': self.payment_way.id,
            'payment_method_id': self.payment_method.id,
            'payment_date': datetime.now()+timedelta(days=30),
            'slip_ids': [(6, 0, [self.payslip_2.id, self.payslip_3.id, self.payslip_4.id]), ]
        })

        self.payslip_run_empty = self.hr_payslip_run.create({
            'name': "Payslip Lot Test 2",
            'date_start': datetime.now()-timedelta(days=1),
            'date_end': datetime.now()+timedelta(days=30),
            'payment_way_id': self.payment_way.id,
            'payment_method_id': self.payment_method.id,
            'payment_date': datetime.now()+timedelta(days=30),
        })

        self.payslip_run_without_lines = self.hr_payslip_run.create({
            'name': "Payslip Lot Invalid Number",
            'date_start': datetime.now()-timedelta(days=1),
            'date_end': datetime.now()+timedelta(days=30),
            'payment_way_id': self.payment_way.id,
            'payment_method_id': self.payment_method.id,
            'payment_date': datetime.now()+timedelta(days=30),
            'slip_ids': [(4, self.payslip_without_lines.id), ]
        })
          
    def test_action_generate_file_payslip_run(self):
        
        self.payslip_run.company_id.vat = '123456789'
        self.payslip_run.company_id.partner_id.write({
            'country_id': self.test_country.id,
            'town_id': self.town.id,
            'state_id': self.test_state.id
        })

        self.payslip_run.company_id.write({ 
            'provider_id': self.tech_provider_1.id,
            'country_id': self.test_country.id,
            'town_id': self.town.id,
            'state_id': self.test_state.id
        })

        self.employee.address_home_id.write({
            'country_id': self.env.ref('base.co')})
        
        prepare_url = (
            'odoo.addons.bits_api_connect.models.api_connection'
            '.ApiConnection.prepare_connection'
        )

        return_prepare = TestFacturaxionReturns()

        with patch(prepare_url, new=Mock(return_value=return_prepare)):
            self.payslip_run.send_massive_file()
            self.payslip_run.get_state_dian_massive_payslip()
    
    def test_action_generate_file_multi_payslip_run(self):
        
        self.multi_payslip_run.company_id.vat = '123456789'
        self.multi_payslip_run.company_id.partner_id.write({
            'country_id': self.test_country.id,
            'town_id': self.town.id,
            'state_id': self.test_state.id
        })

        self.multi_payslip_run.company_id.write({
            'provider_id': self.tech_provider_1.id,
            'country_id': self.test_country.id,
            'town_id': self.town.id,
            'state_id': self.test_state.id
        })

        self.multi_payslip_run.ep_transaction_id_history = "Prueba Historial"

        self.employee.address_home_id.write({
            'country_id': self.test_country.id})

        prepare_url = (
            'odoo.addons.bits_api_connect.models.api_connection'
            '.ApiConnection.prepare_connection'
        )

        return_prepare = TestFacturaxionReturns()

        with patch(prepare_url, new=Mock(return_value=return_prepare)):
            self.multi_payslip_run.generate_epayroll_file()
            self.multi_payslip_run.send_massive_file()
            self.multi_payslip_run._get_payslips_rejected()

    def test_action_generate_file_payslip_run_empty(self):

        self.payslip_run_empty.company_id.vat = '123456789'
        self.payslip_run_empty.company_id.partner_id.write({
            'country_id': self.test_country.id,
            'town_id': self.town.id,
            'state_id': self.test_state.id
        })

        self.payslip_run.company_id.write({
            'provider_id': self.tech_provider_1.id,
            'country_id': self.test_country.id,
            'town_id': self.town.id,
            'state_id': self.test_state.id
        })

        self.employee.address_home_id.write({
            'country_id': self.env.ref('base.co')})

        prepare_url = (
            'odoo.addons.bits_api_connect.models.api_connection'
            '.ApiConnection.prepare_connection'
        )

        return_prepare = TestFacturaxionReturns()

        with patch(prepare_url, new=Mock(return_value=return_prepare)):
            self.payslip_run_empty.send_massive_file()
            self.multi_payslip_run._get_payslips_rejected()
    
    def test_results(self):

        self.multi_payslip_run.company_id.vat = '123456789'
        self.multi_payslip_run.company_id.partner_id.write({
            'country_id': self.test_country.id,
            'town_id': self.town.id,
            'state_id': self.test_state.id
        })

        self.payslip_run.company_id.write({
            'provider_id': self.tech_provider_1.id,
            'country_id': self.test_country.id,
            'town_id': self.town.id,
            'state_id': self.test_state.id
        })

        self.employee.address_home_id.write({
            'country_id': self.test_country.id})

        self.multi_payslip_run.write({
            'ep_transaction_id': False
        })

        self.multi_payslip_run.get_state_dian_massive_payslip()

        self.multi_payslip_run.write({
            'ep_transaction_id': 'IDTN-0000003253'
        })

        self.multi_payslip_run.get_state_dian_massive_payslip()

        rejected = True
        for payslip in self.multi_payslip_run.slip_ids:
            if not rejected:
                payslip.write({
                    'ep_dian_state': 'Rechazado'
                })
            else:
                payslip.write({
                    'ep_dian_state': 'Aceptado'
                })
                rejected = False

        prepare_url = (
            'odoo.addons.bits_api_connect.models.api_connection'
            '.ApiConnection.prepare_connection'
        )

        return_prepare = TestFacturaxionReturns()

        with patch(prepare_url, new=Mock(return_value=return_prepare)):
            self.multi_payslip_run._get_payslips_rejected()

    def test_rejected(self):

        self.multi_payslip_run.company_id.vat = '123456789'
        self.multi_payslip_run.company_id.partner_id.write({
            'country_id': self.test_country.id,
            'town_id': self.town.id,
            'state_id': self.test_state.id
        })

        self.payslip_run.company_id.write({
            'provider_id': self.tech_provider_1.id,
            'country_id': self.test_country.id,
            'town_id': self.town.id,
            'state_id': self.test_state.id
        })

        self.employee.address_home_id.write({
            'country_id': self.test_country.id})

        rejected = False
        for payslip in self.multi_payslip_run.slip_ids:
            if not rejected:
                payslip.write({
                    'ep_dian_state': 'Rechazado'
                })
                rejected = True
            else:
                payslip.write({
                    'ep_dian_state': 'Aceptado'
                })
        prepare_url = (
            'odoo.addons.bits_api_connect.models.api_connection'
            '.ApiConnection.prepare_connection'
        )

        return_prepare = TestFacturaxionReturns()

        with patch(prepare_url, new=Mock(return_value=return_prepare)):
            self.multi_payslip_run._get_payslips_rejected()
            self.multi_payslip_run.send_rejected_payslip_massive_file()

        for payslip in self.multi_payslip_run.slip_ids:
            payslip.write({
                'ep_dian_state': 'Rechazado'
            })

        test_obj = TestFacturaxionReturns()
        test_obj.condition = "upload_accepted_without_tid"
        return_prepare = test_obj

        run_group = self.hr_payslip_run.browse([
            self.multi_payslip_run.id,
            self.payslip_run.id,
        ])

        self.env.company.provider_id = self.tech_provider_1.id

        with patch(prepare_url, new=Mock(return_value=return_prepare)):
            self.multi_payslip_run.send_rejected_payslip_massive_file()

        for payslip in self.multi_payslip_run.slip_ids:
            payslip.write({
                'ep_dian_state': 'Aceptado'
            })

        with patch(prepare_url, new=Mock(return_value=return_prepare)):
            self.multi_payslip_run._get_payslips_rejected()
            self.multi_payslip_run.send_rejected_payslip_massive_file()

    def test_api_connection(self):
        
        self.multi_payslip_run.company_id.vat = '123456789'
        self.multi_payslip_run.company_id.partner_id.write({
            'country_id': self.test_country.id,
            'town_id': self.town.id,
            'state_id': self.test_state.id
        })

        self.multi_payslip_run.company_id.write({ 
            'provider_id': self.tech_provider_1.id,
            'country_id': self.test_country.id,
            'town_id': self.town.id,
            'state_id': self.test_state.id
        })

        self.employee.address_home_id.write({
            'country_id': self.env.ref('base.co')})

        prepare_url = (
            'odoo.addons.bits_api_connect.models.api_connection'
            '.ApiConnection.prepare_connection'
        )

        return_prepare = TestFacturaxionReturns()

        self.env.company.provider_id = self.tech_provider_1.id

        with patch(prepare_url, new=Mock(return_value=return_prepare)):
            self.multi_payslip_run._create_api_connection(self.tech_provider_1, self.tech_provider_1.url_upload)
    
    def test_get_total_massive_payslip(self):

        self.multi_payslip_run.company_id.vat = '123456789'
        self.multi_payslip_run.company_id.partner_id.write({
            'country_id': self.test_country.id,
            'town_id': self.town.id,
            'state_id': self.test_state.id
        })

        self.multi_payslip_run.company_id.write({ 
            'provider_id': self.tech_provider_1.id,
            'country_id': self.test_country.id,
            'town_id': self.town.id,
            'state_id': self.test_state.id
        })

        self.multi_payslip_run.update_dian_transaction_id('IDTN-0000003253')

        self.employee.address_home_id.write({
            'country_id': self.env.ref('base.co')})

        prepare_url = (
            'odoo.addons.bits_api_connect.models.api_connection'
            '.ApiConnection.prepare_connection'
        )

        test_obj = TestFacturaxionReturns()
        test_obj.condition = "download_totals_with_res2"
        return_prepare = test_obj

        self.env.company.provider_id = self.tech_provider_1.id

        with patch(prepare_url, new=Mock(return_value=return_prepare)):
            self.multi_payslip_run.get_state_dian_massive_payslip()

        test_obj = TestFacturaxionReturns()
        test_obj.condition = "download_without_total"
        return_prepare = test_obj

        self.env.company.provider_id = self.tech_provider_1.id

        with patch(prepare_url, new=Mock(return_value=return_prepare)):
            self.multi_payslip_run.get_state_dian_massive_payslip()

        test_obj = TestFacturaxionReturns()
        test_obj.condition = "download_diff_results_types"
        return_prepare = test_obj

        self.env.company.provider_id = self.tech_provider_1.id

        with patch(prepare_url, new=Mock(return_value=return_prepare)):
            self.multi_payslip_run.get_state_dian_massive_payslip()
            self.multi_payslip_run.unlink_massive_response_lines_dian()
     
    def test_generate_electronic_payslip_tech_provider_upload_exception(self):
        
        self.multi_payslip_run.company_id.vat = '123456789'
        self.multi_payslip_run.company_id.partner_id.write({
            'country_id': self.test_country.id,
            'town_id': self.town.id,
            'state_id': self.test_state.id
        })

        self.multi_payslip_run.company_id.write({ 
            'provider_id': self.tech_provider_1.id,
            'country_id': self.test_country.id,
            'town_id': self.town.id,
            'state_id': self.test_state.id
        })

        self.employee.address_home_id.write({
            'country_id': self.env.ref('base.co')})

        prepare_url = (
            'odoo.addons.bits_api_connect.models.api_connection'
            '.ApiConnection.prepare_connection'
        )

        test_obj = TestFacturaxionReturns()
        test_obj.condition = "upload_exception"
        return_prepare = test_obj

        self.env.company.provider_id = self.tech_provider_1.id

        with patch(prepare_url, new=Mock(return_value=return_prepare)):
            self.multi_payslip_run._generate_electronic_payslip_tech_provider()

    def test_generate_electronic_payslip_tech_provider_connection_exception(self):

        self.multi_payslip_run.company_id.vat = '123456789'
        self.multi_payslip_run.company_id.partner_id.write({
            'country_id': self.test_country.id,
            'town_id': self.town.id,
            'state_id': self.test_state.id
        })

        self.multi_payslip_run.company_id.write({ 
            'provider_id': self.tech_provider_1.id,
            'country_id': self.test_country.id,
            'town_id': self.town.id,
            'state_id': self.test_state.id
        })

        self.employee.address_home_id.write({
            'country_id': self.env.ref('base.co')})

        self.tech_provider_1.write({
            'url_upload': 'http://168.61.164.173:8093/Services/NominaServices.asmx?wsdl',
        })

        self.multi_payslip_run._generate_electronic_payslip_tech_provider()

    def test_data_payslips_exception(self):
        
        for payslip in self.multi_payslip_run.slip_ids:
            payslip.employee_id = False

        prepare_url = (
            'odoo.addons.bits_api_connect.models.api_connection'
            '.ApiConnection.prepare_connection'
        )

        return_prepare = TestFacturaxionReturns()

        with patch(prepare_url, new=Mock(return_value=return_prepare)):
            self.multi_payslip_run.get_payslips_data()

    def test_action_generate_file_payslip_run_without_lines(self):

        self.payslip_run_without_lines.company_id.vat = '123456789'
        self.payslip_run_without_lines.company_id.partner_id.write({
            'country_id': self.test_country.id,
            'town_id': self.town.id,
            'state_id': self.test_state.id
        })

        self.payslip_run_without_lines.company_id.write({
            'provider_id': self.tech_provider_1.id,
            'country_id': self.test_country.id,
            'town_id': self.town.id,
            'state_id': self.test_state.id
        })

        self.employee.address_home_id.write({
            'country_id': self.env.ref('base.co')})
        prepare_url = (
            'odoo.addons.bits_api_connect.models.api_connection'
            '.ApiConnection.prepare_connection'
        )

        return_prepare = TestFacturaxionReturns()

        with patch(prepare_url, new=Mock(return_value=return_prepare)):
            self.payslip_run_without_lines.send_massive_file()
            self.payslip_run_without_lines.get_state_dian_massive_payslip()

    def test_action_upload_rejected_one(self):
        self.multi_payslip_run.company_id.vat = '123456789'
        self.multi_payslip_run.company_id.partner_id.write({
            'country_id': self.test_country.id,
            'town_id': self.town.id,
            'state_id': self.test_state.id
        })

        self.multi_payslip_run.company_id.write({ 
            'provider_id': self.tech_provider_1.id,
            'country_id': self.test_country.id,
            'town_id': self.town.id,
            'state_id': self.test_state.id
        })

        self.employee.address_home_id.write({
            'country_id': self.env.ref('base.co')})

        prepare_url = (
            'odoo.addons.bits_api_connect.models.api_connection'
            '.ApiConnection.prepare_connection'
        )

        test_obj = TestFacturaxionReturns()
        test_obj.condition = "upload_rejected_one"
        return_prepare = test_obj

        self.env.company.provider_id = self.tech_provider_1.id

        with patch(prepare_url, new=Mock(return_value=return_prepare)):
            self.multi_payslip_run.send_massive_file()

    def test_action_upload_rejected_multi(self):
        self.multi_payslip_run.company_id.vat = '123456789'
        self.multi_payslip_run.company_id.partner_id.write({
            'country_id': self.test_country.id,
            'town_id': self.town.id,
            'state_id': self.test_state.id
        })

        self.multi_payslip_run.company_id.write({ 
            'provider_id': self.tech_provider_1.id,
            'country_id': self.test_country.id,
            'town_id': self.town.id,
            'state_id': self.test_state.id
        })

        self.employee.address_home_id.write({
            'country_id': self.env.ref('base.co')})

        prepare_url = (
            'odoo.addons.bits_api_connect.models.api_connection'
            '.ApiConnection.prepare_connection'
        )
        
        test_obj = TestFacturaxionReturns()
        test_obj.condition = "upload_rejected_multi"
        return_prepare = test_obj

        self.env.company.provider_id = self.tech_provider_1.id

        with patch(prepare_url, new=Mock(return_value=return_prepare)):
            self.multi_payslip_run._generate_electronic_payslip_tech_provider()

    def test_action_upload_accepted_without_cune(self):
        self.multi_payslip_run.company_id.vat = '123456789'
        self.multi_payslip_run.company_id.partner_id.write({
            'country_id': self.test_country.id,
            'town_id': self.town.id,
            'state_id': self.test_state.id
        })

        self.multi_payslip_run.company_id.write({ 
            'provider_id': self.tech_provider_1.id,
            'country_id': self.test_country.id,
            'town_id': self.town.id,
            'state_id': self.test_state.id
        })

        self.employee.address_home_id.write({
            'country_id': self.env.ref('base.co')})

        prepare_url = (
            'odoo.addons.bits_api_connect.models.api_connection'
            '.ApiConnection.prepare_connection'
        )

        test_obj = TestFacturaxionReturns()
        test_obj.condition = "upload_accepted_without_cune"
        return_prepare = test_obj

        self.env.company.provider_id = self.tech_provider_1.id

        multi_payslip_runs = self.hr_payslip_run.browse(
            [
                self.multi_payslip_run.id, 
                self.payslip_run.id
            ]
        )

        with patch(prepare_url, new=Mock(return_value=return_prepare)):
            multi_payslip_runs.send_massive_file()

    def test_action_download_without_results(self):
        self.multi_payslip_run.company_id.vat = '123456789'
        self.multi_payslip_run.company_id.partner_id.write({
            'country_id': self.test_country.id,
            'town_id': self.town.id,
            'state_id': self.test_state.id
        })

        self.multi_payslip_run.company_id.write({ 
            'provider_id': self.tech_provider_1.id,
            'country_id': self.test_country.id,
            'town_id': self.town.id,
            'state_id': self.test_state.id
        })

        self.multi_payslip_run.write({
            'ep_transaction_id': "IDTN-0000003784",
        })

        self.employee.address_home_id.write({
            'country_id': self.env.ref('base.co')})

        prepare_url = (
            'odoo.addons.bits_api_connect.models.api_connection'
            '.ApiConnection.prepare_connection'
        )

        test_obj = TestFacturaxionReturns()
        test_obj.condition = "download_without_results"
        return_prepare = test_obj

        self.env.company.provider_id = self.tech_provider_1.id

        multi_payslip_runs = self.hr_payslip_run.browse(
            [
                self.multi_payslip_run.id, 
                self.payslip_run.id
            ]
        )

        with patch(prepare_url, new=Mock(return_value=return_prepare)):
            multi_payslip_runs.get_state_dian_massive_payslip()
        
        test_obj = TestFacturaxionReturns()
        test_obj.condition = False
        return_prepare = test_obj

        self.env.company.provider_id = self.tech_provider_1.id

        multi_payslip_runs = self.hr_payslip_run.browse(
            [
                self.multi_payslip_run.id, 
                self.payslip_run.id
            ]
        )

        with patch(prepare_url, new=Mock(return_value=return_prepare)):
            multi_payslip_runs.get_state_dian_massive_payslip()

    def test_action_generate_file_payslip_wrong_ext(self):
        
        self.tech_provider_1.write({
            'file_adapter': '',
        })

        self.payslip_run.company_id.vat = '123456789'
        self.payslip_run.company_id.partner_id.write({
            'country_id': self.test_country.id,
            'town_id': self.town.id,
            'state_id': self.test_state.id
        })

        self.payslip_run.company_id.write({
            'provider_id': self.tech_provider_1.id,
            'country_id': self.test_country.id,
            'town_id': self.town.id,
            'state_id': self.test_state.id
        })

        self.employee.address_home_id.write({
            'country_id': self.env.ref('base.co')})
        prepare_url = (
            'odoo.addons.bits_api_connect.models.api_connection'
            '.ApiConnection.prepare_connection'
        )

        return_prepare = TestFacturaxionReturns()

        with patch(prepare_url, new=Mock(return_value=return_prepare)):
            self.payslip_run.send_massive_file()

    def test_exit_functions(self):

        prepare_url = (
            'odoo.addons.bits_api_connect.models.api_connection'
            '.ApiConnection.prepare_connection'
        )

        return_prepare = TestFacturaxionReturns()

        with patch(prepare_url, new=Mock(return_value=return_prepare)):
            self.hr_payslip_run.get_payslips_related()
            self.hr_payslip_run.get_payslips_data()
            self.hr_payslip_run.get_mass_file_number()
            self.hr_payslip_run.sort_payslips_data()
            self.hr_payslip_run.generate_epayroll_file()
            self.hr_payslip_run._generate_electronic_payslip_tech_provider()
            self.hr_payslip_run._get_payslips_rejected()
            self.hr_payslip_run.get_total_massive_payslip(False, False)

    def test_incomplete_tag_fields(self):

        self.multi_payslip_run.company_id.vat = '123456789'
        self.multi_payslip_run.company_id.partner_id.write({
            'country_id': self.test_country.id,
            'town_id': self.town.id,
            'state_id': self.test_state.id
        })

        self.multi_payslip_run.company_id.write({
            'provider_id': self.tech_provider_1.id,
            'country_id': self.test_country.id,
            'town_id': self.town.id,
            'state_id': self.test_state.id
        })

        employeee_email = self.env.ref('l10n_co_tech_provider.l10n_co_tech_provider_payroll_line_field_159')
        employeee_email.unlink()

        self.employee.address_home_id.write({
            'country_id': self.env.ref('base.co')})
        prepare_url = (
            'odoo.addons.bits_api_connect.models.api_connection'
            '.ApiConnection.prepare_connection'
        )

        return_prepare = TestFacturaxionReturns()

        with patch(prepare_url, new=Mock(return_value=return_prepare)):
            self.multi_payslip_run.send_massive_file()

    def test_slips_results(self):

        prepare_url = (
            'odoo.addons.bits_api_connect.models.api_connection'
            '.ApiConnection.prepare_connection'
        )

        return_prepare = TestFacturaxionReturns()

        with patch(prepare_url, new=Mock(return_value=return_prepare)):
            self.multi_payslip_run.update_slips_results(False)
            provider = self.multi_payslip_run._get_active_tech_provider()
            api_conection = self.multi_payslip_run._create_api_connection(
                provider=provider
            )
            result_vals = self.multi_payslip_run.get_result_massive_payslip(
                provider, 
                api_conection,
            )

    def test_get_result_massive_wo_res_2(self):

        self.multi_payslip_run.company_id.vat = '123456789'
        self.multi_payslip_run.company_id.partner_id.write({
            'country_id': self.test_country.id,
            'town_id': self.town.id,
            'state_id': self.test_state.id
        })

        self.multi_payslip_run.company_id.write({ 
            'provider_id': self.tech_provider_1.id,
            'country_id': self.test_country.id,
            'town_id': self.town.id,
            'state_id': self.test_state.id
        })

        self.multi_payslip_run.update_dian_transaction_id('IDTN-0000003253')

        self.employee.address_home_id.write({
            'country_id': self.env.ref('base.co')})

        prepare_url = (
            'odoo.addons.bits_api_connect.models.api_connection'
            '.ApiConnection.prepare_connection'
        )

        test_obj = TestFacturaxionReturns()
        test_obj.condition = "download_results_wo_res_2"
        return_prepare = test_obj

        self.env.company.provider_id = self.tech_provider_1.id

        with patch(prepare_url, new=Mock(return_value=return_prepare)):
            self.multi_payslip_run.get_state_dian_massive_payslip()

        test_obj = TestFacturaxionReturns()
        test_obj.condition = "download_results_wo_details_payslip"
        return_prepare = test_obj

        self.env.company.provider_id = self.tech_provider_1.id

        with patch(prepare_url, new=Mock(return_value=return_prepare)):
            self.multi_payslip_run.get_state_dian_massive_payslip()

        test_obj = TestFacturaxionReturns()
        test_obj.condition = "download_results_with_pdf"
        return_prepare = test_obj

        self.env.company.provider_id = self.tech_provider_1.id

        with patch(prepare_url, new=Mock(return_value=return_prepare)):
            self.multi_payslip_run.get_state_dian_massive_payslip()
