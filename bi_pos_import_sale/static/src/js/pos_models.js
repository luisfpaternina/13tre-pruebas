odoo.define('bi_pos_import_sale.import_sale', function(require) {
	"use strict";

	var models = require('point_of_sale.models');
	var screens = require('point_of_sale.screens');
    var PosDb = require("point_of_sale.DB");
	var core = require('web.core');
	var gui = require('point_of_sale.gui');
	var popups = require('point_of_sale.popups');
	var QWeb = core.qweb;
	var utils = require('web.utils');
	var round_pr = utils.round_precision;
	var rpc = require('web.rpc');
	var Dialog = require('web.Dialog');
	var _t = core._t;

	// Load Models
	models.load_models({
		model:  'sale.order',
		fields: ['name','partner_id','user_id','amount_untaxed','state',
				 'order_line','amount_tax','amount_total','company_id','date_order',],
		domain: function(self)
				{
					var days = self.config.load_orders_days
					var is_draft_sent=self.config.load_draft_sent
					if(days > 0)
					{
						var today= new Date();
						today.setDate(today.getDate() - days);
						var dd = today.getDate();
						var mm = today.getMonth()+1; //January is 0!

						var yyyy = today.getFullYear();
						if(dd<10){
							dd='0'+dd;
						}
						if(mm<10){
							mm='0'+mm;
						}
						var today = yyyy+'-'+mm+'-'+dd+" "+ "00" + ":" + "00" + ":" + "00";

						if(is_draft_sent){
							return [
								['date_order', '>=',today],
								['state','in',['draft','sent']]
							];
						}
						else{
							return [
								['date_order', '>=',today]
							];
						}
					}
					else{
						var is_draft_sent=self.config.load_draft_sent
						if(is_draft_sent){
							return [
								['state','in',['draft','sent']]
							];
						}
					}
				},
		loaded: function(self,order){
			var i=0;
			self.all_orders_list = order;
			self.get_orders_by_id = {};
			order.forEach(function(orders) {
				self.get_orders_by_id[orders.id] = orders;
			});
		},
	});

	models.load_models({
		model: 'sale.order.line',
		fields: ['order_id', 'product_id', 'discount', 'product_uom_qty', 'price_unit','price_subtotal'],
		domain: function(self) {
			var order_lines = []
			var orders = self.all_orders_list;
			for (var i = 0; i < orders.length; i++) {
				order_lines = order_lines.concat(orders[i]['order_line']);
			}
			return [
				['id', 'in', order_lines]
			];
		},
		loaded: function(self, sale_order_line) {
			self.all_orders_line_list = sale_order_line;
			self.get_lines_by_id = {};
			sale_order_line.forEach(function(line) {
				self.get_lines_by_id[line.id] = line;
			});

			self.sale_order_line = sale_order_line;
		},
	});

	var SaleOrderButtonWidget = screens.ActionButtonWidget.extend({
		template: 'SaleOrderButtonWidget',

		button_click: function() {
			var self = this;
			this.gui.show_screen('see_all_orders_screen_widget', {});
		},
	});

	// The button to list the orders (sale.order) is disabled,
	// change the 'return' to 'true' in the 'condition'
	// in order to display the button
	screens.define_action_button({
		'name': 'See All Orders Button Widget',
		'widget': SaleOrderButtonWidget,
		'condition': function() {
			return false;
		},
	});




	// SeeAllOrdersScreenWidget start

	var SeeAllOrdersScreenWidget = screens.ScreenWidget.extend({
		template: 'SeeAllOrdersScreenWidget',
		init: function(parent, options) {
			this._super(parent, options);
			//this.options = {};
		},

		render_list_orders: function(orders, search_input){
			var self = this;
			if(search_input != undefined && search_input != '') {
				var selected_search_orders = [];
				var search_text = search_input.toLowerCase()
				for (var i = 0; i < orders.length; i++) {
					if (orders[i].partner_id == '') {
						orders[i].partner_id = [0, '-'];
					}
					if (((orders[i].name.toLowerCase()).indexOf(search_text) != -1) || ((orders[i].name.toLowerCase()).indexOf(search_text) != -1) || ((orders[i].partner_id[1].toLowerCase()).indexOf(search_text) != -1)) {
						selected_search_orders = selected_search_orders.concat(orders[i]);
					}
				}
				orders = selected_search_orders;
			}

			var content = this.$el[0].querySelector('.client-list-contents');
			content.innerHTML = "";
			var orders = orders;
			for(var i = 0, len = Math.min(orders.length,1000); i < len; i++){
				var order    = orders[i];
				var ordersline_html = QWeb.render('OrdersLine',{widget: this, order:orders[i]});
				var ordersline = document.createElement('tbody');
				ordersline.innerHTML = ordersline_html;
				ordersline = ordersline.childNodes[1];
				content.appendChild(ordersline);
			}
		},

		get_last_day_orders: function () {
			var days = this.pos.config.load_orders_days
			var today= new Date();
			today.setDate(today.getDate() - days);
			var dd = today.getDate();
			var mm = today.getMonth()+1; //January is 0!

			var yyyy = today.getFullYear();
			if(dd<10){
				dd='0'+dd;
			}
			if(mm<10){
				mm='0'+mm;
			}
			var today = yyyy+'-'+mm+'-'+dd+" "+ "00" + ":" + "00" + ":" + "00";
			return today
		},

		show: function(options) {
			var self = this;
			this._super(options);
			this.old_sale_order = null;
			this.details_visible = false;
			var flag = 0;
			var orders = self.pos.all_orders_list;
			var orders_lines = self.pos.all_orders_line_list;
			var selectedOrder;
			var thisOrder = this.pos.get_order();
			this.render_list_orders(orders, undefined);
			var l_date = self.get_last_day_orders();
			var config_id = this.pos.config.id
			$('.refresh-order').on('click',function () {
				rpc.query({
					model: 'pos.order',
					method: 'search_all_sale_order',
					args: [1,config_id,l_date],
				}).then(function(output) {
					self.pos.all_orders_list = output
					orders = output;
					var so = output;
					rpc.query({
						model: 'pos.order',
						method: 'sale_order_line',
						args: [1],
					}).then(function(output1) {
						self.pos.all_orders_line_list = output1
						orders_lines = output1
						// self.show();
						self.render_list_orders(so,undefined);
					});
				});
			});


			var selectedorderlines = [];
			var client = false
			var count = 0;

			this.$('.back').click(function(){
				self.gui.show_screen('products');
			});

			this.$('.client-list-contents').delegate('.sale-order','click',function(event){
				var orderPos = self.pos.get_order()
				var linesOrderPos = orderPos.get_orderlines()
				if (linesOrderPos.length > 0){
					for (var i=0; i<linesOrderPos.length; i++){
						orderPos.remove_orderline(linesOrderPos[i])
					}
				}
				var order_id = parseInt(this.id);
				selectedOrder = null;
				for(var i = 0, len = Math.min(orders.length,1000); i < len; i++) {
					if (orders[i] && orders[i].id == order_id) {
						selectedOrder = orders[i];
					}
				}
				var linesSelectOrder = [];
				
				for (var order in selectedOrder.order_line){
					linesSelectOrder.push(selectedOrder.order_line[order])
				}
				if(self.pos.db.origin_invoice_pos){
					self.pos.db.origin_invoice_pos = false
				}

				for (var x=0; x<orders_lines.length; x++){
					for (var y=0; y<linesSelectOrder.length; y++){
						if  (orders_lines[x].id == linesSelectOrder[y]){
							var product_id = orders_lines[x]['product_id'][0];
							var quantity = orders_lines[x]['product_uom_qty'];
							var product = self.pos.db.get_product_by_id(product_id);
							thisOrder.add_product(product,{ quantity: quantity});
						}
					}
				}
				
				var customer = selectedOrder['partner_id'][0];
				self.pos.get_order().set_client(self.pos.db.get_partner_by_id(customer));
				if(self.pos.db.origin_sale_order_pos){
					self.pos.db.origin_sale_order_pos = false
				}
				self.pos.db.origin_sale_order_pos = selectedOrder.id
				self.gui.show_screen('products');
			});


			this.$('.client-list-contents').delegate('.orders-line-name', 'click', function(event) {
				var order_id = parseInt(this.id);
				selectedOrder = null;
				for(var i = 0, len = Math.min(orders.length,1000); i < len; i++) {
					if (orders[i] && orders[i].id == order_id) {
						selectedOrder = orders[i];
					}
				}
				var orderlines = [];

				selectedOrder.order_line.forEach(function(line_id) {
					for(var y=0; y<orders_lines.length; y++){
						if(orders_lines[y]['id'] == line_id){
						   orderlines.push(orders_lines[y]);
						}
					}

				});

				self.gui.show_popup('see_order_details_popup_widget', {'orderline': orderlines, 'order': [selectedOrder] });

			});

			this.$('.client-list-contents').delegate('.orders-line-date', 'click', function(event) {
				var order_id = parseInt(this.id);
				selectedOrder = null;
				for(var i = 0, len = Math.min(orders.length,1000); i < len; i++) {
					if (orders[i] && orders[i].id == order_id) {
						selectedOrder = orders[i];
					}
				}
				var orderlines = [];
				selectedOrder.order_line.forEach(function(line_id) {

					for(var y=0; y<orders_lines.length; y++){
						if(orders_lines[y]['id'] == line_id){
						   orderlines.push(orders_lines[y]);
						}
					}

				});

				self.gui.show_popup('see_order_details_popup_widget', {'orderline': orderlines, 'order': [selectedOrder] });

			});

			this.$('.client-list-contents').delegate('.orders-line-partner', 'click', function(event) {
				var order_id = parseInt(this.id);
				selectedOrder = null;
				for(var i = 0, len = Math.min(orders.length,1000); i < len; i++) {
					if (orders[i] && orders[i].id == order_id) {
						selectedOrder = orders[i];
					}
				}
				var orderlines = [];

				selectedOrder.order_line.forEach(function(line_id) {

					for(var y=0; y<orders_lines.length; y++){
						if(orders_lines[y]['id'] == line_id){
						   orderlines.push(orders_lines[y]);
						}
					}

				});

				self.gui.show_popup('see_order_details_popup_widget', {'orderline': orderlines, 'order': [selectedOrder] });

			});

			this.$('.client-list-contents').delegate('.orders-line-saleperson', 'click', function(event) {
				var order_id = parseInt(this.id);
				selectedOrder = null;
				for(var i = 0, len = Math.min(orders.length,1000); i < len; i++) {
					if (orders[i] && orders[i].id == order_id) {
						selectedOrder = orders[i];
					}
				}
				var orderlines = [];

				selectedOrder.order_line.forEach(function(line_id) {

					for(var y=0; y<orders_lines.length; y++){
						if(orders_lines[y]['id'] == line_id){
						   orderlines.push(orders_lines[y]);
						}
					}

				});

				self.gui.show_popup('see_order_details_popup_widget', {'orderline': orderlines, 'order': [selectedOrder] });

			});

			this.$('.client-list-contents').delegate('.orders-line-subtotal', 'click', function(event) {
				var order_id = parseInt(this.id);
				selectedOrder = null;
				for(var i = 0, len = Math.min(orders.length,1000); i < len; i++) {
					if (orders[i] && orders[i].id == order_id) {
						selectedOrder = orders[i];
					}
				}
				var orderlines = [];

				selectedOrder.order_line.forEach(function(line_id) {

					for(var y=0; y<orders_lines.length; y++){
						if(orders_lines[y]['id'] == line_id){
						   orderlines.push(orders_lines[y]);
						}
					}

				});

				self.gui.show_popup('see_order_details_popup_widget', {'orderline': orderlines, 'order': [selectedOrder] });

			});

			this.$('.client-list-contents').delegate('.orders-line-tax', 'click', function(event) {
				var order_id = parseInt(this.id);
				selectedOrder = null;
				for(var i = 0, len = Math.min(orders.length,1000); i < len; i++) {
					if (orders[i] && orders[i].id == order_id) {
						selectedOrder = orders[i];
					}
				}
				var orderlines = [];

				selectedOrder.order_line.forEach(function(line_id) {

					for(var y=0; y<orders_lines.length; y++){
						if(orders_lines[y]['id'] == line_id){
						   orderlines.push(orders_lines[y]);
						}
					}

				});

				self.gui.show_popup('see_order_details_popup_widget', {'orderline': orderlines, 'order': [selectedOrder] });

			});

			this.$('.client-list-contents').delegate('.orders-line-tot', 'click', function(event) {
				var order_id = parseInt(this.id);
				selectedOrder = null;
				for(var i = 0, len = Math.min(orders.length,1000); i < len; i++) {
					if (orders[i] && orders[i].id == order_id) {
						selectedOrder = orders[i];
					}
				}
				var orderlines = [];

				selectedOrder.order_line.forEach(function(line_id) {

					for(var y=0; y<orders_lines.length; y++){
						if(orders_lines[y]['id'] == line_id){
						   orderlines.push(orders_lines[y]);
						}
					}

				});

				self.gui.show_popup('see_order_details_popup_widget', {'orderline': orderlines, 'order': [selectedOrder] });

			});

			//this code is for Search Orders
			this.$('.search-order input').keyup(function() {
				self.render_list_orders(orders, this.value);
			});
		},
	});
	gui.define_screen({
		name: 'see_all_orders_screen_widget',
		widget: SeeAllOrdersScreenWidget
	});

	var _super_order = models.Order.prototype;
	models.Order = models.Order.extend({
		initialize: function(attr, options) {
			this.imported_sales = this.imported_sales || [];
			_super_order.initialize.call(this,attr,options);
		},

		set_imported_sales: function(so){
			let sale = so.toString();
			if(!this.imported_sales.includes(sale))
				this.imported_sales += sale+',';
		},

		get_imported_sales: function(){
			return this.imported_sales;
		},
		export_as_JSON: function() {
			var json = _super_order.export_as_JSON.apply(this,arguments);
			json.imported_sales = this.imported_sales || [];
			return json;
		},

		init_from_JSON: function(json){
			_super_order.init_from_JSON.apply(this,arguments);
			this.imported_sales = json.imported_sales || [];
		},
	});

	var SeeOrderDetailsPopupWidget = popups.extend({
		template: 'SeeOrderDetailsPopupWidget',

		init: function(parent, args) {
			this._super(parent, args);
			this.options = {};
		},

		show: function(options) {
			var self = this;
			options = options || {};
			this._super(options);


			this.order = options.order || [];
			this.orderline = options.orderline || [];

		},

		events: {
			'click .button.cancel': 'click_cancel',
		},

		renderElement: function() {
			var self = this;
			this._super();
		},
	});

	gui.define_popup({
		name: 'see_order_details_popup_widget',
		widget: SeeOrderDetailsPopupWidget
	});

	var ErrorSaleOrder = popups.extend({
		template: 'ErrorSaleOrder',

		init: function(parent, args) {
			this._super(parent, args);
			this.options = {};
		},

		show: function(options) {
			options = options || {};
			this._super();
			this.renderElement();

			if (this.pos.barcode_reader) {
				this.pos.barcode_reader.save_callbacks();
				this.pos.barcode_reader.reset_action_callbacks();
			}
		},

		events: {
			'click .button.cancel': 'click_cancel',
		},
	});

	return {
		SaleOrderButtonWidget: SaleOrderButtonWidget,
		SeeAllOrdersScreenWidget: SeeAllOrdersScreenWidget,
		SeeOrderDetailsPopupWidget: SeeOrderDetailsPopupWidget,
	};
});
