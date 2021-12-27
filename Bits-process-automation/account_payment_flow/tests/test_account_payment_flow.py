from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase
from datetime import datetime


class TestAccountPaymentFlow(TransactionCase):

    def setUp(self):
        super(TestAccountPaymentFlow, self).setUp()
        self.AccountPaymentFlow = self.env['account.payment.flow']
        self.ResCompany = self.env['res.company'].search([])
        self.AccountAccount = self.env['account.account']
        self.AccountAccountType = self.env['account.account.type']
        self.ResPartner = self.env['res.partner']
        self.ResBank = self.env['res.bank']
        self.ResPartnerBank = self.env['res.partner.bank']
        self.AccountJournal = self.env['account.journal']
        self.AccountMove = self.env['account.move']
        self.AccountPaymentFlowTeam = self\
            .env['account.payment.flow.stage.team']
        self.ResGroups = self.env['res.groups']
        self.Mail = self.env['mail.template']

        self.env.user = self.env['res.users'].browse(2)

        self.account_account_type = self.AccountAccountType.create({
            'name': 'Gastos de administración',
            'type': 'other',
            'internal_group': 'expense'
        })

        self.account_bank = self.AccountAccount.create({
            'code': "10151206",
            'name': "TEST Account Bank",
            'user_type_id': self.account_account_type.id
        })

        self.res_partner = self.ResPartner.create({
            'name': "Partner Test"
        })
        self.res_bank = self.ResBank.create({
            'name': "Test Res Bank",
            'bic': "5"
        })

        self.res_group = self.env['res.groups'].search([
            ('users', 'not in', [self.env.user.id])
        ], limit=1)

        self.res_group_admin = self.env.user.groups_id[0]

        self.res_partner_bank = self.ResPartnerBank.create({
            'bank_id': self.res_bank.id,
            'partner_id': self.ResCompany.partner_id.id,
            'acc_number': "159753456"
        })
        self.account_journal = self.AccountJournal.create({
            "name": "Test Bank",
            "code": "TESB",
            "type": "general",
            'default_credit_account_id': self.account_bank.id,
            'default_debit_account_id':  self.account_bank.id,
            'bank_account_id': self.res_partner_bank.id
        })
        self.account_payment_flow = self.AccountPaymentFlow.create({
            'partner_id': self.res_partner.id,
            'journal_id': self.account_journal.id,
            'payment_instructions': '1) instructions',
            'payment_method_id': self.env
            .ref('account_payment_flow.account_payment_method_pse').id
        })

        self.account_move = self.AccountMove.create({
            'name': 'Invoice Test',
            'ref': 'Test',
            'date': datetime.now(),
            'journal_id': self.account_journal.id,
            'payment_flow_id': self.account_payment_flow.id
        })

        self.template_email = self.Mail.search([
            ('name',
             '=',
             'Template: Prepare Payment')
        ], limit=1)

        self.stage = self.env\
            .ref('account_payment_flow.stage_payment_flow_1')
        self.next_stage = self.env\
            .ref('account_payment_flow.stage_payment_flow_2')

    def test_email_template(self):
        self.account_payment_flow._track_template(changes={})

    def test_open_wizard(self):
        self.account_move.action_invoice_payment_flow()
        self.account_move._compute_allowed_payment()

    def test_functions_flow(self):
        self.account_payment_flow._get_partner()
        self.account_payment_flow._compute_payment_check()

        self.account_payment_flow._onchange_field()
        self.account_payment_flow._validate_groups(self.stage)
        self.account_payment_flow._get_stage_ids(False, [], False)

    def test_register_payment(self):
        self.account_payment_flow\
            .with_context({
                'active_ids': False
            })._action_register_payment_flow()

    def test_register_record(self):
        self.account_payment_flow\
            .with_context({
                'active_id': self.account_move.id
            }).register_record()

    def test_validate_groups_error(self):
        with self.assertRaises(ValidationError):

            self.AccountPaymentFlowTeam.create({
                'name': 'group test 2',
                'team_stage_rel': self.next_stage.id,
                'group': self.res_group.id
            })

            self.account_payment_flow\
                .write({
                    'stage_id': self.next_stage.id
                })

    def test_validate_previus_stage(self):
        with self.assertRaises(ValidationError):

            self.account_payment_flow.write({
                'stage_id': self.next_stage.id
            })

            self.account_move.write({
                'invoice_payment_state': 'paid'
            })

            self.account_payment_flow.write({
                'stage_id': self.stage.id
            })

    def test_validate_groups_success(self):

        self.AccountPaymentFlowTeam.create({
            'name': 'group test 2',
            'team_stage_rel': self.next_stage.id,
            'group': self.res_group_admin.id
        })

        self.next_stage.write({
            'template_id': self.template_email.id
        })

        self.account_payment_flow\
            .write({
                'stage_id': self.next_stage.id
            })

    def test_change_group_with_partner(self):
        self.stage.write({
            'partner_id': self.res_partner.id
        })

        self.account_payment_flow.write({
            'stage_id': self.stage.id
        })
        self.account_payment_flow._compute_purchase_order_invoice()
