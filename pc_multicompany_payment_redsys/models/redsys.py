# Copyright 2020-2021 Hector Cerezo <hector.cerezo@processcontrol.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import base64
import hashlib
import hmac
import json
import logging
import urllib

from odoo import _, api, exceptions, fields, http, models
from odoo.tools import config
from odoo.tools.float_utils import float_compare

from odoo.addons.payment.models.payment_acquirer import ValidationError

_logger = logging.getLogger(__name__)

try:
    from Crypto.Cipher import DES3
except ImportError:
    _logger.info("Missing dependency (pycryptodome). See README.")


class AcquirerRedsys(models.Model):
    _inherit = "payment.acquirer"

    def _prepare_merchant_parameters(self, tx_values):
        # Check multi-website

        base_url = self._get_website_url()
        callback_url = self._get_website_callback_url()
        if self.redsys_percent_partial > 0:
            amount = tx_values["amount"]
            tx_values["amount"] = amount - (amount * self.redsys_percent_partial / 100)
        values = {
            "Ds_Sermepa_Url": self.redsys_get_form_action_url(),
            "Ds_Merchant_Amount": str(int(round(tx_values["amount"] * 100))),
            "Ds_Merchant_Currency": self.redsys_currency or "978",
            "Ds_Merchant_Order": (
                    tx_values["reference"] and tx_values["reference"][-12:] or False
            ),
            "Ds_Merchant_MerchantCode": (
                    self.redsys_merchant_code and self.redsys_merchant_code[:9]
            ),
            "Ds_Merchant_Terminal": self.redsys_terminal or "1",
            "Ds_Merchant_TransactionType": (self.redsys_transaction_type or "0"),
            "Ds_Merchant_Titular": tx_values.get(
                "billing_partner", self.env.user.partner_id
            ).display_name[:60],
            "Ds_Merchant_MerchantName": (
                    self.redsys_merchant_name and self.redsys_merchant_name[:25]
            ),
            "Ds_Merchant_MerchantUrl": (
                                               "%s/payment/redsys/return" % (callback_url or base_url)
                                       )[:250],
            "Ds_Merchant_MerchantData": self.redsys_merchant_data or "",
            "Ds_Merchant_ProductDescription": (
                    self._product_description(tx_values["reference"])
                    or self.redsys_merchant_description
                    and self.redsys_merchant_description[:125]
            ),
            "Ds_Merchant_ConsumerLanguage": (self.redsys_merchant_lang or "001"),
            "Ds_Merchant_UrlOk": "%s/payment/redsys/result/redsys_result_ok" % base_url,
            "Ds_Merchant_UrlKo": "%s/payment/redsys/result/redsys_result_ko" % base_url,
            "Ds_Merchant_Paymethods": self.redsys_pay_method or "T",
        }
        return self._url_encode64(json.dumps(values))


class TxRedsys(models.Model):
    _inherit = "payment.transaction"

    def merchant_params_json2dict(self, data):
        parameters = data.get("Ds_MerchantParameters", "")
        return json.loads(base64.b64decode(parameters).decode())

    # --------------------------------------------------
    # FORM RELATED METHODS
    # --------------------------------------------------

    @api.model
    def _redsys_form_get_tx_from_data(self, data):
        """ Given a data dict coming from redsys, verify it and
        find the related transaction record. """
        parameters = data.get("Ds_MerchantParameters", "")
        parameters_dic = json.loads(base64.b64decode(parameters).decode())
        reference = urllib.parse.unquote(parameters_dic.get("Ds_Order", ""))

        reference = 'S/' + reference
        
        _logger.error("Referencis")
        _logger.error(reference)

        pay_id = parameters_dic.get("Ds_AuthorisationCode")
        shasign = data.get("Ds_Signature", "").replace("_", "/").replace("-", "+")
        test_env = config["test_enable"]
        if not reference or not pay_id or not shasign:
            error_msg = (
                    "Redsys: received data with missing reference"
                    " (%s) or pay_id (%s) or shashign (%s)" % (reference, pay_id, shasign)
            )
            if not test_env:
                _logger.error(error_msg)
                raise ValidationError(error_msg)
            # For tests
            http.OpenERPSession.tx_error = True
        tx = self.search([("reference", "=", reference)])
        _logger.error("Objeto TX")
        _logger.error(tx.id)
        
        _logger.error("Tamaño Objeto TX")
        _logger.error(len(tx))
        
        if not tx or len(tx) > 1:
            error_msg = "Redsys: received data for reference %s" % (reference)
            if not tx:
                error_msg += "; no order found"
            else:
                error_msg += "; multiple order found"
            if not test_env:
                _logger.error(error_msg)
                raise ValidationError(error_msg)
            # For tests
            http.OpenERPSession.tx_error = True
        if tx and not test_env:
            # verify shasign
            shasign_check = tx.acquirer_id.sign_parameters(
                tx.acquirer_id.redsys_secret_key, parameters
            )
            if shasign_check != shasign:
                error_msg = (
                        "Redsys: invalid shasign, received %s, computed %s, "
                        "for data %s" % (shasign, shasign_check, data)
                )
                _logger.error(error_msg)
                raise ValidationError(error_msg)
        return tx
