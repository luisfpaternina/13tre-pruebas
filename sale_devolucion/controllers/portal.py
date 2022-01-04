
import werkzeug
from odoo import fields as odoo_fields, http, tools, _, SUPERUSER_ID
from odoo.http import request
from odoo.exceptions import AccessError, MissingError

class SaleDevolucionController(http.Controller):

    def _document_check_access(self, model_name, document_id, access_token=None):
        document = request.env[model_name].browse([document_id])
        document_sudo = document.with_user(SUPERUSER_ID).exists()
        if not document_sudo:
            raise MissingError(_("This document does not exist."))
        try:
            document.check_access_rights('read')
            document.check_access_rule('read')
        except AccessError:
            if not access_token or not document_sudo.access_token or not consteq(document_sudo.access_token, access_token):
                raise
        return document_sudo


    @http.route("/my/orders/devolucion/<int:order_id>", type="http", auth="user")
    def crear_sale_devolucion(self, order_id, access_token, **kw):
        #Verificar acceso por token
        try:
            order = self._document_check_access('sale.order', order_id, access_token=access_token)
        except (AccessError, MissingError):
            return werkzeug.utils.redirect('/my')


        #Obtener valores pasados en el formulario
        values = {}
        for field_name, field_value in kw.items():
            if field_name.endswith("_id"):
                values[field_name] = int(field_value)
            else:
                values[field_name] = field_value

        #Obtener pedido

        #order = (
        #    http.request.env["sale.order"]
        #    .with_user(http.request.env.user.id)
        #    .search([("id", "=", values["order_id"])])
        #)

        order.motivo_devolucion = values.get("motivo_devolucion")
        order.cantidad_devolver = values.get("cantidad_devolver")
        order.status_devolucion= "pendiente"

        #Enviar email
        #email_from="enzo@eaata.eu";
        #email_to="raul.carbonell@processcontrol.es";
        #body="<DIV>El cliente " + order.partner_id.name + " ha pedido la devolución del pedido "  + order.name + "</DIV><BR/><DIV><B>Motivo devolución: </B> " + order.motivo_devolucion + "</DIV><DIV><B>Cantidad a devolver: </B> " + order.cantidad_devolver + "";
        #mail_values = {
        #    'subject': "Pedido Devuelto - " + order.name,
        #    'body_html': body,
        #    'email_to':email_to,
        #    'email_from': email_from,
        #}

        template = request.env.ref('sale_devolucion.sale_devolucion_email_template')

        request.env['mail.template'].browse(template.id).sudo().send_mail(order.id, force_send=True)

        #create_and_send_email = request.env['mail.mail'].sudo().create(mail_values).send()

        return werkzeug.utils.redirect('/my/orders/%s?access_token=%s' % (order_id, access_token or ''))
