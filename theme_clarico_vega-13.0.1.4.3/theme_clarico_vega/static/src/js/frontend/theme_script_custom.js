/**************************************************
        01. Search in Header
        02. Page Scroll up
        03. Theme Wishlist
        04. Shop Events
        05. cart Popover
        06. Theme layout
        07. Compare short name
**************************************************/
odoo.define('theme_clarico_vega.theme_script', function(require) {
    'use strict';

    var sAnimations = require('website.content.snippets.animation');
    var publicWidget = require('web.public.widget');
    var Widget = require('web.Widget');
    var core = require('web.core');
    var _t = core._t
    var ajax = require('web.ajax');
    var config = require('web.config');
    var sale = new sAnimations.registry.WebsiteSale();

    console.log("Registro web");

});