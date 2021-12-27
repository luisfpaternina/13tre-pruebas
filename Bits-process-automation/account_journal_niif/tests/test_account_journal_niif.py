from odoo.tests.common import TransactionCase


class TestAccountJournalNiif(TransactionCase):

    def setUp(self):
        super(TestAccountJournalNiif, self).setUp()
        self.Journal = self.env['account.journal']

    def test_create_new_journal(self):
        new_journal = self.Journal.create({
            "name": "Test Journal",
            "type": "sale",
            "code": "0011",
            "accounting": "niif"
        })
