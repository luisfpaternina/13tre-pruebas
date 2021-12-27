odoo.define("pos_sale_order_customer.order", function (require) {
    "use strict";

    var core = require("web.core");
    var gui = require("point_of_sale.gui");
    var models = require("point_of_sale.models");
    var PosDb = require("point_of_sale.DB");
    var utils = require("web.utils");
    var screens = require("point_of_sale.screens");
    var rpc = require("web.rpc");
    var chrome = require("point_of_sale.chrome");

    var _super_order = models.Order.prototype;
    models.Order = models.Order.extend({
        initialize: function (session, attributes) {
            _super_order.initialize.apply(this, arguments);
        },
        export_as_JSON: function() {
            var orderLines, paymentLines;
            orderLines = [];
            this.orderlines.each(_.bind( function(item) {
                return orderLines.push([0, 0, item.export_as_JSON()]);
            }, this));
            paymentLines = [];
            this.paymentlines.each(_.bind( function(item) {
                return paymentLines.push([0, 0, item.export_as_JSON()]);
            }, this));
            var json = {
                name: this.get_name(),
                amount_paid: this.get_total_paid() - this.get_change(),
                amount_total: this.get_total_with_tax(),
                amount_tax: this.get_total_tax(),
                amount_return: this.get_change(),
                lines: orderLines,
                statement_ids: paymentLines,
                pos_session_id: this.pos_session_id,
                pricelist_id: this.pricelist ? this.pricelist.id : false,
                partner_id: this.get_client() ? this.get_client().id : false,
                user_id: this.pos.user.id,
                employee_id: this.pos.get_cashier().id,
                uid: this.uid,
                sequence_number: this.sequence_number,
                creation_date: this.validation_date || this.creation_date, // todo: rename creation_date in master
                fiscal_position_id: this.fiscal_position ? this.fiscal_position.id : false,
                server_id: this.server_id ? this.server_id : false,
                to_invoice: this.to_invoice ? this.to_invoice : false,
                invoice_origin_pos: this.pos.db.origin_invoice_pos,
                sale_order_origin_pos: this.pos.db.origin_sale_order_pos,
            };
            if (!this.is_paid && this.user_id) {
                json.user_id = this.user_id;
            }
            return json;
        },
        finalize: function(){
            this.destroy();
            window.location.reload();
        },
    });

});