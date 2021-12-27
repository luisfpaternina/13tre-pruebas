odoo.define('pos_sale_order_customer.validate_invoice_draft', function(require){
    "use strict";

    var screens = require('point_of_sale.screens');
    var rpc = require('web.rpc');
    var PaymentScreenWidget = screens.PaymentScreenWidget;

    // PaymentScreenWidget.include({
    //     validate_order: function(force_validation) {
    //         var self = this;
    //         var order = self.pos.get_order();
    //         if (this.order_is_valid(force_validation)) {
    //             this.finalize_validation();
                
    //         }
    //         rpc.query({
    //             model: 'sale.order',
    //             method: 'invoice_origin_pos_to_post',
    //             args: [{
    //                 'self': order,
    //                 'invoice_id': self.pos.db.origin_invoice_pos,
    //             }]
    //         });
    //         console.log(order.state);
    //         console.log(this);
    //     }
    // });

});