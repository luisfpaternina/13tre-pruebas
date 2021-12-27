# -*- coding: utf-8 -*-

from odoo.fields import Date
from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestBaseResPartner(TransactionCase):

    def setUp(self):
        super(TestBaseResPartner, self).setUp()
        self.ref_res_partner = self.env['res.partner']
        self.ref_ciiu = self.env['ciiu']

        self.contact = self.ref_res_partner.create({
            'name': 'partner name',
        })

        self.ciiu = self.ref_ciiu.create({
            'name': 'SECCIÓN A',
            'code': 'SECCIÓN A ',
            'description': ' AGRICULTURA, GANADERÍA, CAZA...',
            'has_parent': False,
            'has_division': False,
            'has_section': False,
        })

        self.section = self.ref_ciiu.create({
            'code': '1 ',
            'description': ' Agricultura, ganadería, caza...',
            'section': self.ciiu.id,
            'has_parent': False,
            'has_division': False,
            'has_section': True,
        })

        self.division = self.ref_ciiu.create({
            'name': 'division',
            'code': '11 ',
            'description': ' Cultivos agrícolas transitorios ',
            'division': self.section.id,
            'has_parent': False,
            'has_section': False,
            'has_division': True,
        })

        self.parent = self.ref_ciiu.create({
            'name': 'parent',
            'code': '111 ',
            'description': ' Cultivo de cereales (excepto arroz)... ',
            'parent': self.division.id,
            'has_parent': True,
            'has_section': False,
            'has_division': False,
        })
