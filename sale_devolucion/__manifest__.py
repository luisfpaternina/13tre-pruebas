# Copyright 2020 Raul Carbonell - raul.carbonell@processcontrol.es
# License AGPL-3.0 or later
{
    "name": "Sale Devolución",
    "summary":
         "Poder indicar desde el portal que se tiene que hacer una devolución de un pedido",
    "version": "13.0.1.0.0",
    "category": "undefined",
    "website": "",
    "author": "Raul Carbonell",
    "license": "AGPL-3",
    "data": [
        "data/mail_template_data.xml",
        "views/portal_sale_devolucion_template.xml",
        "views/sale_order_views.xml",
    ],
    "depends": [
        "base",
        "sale",
    ],
    "application": False,
    "installable": True,
}
