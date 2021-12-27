odoo.define("pos_sale_order_customer", function (require) {
    "use strict";

    var core = require("web.core");
    var gui = require("point_of_sale.gui");
    var models = require("point_of_sale.models");
    var PosDb = require("point_of_sale.DB");
    var screens = require("point_of_sale.screens");
    var rpc = require("web.rpc");
    var chrome = require("point_of_sale.chrome");

    var QWeb = core.qweb;
    var _t = core._t;

    chrome.Chrome.include({
        build_widgets: function () {
            this._super();
            // For compatibility with https://www.odoo.com/apps/modules/12.0/pos_mobile/
            if (odoo.is_mobile) {
                var payment_method = $(
                    ".invoice-payment-screen .paymentmethods-container"
                );
                payment_method.detach();
                $(".invoice-payment-screen .paymentlines-container").after(
                    payment_method
                );

                $(".invoice-payment-screen .touch-scrollable").niceScroll();
            }
        },
    });

    models.load_models({
        model: "account.move",
        fields: [
            "name",
            "partner_id",
            "invoice_date",
            "invoice_date_due",
            "invoice_origin",
            "amount_total",
            "invoice_user_id",
            "amount_residual",
            "invoice_payment_state",
            "amount_untaxed",
            "amount_tax",
            "state",
            "type",
            "num_id_partner",
        ],
        domain: [
            ["invoice_payment_state", "=", "not_paid"],
            ["state", "in", ["posted", "draft"]],
            ["type", "=", "out_invoice"],
        ],
        loaded: function (self, invoices) {
            _.each(invoices, function (invoice) {
                invoice.user_id = invoice.invoice_user_id;
            });

            var invoices_ids = _.pluck(invoices, "id");
            self.prepare_invoices_data(invoices);
            self.invoices = invoices;
            self.db.add_invoices(invoices);
            self.get_invoice_lines(invoices_ids);
        },
    });

    
    var _super_posmodel = models.PosModel.prototype;
    models.PosModel = models.PosModel.extend({
        initialize: function (session, attributes) {
            _super_posmodel.initialize.apply(this, arguments);
        },

        fetch_lines: function (data, model_name, method_name, fields) {
            return rpc.query({
                model: model_name,
                method: method_name,
                args: [data, fields],
            });
        },

        get_invoice_lines: function (data) {
            var self = this;
            data = data || [];
            return this.fetch_lines(
                [["move_id", "in", data]],
                "account.move.line",
                "search_read",
                [
                    "id",
                    "move_id",
                    "name",
                    "account_id",
                    "product_id",
                    "price_unit",
                    "quantity",
                    "tax_ids",
                    "discount",
                    "amount_currency",
                ]
            ).then(function (lines) {
                _.each(lines, function (l) {
                    var invoice = self.db.invoices_by_id[l.move_id[0]];
                    if (!invoice) {
                        return;
                    }
                    invoice.lines = invoice.lines || {};
                    invoice.lines[l.id] = l;
                });
            });
        },

        prepare_invoices_data: function (data) {
            _.each(data, function (item) {
                for (var property in item) {
                    if (Object.prototype.hasOwnProperty.call(item, property)) {
                        if (item[property] === false) {
                            item[property] = " ";
                        }
                    }
                }
            });
        },

        get_res: function (model_name, id) {
            var fields = _.find(this.models, function (model) {
                    return model.model === model_name;
                }).fields,
                domain = [["id", "=", id]];
            return rpc.query({
                model: model_name,
                method: "search_read",
                args: [domain, fields],
            });
        },

        validate_invoice: function (id) {
            return rpc.query({
                model: "account.move",
                method: "action_invoice_open",
                args: [id],
            });
        },

        get_invoices_to_render: function (invoices) {
            var muted_invoices_ids = [],
                order = {},
                id = 0,
                i = 0,
                client = this.get_client(),
                orders_to_mute = _.filter(this.db.get_orders(), function (mtd_order) {
                    return mtd_order.data.invoice_to_pay;
                });
            if (orders_to_mute) {
                for (i = 0; orders_to_mute.length > i; i++) {
                    order = orders_to_mute[i];
                    id = order.data.invoice_to_pay.id;
                    muted_invoices_ids.push(id);
                }
            }
            if (muted_invoices_ids && muted_invoices_ids.length) {
                invoices = _.filter(invoices, function (inv) {
                    return !_.contains(muted_invoices_ids, inv.id);
                });
            }
            if (client) {
                invoices = _.filter(invoices, function (inv) {
                    return inv.partner_id[0] === client.id;
                });
                return invoices;
            }
            invoices = _.filter(invoices, function (inv) {
                return (
                    (inv.state === "posted" || inv.state === "draft") && inv.invoice_payment_state === "not_paid"
                );
            });
            return invoices;
        },

        start_invoice_processing: function () {
            this.add_itp_data = true;
        },

        stop_invoice_processing: function () {
            this.add_itp_data = false;
            // Remove order paymentlines
            var order = this.get_order();
            var lines = order.get_paymentlines();
            for (var i = 0; i < lines.length; i++) {
                order.remove_paymentline(lines[i]);
            }
        },
    });

    PosDb.include({
        init: function (options) {
            this._super(options);
            this.invoices = [];
            this.invoices_by_id = {};
            this.invoices_search_string = "";
        },

        update_invoices_search_string: function (invoices) {
            var self = this;
            self.invoices_search_string = "";
            _.each(invoices, function (inv) {
                self.invoices_search_string += self._invoice_search_string(inv);
            });
        },

        add_invoices: function (invoices) {
            var self = this;
            _.each(invoices, function (invoice) {
                self.invoices.push(invoice);
                self.invoices_by_id[invoice.id] = invoice;
                self.invoices_search_string += self._invoice_search_string(invoice);
            });
        },

        _invoice_search_string: function (invoice) {
            var str = invoice.partner_id[1];
            if (invoice.name) {
                str += "|" + invoice.name;
            }
            if (invoice.invoice_date) {
                str += "|" + invoice.invoice_date;
            }
            if (invoice.invoice_date_due) {
                str += "|" + invoice.invoice_date_due;
            }
            if (invoice.invoice_user_id[1]) {
                str += "|" + invoice.invoice_user_id[1];
            }
            if (invoice.amount_total) {
                str += "|" + invoice.amount_total;
            }
            if (invoice.num_id_partner) {
                str += "|" + invoice.num_id_partner;
            }
            str = String(invoice.id) + ":" + str.replace(":", "") + "\n";
            return str;
        },

        search_invoices: function (query) {
            try {
                query = query.replace(
                    /[\[\]\(\)\+\*\?\.\-\!\&\^\$\|\~\_\{\}\:\,\\\/]/g,
                    "."
                );
                query = query.replace(/ /g, ".+");
                var re = RegExp("([0-9]+):.*?" + query, "gi");
            } catch (e) {
                return [];
            }
            var results = [];
            for (var i = 0; i < this.limit; i++) {
                var r = re.exec(this.invoices_search_string);
                if (r) {
                    var id = Number(r[1]);
                    results.push(this.get_invoice_by_id(id));
                } else {
                    break;
                }
            }
            return results.filter(function (res) {
                return typeof res === "object";
            });
        },

        get_invoice_by_id: function (id) {
            return this.invoices_by_id[id];
        },
    });

    var InvoicesButton = screens.ActionButtonWidget.extend({
        template: "InvoicesButton",
        button_click: function () {
            this.gui.show_screen("invoices_list");
            return;
        },
    });

    screens.define_action_button({
        name: "invoices_button",
        widget: InvoicesButton,
        condition: function () {
            var visible = false;
            var invoices = this.pos.db.invoices;
            // VALIDACION COMPLETA, PERO NO ESTA 100% FUNCIONAL.
            // var client = this.pos.get_order().get_client();
            // if (client){
            //     for (var x=0; x<invoices.length; x++){
            //         if (invoices[x].partner_id[0] == client.id){
            //             console.log(invoices[x].partner_id[0])
            //             visible = true;
            //         }
            //     }
            // } else if (invoices.length > 0){
            //     visible = true;
            // }

            //VALIDACION SOLICITADA
            if (invoices.length > 0){
                visible = true;
            }
            return visible;
        },
    });

    var InvoicesBaseWidget = screens.ScreenWidget.extend({
        show: function () {
            var self = this;
            this._super();
            this.renderElement();

            this.$(".next").click(function (e) {
                e.preventDefault();
                self.click_next(e);
                self.validate_count(e);
            });

            this.render_data(this.get_data());

            this.$(".list-contents").delegate(this.$listEl, "click", function (event) {
                self.select_line(event, $(this), parseInt($(this).data("id"), 10));
            });

            if (this.pos.config.iface_vkeyboard && this.chrome.widget.keyboard) {
                this.chrome.widget.keyboard.connect(this.$(".searchbox input"));
            }

            var search_timeout = null;
            this.$(".searchbox input").on("keypress", function (event) {
                var query = this.value;
                clearTimeout(search_timeout);
                search_timeout = setTimeout(function () {
                    self._search(query);
                }, 70);
            });

            this.$(".searchbox .search-clear").click(function () {
                self._clear_search();
            });

            if (odoo.is_mobile) {
                setTimeout(function () {
                    var width = self.$(".screen-content").width();
                    var height = self.$("table.list").height();
                    var max_height = self.$(".full-content").height();
                    if (height > max_height) {
                        height = max_height;
                    }
                    self.$(
                        ".subwindow-container-fix.touch-scrollable.scrollable-y"
                    ).css({
                        width: width,
                        height: height,
                    });
                    self.$(".touch-scrollable").niceScroll();
                }, 0);
            }
        },
        render_data: function (data) {
            var contents = this.$el[0].querySelector(".list-contents");
            contents.innerHTML = "";
            for (var i = 0, len = Math.min(data.length, 1000); i < len; i++) {
                var item_html = QWeb.render(this.itemTemplate, {
                    widget: this,
                    item: data[i],
                });
                var item_line = document.createElement("tbody");

                var $tr = document.createElement("tr");
                if (data[i].lines) {
                    var $td = document.createElement("td");
                    $td.setAttribute("colspan", this.num_columns);

                    $tr.classList.add("line-element-hidden");
                    $tr.classList.add("line-element-container");
                }
                item_line.innerHTML = item_html;
                item_line = item_line.childNodes[1];

                contents.appendChild(item_line);
                contents.appendChild($tr);
            }
        },
    });

    var InvoicesWidget = InvoicesBaseWidget.extend({
        template: "InvoicesWidget",
        invoice_screen: true,
        init: function () {
            this._super.apply(this, arguments);
            this.$listEl = ".invoice";
            this.itemTemplate = "Invoice";
            this.num_columns = 8;
            this.selected_invoice = false;
        },

        get_data: function () {
            return this.pos.get_invoices_to_render(this.pos.db.invoices);
        },

        show: function () {
            var self = this;
            this._super();

            this.$(".back").click(function () {
                self.gui.back();
            });
        },

        select_line: function (event, $line, id) {
            var invoice = this.pos.db.get_invoice_by_id(id);
            this.$(".list .lowlight").removeClass("lowlight");
            this.$(".line-element-container").addClass("line-element-hidden");
            if ($line.hasClass("highlight")) {
                this.selected_invoice = false;
                $line.removeClass("highlight");
                $line.addClass("lowlight");
                $line.next().addClass("line-element-hidden");
            } else {
                this.$(".list .highlight").removeClass("highlight");
                $line.addClass("highlight");
                this.selected_invoice = invoice;
                $line.next().removeClass("line-element-hidden");
                $line.next().addClass("line-element");
            }
            this.toggle_save_button(this.selected_invoice);
            if (odoo.is_mobile) {
                var height = this.$("table.list").height();
                var max_height = this.$(".full-content").height();
                if (height > max_height) {
                    height = max_height;
                }
                this.$(".subwindow-container-fix.touch-scrollable.scrollable-y").css({
                    height: height,
                });
                this.$(".subwindow-container-fix.touch-scrollable.scrollable-y")
                    .getNiceScroll()
                    .resize();
            }
        },

        toggle_save_button: function (selected_invoice) {
            var $button = this.$(".button.next");
            if (selected_invoice) {
                $button.removeClass("oe_hidden");
            } else {
                $button.addClass("oe_hidden");
            }
        },

        _search: function (query) {
            var invoices = [];
            if (query) {
                invoices = this.pos.db.search_invoices(query);
                invoices = this.pos.get_invoices_to_render(invoices);
                this.render_data(invoices);
            } else {
                invoices = this.pos.db.invoices;
                invoices = this.pos.get_invoices_to_render(invoices);
                this.render_data(invoices);
            }
        },

        _clear_search: function () {
            var invoices = this.pos.db.invoices;
            this.render_data(invoices);
            this.$(".searchbox input")[0].value = "";
            this.$(".searchbox input").focus();
        },

        click_next: function () {
            var order = this.pos.get_order();
            order.remove_orderline(order.get_orderlines());

            var selected_invoice = this.selected_invoice;
            if (selected_invoice){
                for (var line in selected_invoice['lines']){
                    if (selected_invoice['lines'][line]['product_id'] != false){
                        var quantity = selected_invoice['lines'][line]['quantity'];
                        var taxs = selected_invoice['lines'][line]['tax_ids'];
                        var disc = selected_invoice['lines'][line]['discount'];
                        var product_id = this.pos.db.get_product_by_id(selected_invoice['lines'][line]['product_id'][0]);
                        var customer = selected_invoice['partner_id'][0];
                        this.pos.get_order().add_product(product_id,{quantity: quantity});
                        var last_orderline = this.pos.get_order().get_last_orderline();
                        if(last_orderline){
                            last_orderline.set_discount(disc);
                        }
                        this.pos.get_order().set_client(this.pos.db.get_partner_by_id(customer));
                        
                    }
                }
                if(this.pos.db.origin_sale_order_pos){
					this.pos.db.origin_sale_order_pos = false
				}
                
                if (this.pos.db.origin_invoice_pos){
                    this.pos.db.origin_invoice_pos = false
                }
                this.pos.db.origin_invoice_pos = selected_invoice['id'];
                this.gui.show_screen('products');
            }
        },

        validate_count: function(){
            var invoices = this.pos.db.invoices;
            var visible = false;
            if (invoices.length > 0){
                visible = true;
            }
            return visible
        },
    });

    gui.define_screen({name: "invoices_list", widget: InvoicesWidget});

    // Para recargar la pantalla, despues de darle en Next Order, para
    // no me quede cache
    var ReceiptScreenWidgetInherit = screens.ReceiptScreenWidget.extend({
        template: 'ReceiptScreenWidget',
        renderElement: function() {
            var self = this;
            this._super();
            this.$('.next').click(function(){
                if (!self._locked) {
                    self.click_next();
                }
            });
        },
        click_next: function() {
            this.pos.get_order().finalize();
            window.location.reload();
        },
    });

    gui.define_screen({name: "receipt_screen_inherit", widget: ReceiptScreenWidgetInherit});

});
