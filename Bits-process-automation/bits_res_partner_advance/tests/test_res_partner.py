import random

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase
from odoo.tests.common import Form


class TestResPartner(TransactionCase):

    def setUp(self):
        super(TestResPartner, self).setUp()
        self.ResPartner = self.env['res.partner']
        self.search_partner = self.ResPartner.search([])
        for partner in self.search_partner:
            identification_card = random.randint(100000, 600000) + 1000000000
            partner.write({
                'document_type': '31',
                'number_identification': str(identification_card),
                'company_type': 'company'
            })

    # Verification that when entering a number with a length
    # greater than 10 an exception is fired

    def test_validation_ti_length(self):
        with self.assertRaises(ValidationError):
            self.ResPartner.create({
                'name': 'Jaider Manzano',
                'document_type': '12',
                'number_identification': '1545784578454545',
                'company_type': 'person'
            })

    def test_validation_cc_length(self):
        with self.assertRaises(ValidationError):
            self.ResPartner.create({
                'name': 'Jhon Castrillon',
                'document_type': '13',
                'number_identification': '18878473483',
                'company_type': 'person'
            })

    def test_validation_ce_length(self):
        with self.assertRaises(ValidationError):
            self.ResPartner.create({
                'name': 'Jhon Castrillon',
                'document_type': '22',
                'number_identification': '14586589568211221',
                'company_type': 'person'
            })

    def test_validation_ti_alphanumeric(self):
        with self.assertRaises(ValidationError):
            self.ResPartner.create({
                'name': 'Andres Ayala',
                'document_type': '12',
                'number_identification': '100543i483',
                'company_type': 'person'
            })

    def test_validation_cc_alphanumeric(self):
        with self.assertRaises(ValidationError):
            self.ResPartner.create({
                'name': 'Andres Gonzalez',
                'document_type': '13',
                'number_identification': '100574i356',
                'company_type': 'person'
            })

    def test_validation_ce_alphanumeric(self):
        with self.assertRaises(ValidationError):
            self.ResPartner.create({
                'name': 'Andres Loaiza',
                'document_type': '22',
                'number_identification': '100654i377',
                'company_type': 'person'
            })

    def test_validation_pa_alphanumeric(self):
        with self.assertRaises(ValidationError):
            self.ResPartner.create({
                'name': 'Rogelio Andrade',
                'document_type': '41',
                'number_identification': '1005776446',
                'company_type': 'person'
            })

    def test_validation_pa_length(self):
        with self.assertRaises(ValidationError):
            self.ResPartner.create({
                'name': 'Andrea Cuellar',
                'document_type': '41',
                'number_identification': 'C3s6',
                'company_type': 'person'
            })

    def test_verification_pa(self):
        partner = self.ResPartner.create({
            'name': 'Gabriel Camargo',
            'document_type': '41',
            'number_identification': 'C363212s32',
            'company_type': 'person'
        })
        self.assertEqual(partner.name, 'Gabriel Camargo')
        self.assertEqual(partner.document_type, '41')
        self.assertEqual(partner.number_identification, 'C363212s32')
        self.assertEqual(partner.company_type, 'person')

    def test_validation_nit_company(self):
        with self.assertRaises(ValidationError):
            self.ResPartner.create({
                'name': 'Andrea Cuellar',
                'document_type': '13',
                'number_identification': '1005770243',
                'company_type': 'company',
                'country_id': self.env.ref('base.co').id
            })

    def test_validation_spaces(self):
        self.form = Form(self.env['res.partner'])
        self.form.name = 'Andrea Cuellar'
        self.form.document_type = '13'
        self.form.number_identification = '19 94 993323'
        self.form.company_type = 'person'
        self.assertTrue(self.form.number_identification == "1994993323")

    def test_validation_field_empty(self):
        with self.assertRaises(ValidationError):
            self.ResPartner.create({
                'name': 'Ramiro Cardenas',
                'document_type': '13',
                'company_type': 'person'
            })

    def test_correct_creation_for_ce(self):
        self.ResPartner.create({
            'name': 'Fernando Contreras',
            'document_type': '22',
            'number_identification': '15547747',
            'company_type': 'person'
        })

    def test_validation_for_empty_type_document(self):
        with self.assertRaises(ValidationError):
            self.ResPartner.create({
                'name': 'Antonio Gavilan',
                'number_identification': '3533367847',
                'company_type': 'person'
            })

    def test_validation_first_name(self):
        partner1 = self.ResPartner.new({
            'l10n_co_document_type': 'national_citizen_id',
            'vat': '1033515415'
        })
        partner1._on_change_name()
        partner1._compute_verification_code()

    def test_validation_name(self):
        partner2 = self.ResPartner.new({
            'first_name': 'Usuario',
            'l10n_co_document_type': 'national_citizen_id',
            'vat': '1033515415',
            'l10n_co_document_type': 'rut'
        })
        partner2._on_change_l10n_co_document_type()
        partner2._on_change_name()
        partner2._on_change_vat()
        partner2._compute_verification_code()

    def test_validation_check_vat(self):
        identification_card = random.randint(100000, 600000) + 1000000000
        self.ResPartner.create({
            'document_type': '31',
            'number_identification': str(identification_card),
            'vat': str(identification_card),
            'l10n_co_document_type': 'rut',
            'company_type': 'company',
            'name': 'Company Test'
        })

    # def test_validation_check_vat_install_module(self):
    #     module = self.env.ref('base.module_base_vat')
    #     module.button_immediate_install()
    #     identification_card = random.randint(100000, 600000) + 1000000000
    #     self.ResPartner.create({
    #         'document_type': '31',
    #         'number_identification': str(identification_card),
    #         'vat': str(identification_card),
    #         'l10n_co_document_type': 'rut',
    #         'company_type': 'company',
    #         'name': 'Company Test'
    #     })
    #     module.button_immediate_uninstall()
