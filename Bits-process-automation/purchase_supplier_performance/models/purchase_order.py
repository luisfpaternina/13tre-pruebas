from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    has_qualification = fields.Boolean(string='Has Qualification',
                                       default=False)

    def supplier_qualification(self):
        return {
            'name': ('Supplier Qualification'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'supplier.qualification.wizard',
            'view_id': self.env.ref('purchase_supplier_performance.'
                                    'supplier_qualification_wizard_form').id,
            'target': 'new',
            'context': {'partner_id': self.partner_id.id, 'order_id': self.id,
                        'type_qualification': 'supplier'}
        }

    def action_view_invoice(self):
        if not self.has_qualification:
            raise ValidationError(_("You cannot generate the invoice until you"
                                    " have made the supplier qualification"))
        result = super(PurchaseOrder, self).action_view_invoice()
        return result
