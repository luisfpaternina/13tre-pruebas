odoo.define('account_difference_report_niif_colgap.accounts_report', function (require) {
    "use strict";

    var core = require('web.core');
    var actionAccount = require('account_reports.account_report');
    var StandaloneFieldManagerMixin = require(
        'web.StandaloneFieldManagerMixin');
    var RelationalFields = require('web.relational_fields');
    var Widget = require('web.Widget');
    var QWeb = core.qweb;
    var _t = core._t;

    var O2MFilters = Widget.extend(StandaloneFieldManagerMixin, {
        init: function (parent, fields) {
            this._super.apply(this, arguments);
            StandaloneFieldManagerMixin.init.call(this);
            this.fields = fields;
            this.widgets = {};
        },
        willStart: function () {
            var self = this;
            var defs = [this._super.apply(this, arguments)];
            _.each(this.fields, function (field, fieldName) {
                defs.push(self._makeO2MWidget(field, fieldName));
            });
            return Promise.all(defs);
        },
        start: function () {
            var self = this;
            var $content = $(QWeb.render(
                "m2mWidgetTable", { fields: this.fields }));
            self.$el.append($content);
            _.each(this.fields, function (field, fieldName) {
                self.widgets[fieldName].appendTo(
                    $content.find('#' + fieldName + '_field'));
            });
            return this._super.apply(this, arguments);
        },
        _confirmChange: function () {
            var self = this;
            var result = StandaloneFieldManagerMixin._confirmChange.apply(
                this, arguments);
            var data = {};
            _.each(this.fields, function (filter, fieldName) {
                data[fieldName] = self.widgets[fieldName].value.res_id;
            });
            this.trigger_up('value_changed', data);
            return result;
        },
        _makeO2MWidget: function (fieldInfo, fieldName) {
            var self = this;
            var options = {};
            options[fieldName] = {
                options: {
                    no_create_edit: true,
                    no_create: true,
                }
            };
            return this.model.makeRecord(fieldInfo.modelName, [{
                fields: [{
                    name: 'id',
                    type: 'integer',
                }, {
                    name: 'display_name',
                    type: 'char',
                }],
                name: fieldName,
                relation: fieldInfo.modelName,
                type: 'many2one',
                // value: fieldInfo.value,
            }], options).then(function (recordID) {
                self.widgets[fieldName] = new RelationalFields.FieldMany2One(
                    self,
                    fieldName,
                    self.model.get(recordID),
                    { mode: 'edit', }
                );
                self._registerWidget(recordID, fieldName,
                    self.widgets[fieldName]);
            });
        },
    });

    actionAccount.include({
        custom_events: _.extend({}, actionAccount.prototype.custom_events, {
            'value_changed': function (ev) {
                var self = this;
                self.report_options.account_accounts = ev.data.account_accounts;
                self.report_options.account_accounts_to = ev.data.account_accounts_to;
                return self.reload().then(function () {
                    self.$searchview_buttons.find(
                        '.account_accounts_filter').click();
                });
            }
        }),
        init: function (parent, action) {
            return this._super.apply(this, arguments);
        },
        render_searchview_buttons: function () {
            this._super.apply(this, arguments);
            if (this.report_options.range_account) {
                if (!this.O2MFilters) {
                    var fields = {};
                    if (this.report_options.account_accounts) {
                        fields['account_accounts'] = {
                            label: _t('Accounts From'),
                            modelName: 'account.account',
                            value: this.report_options.account_accounts
                        };
                    }
                    if (this.report_options.account_accounts_to) {
                        fields['account_accounts_to'] = {
                            label: _t('Accounts To'),
                            modelName: 'account.account',
                            value: this.report_options.account_accounts_to
                        };
                    }
                    if (!_.isEmpty(fields)) {
                        this.O2MFilters = new O2MFilters(this, fields);
                        this.O2MFilters.appendTo(
                            this.$searchview_buttons.find(
                                '.js_account_accounts_m2m'));
                    }
                } else {
                    this.$searchview_buttons.find(
                        '.js_account_accounts_m2m').append(
                            this.O2MFilters.$el);
                }
            }

        },

    });
});