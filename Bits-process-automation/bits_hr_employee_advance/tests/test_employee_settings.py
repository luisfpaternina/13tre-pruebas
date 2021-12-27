from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError
from datetime import date, datetime, timedelta
import re


class TestHrEmployee(TransactionCase):

    def setUp(self):
        super(TestHrEmployee, self).setUp()
        config = self.env['res.config.settings'].create({})
