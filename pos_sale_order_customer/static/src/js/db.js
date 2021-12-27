odoo.define('pos_sale_order_customer.db', function(require) {
    "use strict";
    var db = require('point_of_sale.DB');
    
    db.include({
        init: function(options) {
            this._super.apply(this, arguments);
            this.origin_invoice_pos = false;
            this.origin_sale_order_pos = false;
        },
    
        get_client: function(quotations) {
            return this.get('client');
        },

        get_current_invoice: function(){
            return this.current_invoice;
        },

        get_origin_invoice_pos: function(){
            return this.origin_invoice_pos;
        },

        get_origin_sale_order_pos: function(){
            return this.origin_sale_order_pos;
        },

    });
    return db
});