{
    # Theme information

    'name': 'Theme Clarico Vega ProcessControl Alter',
    'category': 'Theme/eCommerce',
    'summary': 'Fully Responsive, Clean, Modern & Sectioned Odoo Theme. Crafted to be Pixel Perfect, It is suitable for eCommerce Businesses like Furniture, Fashion, Electronics, Beauty, Health & Fitness, Jewellery, Sports etc.',
    'version': '1.4.3',
    'license': 'OPL-1',
    'depends': [
        'website_theme_install',
        'website_sale_wishlist',
        'sale_product_configurator',
        'website_sale_stock',
    ],

    'data': [
	    #'security/groups.xml',
	    'security/ir.model.access.csv',
        'templates/shop.xml',
        'views/views.xml',
    ],

    # Odoo Store Specific
    'live_test_url': 'http://claricovega.theme13demo.emiprotechnologies.com/',
    'images': [
        'static/description/main_poster.jpg',
        'static/description/main_screenshot.gif',
    ],

    # Author
    'author': 'ProcessControl',
    'website': 'https://www.processcontrol.es',
    'maintainer': 'ProcessControl',

    # Technical
    'installable': True,
    'auto_install': False,
    'price':0.00,
    'currency': 'EUR',
}
