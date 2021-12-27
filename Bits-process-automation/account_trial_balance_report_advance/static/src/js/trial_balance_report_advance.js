odoo.define('account_trial_balance_report_advance.account_trial_report', function (require) {
    "use strict";

    var core = require('web.core');
    var actionAccount = require('account_reports.account_report');
    var _t = core._t;

    actionAccount.include({
        init: function (parent, action) {
            return this._super.apply(this, arguments);
        },
        render_searchview_buttons: function () {
            this._super.apply(this, arguments);
            // types niif and fiscal
            var self = this;
            

            _.each(this.$searchview_buttons.find(
                '.js_account_account_levels_filter'), function(k) {
                    $(k)
                    .toggleClass(
                        'selected',
                        (_.filter(
                            self.report_options[$(k).data('filter')],
                            function(el){
                                return ''+el.code == ''+$(k)
                                    .data('id') && el.selected === true;
                            })).length > 0);
            });
            _.each(this.$searchview_buttons.find(
                '.account_accounting_types_filter'), function(k) {
                    $(k)
                    .toggleClass(
                        'selected',
                        (_.filter(
                            self.report_options[$(k).data('filter')],
                            function(el){
                                return ''+el.code == ''+$(k)
                                    .data('id') && el.selected === true;
                            })).length > 0);
            });
            this.$searchview_buttons.find('.js_account_account_levels_filter')
                .click(function(evt){
                    var option_value = $(this).data('filter');
                    var option_id = $(this).data('id');
                    _.filter(self.report_options[option_value], function(el){
                        if (''+el.code == ''+option_id){
                            if (el.selected === undefined || el.selected === null){el.selected = false;}
                            el.selected = !el.selected;
                        } else if (option_value === 'ir_filters') {
                            el.selected = false;
                        }
                        return el;
                    });
                    self.reload();
                });
            this.$searchview_buttons.find('.account_accounting_types_filter')
                .click(function(evt){
                    var option_value = $(this).data('filter');
                    var option_id = $(this).data('id');
                    _.filter(self.report_options[option_value], function(el){
                        if (''+el.code == ''+option_id){
                            if (el.selected === undefined || el.selected === null){el.selected = false;}
                            el.selected = !el.selected;
                        } else if (option_value === 'ir_filters') {
                            el.selected = false;
                        }
                        return el;
                    });
                    self.reload();
                });
        },

    });
});
