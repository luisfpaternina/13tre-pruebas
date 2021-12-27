odoo.define("bi_pos_import_sale.pos", function (require) {
    "use strict";

    var core = require("web.core");
    var gui = require("point_of_sale.gui");
    var models = require("point_of_sale.models");
    var PosDb = require("point_of_sale.DB");
    var utils = require("web.utils");
    var screens = require("point_of_sale.screens");
    var rpc = require("web.rpc");
    var chrome = require("point_of_sale.chrome");

    var exports = {};

    var _super_order = models.Order.prototype;
    models.Order = models.Order.extend({
        initialize: function (session, attributes) {
            _super_order.initialize.apply(this, arguments);
        },
        remove_orderline: function( line ){
            this.assert_editable();
            this.orderlines.remove(line);
            this.select_orderline(this.get_last_orderline());
        },
    });

});