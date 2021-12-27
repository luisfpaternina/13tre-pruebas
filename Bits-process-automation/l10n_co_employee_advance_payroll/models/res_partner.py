from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError


class RestPartner(models.Model):
    _inherit = 'res.partner'

    l10n_co_document_type = fields.Selection(selection_add=[
        ('47', 'PEP'),
        ('50', 'NIT of other Country'),
        ('91', 'NUIP*')])
