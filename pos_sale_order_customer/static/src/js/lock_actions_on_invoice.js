odoo.define('pos_sale_order_customer.lock_mode', function(require) {
    "use strict";

    var screens = require('point_of_sale.screens');
    var ProductListWidget = screens.ProductListWidget;
    var OrderWidget = screens.OrderWidget;
    var ClientListScreenWidget = screens.ClientListScreenWidget;

    var ResetButton = screens.ActionButtonWidget.extend({
        template: "ResetButton",
        button_click: function () {
            var order = this.pos.get_order();
            order.destroy();
            this.pos.db.origin_sale_order_pos = false;
            this.pos.db.origin_invoice_pos = false;
            return;
        },
    });

    screens.define_action_button({
        name: "reset_button",
        widget: ResetButton,
        condition: function () {
            var visible = false;
            var invoices = this.pos.db.invoices;

            if (invoices.length > 0) {
                visible = true;
            }
            return visible;
        },
    });

    ClientListScreenWidget.include({

        save_changes: function () {
            var order = this.pos.get_order();
            if( this.has_client_changed() && !this.pos.db.get_origin_invoice_pos() ){
                var default_fiscal_position_id = _.findWhere(this.pos.fiscal_positions, {'id': this.pos.config.default_fiscal_position_id[0]});
                if ( this.new_client ) {
                    var client_fiscal_position_id;
                    if (this.new_client.property_account_position_id ){
                        client_fiscal_position_id = _.findWhere(this.pos.fiscal_positions, {'id': this.new_client.property_account_position_id[0]});
                    }
                    order.fiscal_position = client_fiscal_position_id || default_fiscal_position_id;
                    order.set_pricelist(_.findWhere(this.pos.pricelists, {'id': this.new_client.property_product_pricelist[0]}) || this.pos.default_pricelist);
                } else {
                    order.fiscal_position = default_fiscal_position_id;
                    order.set_pricelist(this.pos.default_pricelist);
                }

                order.set_client(this.new_client);
            }
        }

    });

    ProductListWidget.include({
        init: function(parent, options) {
            this._super(parent, options);
            var self = this;

            this.click_product_handler = function(event){
                if (self.pos.db.get_origin_invoice_pos() === false){
                    var product = self.pos.db.get_product_by_id(this.dataset.productId);
                    options.click_product_action(product);
                }
            }
        }
    });

    OrderWidget.include({

        set_value: function(val) {
            var order = this.pos.get_order();
            var self = this;
            if (self.pos.db.get_origin_invoice_pos() === false){
                if (order.get_selected_orderline()) {
                    var mode = this.numpad_state.get('mode');
                    if( mode === 'quantity'){
                        order.get_selected_orderline().set_quantity(val);
                    }else if( mode === 'discount'){
                        order.get_selected_orderline().set_discount(val);
                    }else if( mode === 'price'){
                        var selected_orderline = order.get_selected_orderline();
                        selected_orderline.price_manually_set = true;
                        selected_orderline.set_unit_price(val);
                    }
                    if (this.pos.config.iface_customer_facing_display) {
                        this.pos.send_current_order_to_customer_facing_display();
                    }
                }
            }
        },

    });

});