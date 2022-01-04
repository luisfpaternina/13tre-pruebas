# Copyright 2020 Raul Carbonell - raul.carbonell@processcontrol.es
# License AGPL-3.0 or later
{
    "name": "Shop button - Ecommerce",
    "summary":
         "Añadir el boton de comprar directamente en la vista de los product_items. (sin entrar dentro del producto)",
    "version": "13.0.1.0.0",
    "category": "undefined",
    "website": "",
    "author": "Raul Carbonell",
    "license": "AGPL-3",
    "data": [
        "views/website_sale_products_item_shop_button.xml",
    ],
    "depends": [
        "base",
        "website_sale",
        "website_hide_price"
    ],
    "application": False,
    "installable": True,
}
