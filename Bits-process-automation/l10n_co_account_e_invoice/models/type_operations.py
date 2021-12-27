
import logging
from odoo import api, fields, models, tools

_logger = logging.getLogger(__name__)


class TypeOperations(models.Model):
    _name = "l10n_co.type_operations"
    _description = "Operacions type"

    name = fields.Char(
        required=True,
        readonly=True)
    code = fields.Char(
        required=False,
        readonly=True)
    cufe_algorithm = fields.Char(
        required=False,
        readonly=True)
    prefix = fields.Char(
        required=False,
        readonly=True)
    type = fields.Char(
        string="Document type",
        required=False,
        readonly=True)
