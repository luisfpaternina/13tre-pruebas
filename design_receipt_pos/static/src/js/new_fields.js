odoo.define('design_receipt_pos.new_fields', function (require) {
var models = require('point_of_sale.models');
models.load_fields("pos.config", ['street']);
models.load_fields("res.partner", ['l10n_co_document_type', 'number_identification',  'company_type']);
var _super_order = models.Order.prototype;
models.Order = models.Order.extend({    
    export_for_printing: function() {
      var result = _super_order.export_for_printing.apply(this,arguments);
      var client = this.pos.get_client();
      var company = this.pos.company;
      console.log(this.pos.config)
      console.log(this.pos.config.street)
      result['street'] = this.pos.config.street;
      result['client_vat'] = this.get_identification(client);
      result['client_l10n_co_document_type'] =  this.get_l10n_co_document_type(
        client);
      console.log(result)
      return result;
    },

    get_identification: function(client){
      var vat = client ? client.vat : null;
      var number_identification = client ? client.number_identification : null;
      var company_type = client ? client.company_type : null;
      var result = number_identification
      if (company_type == 'company'){
        result = vat
      }
      return result;
    },

    get_l10n_co_document_type: function(client){
      var l10n_co_document_type = client ? client.l10n_co_document_type : null;
      result = ''
      if (l10n_co_document_type == 'rut'){
        result = 'NIT';
      }else if (l10n_co_document_type == 'national_citizen_id'){
        result = 'CC';
      }else if (l10n_co_document_type == 'id_card'){
        result = 'TI';
      }else if (l10n_co_document_type == 'civil_registration'){
        result = 'RC';
      }

      return result;
    },
});
});

