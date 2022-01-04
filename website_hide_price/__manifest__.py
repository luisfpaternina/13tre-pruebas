# Copyright 2020 Raul Carbonell - raul.carbonell@processcontrol.es
# License AGPL-3.0 or later
{
    "name": "WebSite Hide Price",
    "summary":
         "Ocultar precio de los productos de la web al cliente publico o clientes marcados manualmente",
    "version": "13.0.1.0.0",
    "category": "undefined",
    "website": "",
    "author": "Raul Carbonell",
    "license": "AGPL-3",
    "data": [
        "views/res_partner_views.xml",
        "views/website_sale_templates.xml",
        "views/product_template_views.xml",        
    ],
    "depends": [
        "base",
        "website_sale",
    ],
    "application": False,
    "installable": True,
}
