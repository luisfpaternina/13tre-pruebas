# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

#
# Order Point Method:
#    - Order if the virtual stock of today is below the min of the defined order point
#

from odoo import models
import logging
import requests
import json
from pprint import pprint
from datetime import datetime
import pytz

_logger = logging.getLogger(__name__)


class SynchronizationCallsWzd(models.TransientModel):
    _name = 'synchronization.calls.wzd'

    def get_all_calls(self):
        try:
            call_api = self.env['ir.config_parameter'].sudo(
            ).get_param('call.endpoint')
            api_token = self.env['ir.config_parameter'].sudo(
            ).get_param('call.register.token')
            last_cdr_id = self.env['ir.config_parameter'].sudo(
            ).get_param('call.last_cdr_id')

            aux_dict = {"limit_count": 400}
            if last_cdr_id and last_cdr_id != '0':
                aux_dict.update({"last_id_returned": 999999999})

            response = requests.post(call_api, verify=True, data=json.dumps(aux_dict),
                                     headers={"Content-type": "application/json", 
                                     'Authorization': api_token})
            response.raise_for_status()
            result = response.json()
            # logging.info("Ringover URL sent: ")
            # logging.info(call_api)
            # logging.info("Ringover Token sent: ")
            # logging.info(api_token)
            # logging.info("Ringover Data sent: ")
            # logging.info(aux_dict)
            # logging.info("Ringover Response: ")
            # logging.info(result)

            if 'call_list' in result:
                call_list = result['call_list']
            self.register_calls(call_list)
        except Exception as e:
            error = str(e)
            pprint(error)

    def add_user_id(self, user, user_id):
        user.sudo().write({'ring_over_user_id': user_id})

    def register_calls(self, call_list):
        call_register = self.env['call.register'].sudo()
        self.env['call.register'].sudo().search([]).unlink()

        user_cls = self.env['res.users'].sudo()
        for call in call_list:
            logging.info('Entro al ciclo!')
            user = False
            if 'user' in call and call['user']:
                user = user_cls.sudo().search(
                    [('ring_over_user_id', '=', call['user']['user_id'])], limit=1)
            calls = dict()
            calls['call_id'] = call['call_id']
            calls['cdr_id'] = call['cdr_id']
            calls['contact_number'] = call['contact_number']
            calls['start_date'] = self.process_time(call['start_time'])
            calls['answered_time'] = self.process_time(call['answered_time'])
            calls['call_end'] = self.process_time(call['end_time'])
            calls['incall_duration'] = 0 if call['incall_duration'] is None else call['incall_duration']
            calls['total_duration'] = 0 if call['total_duration'] is None else call['total_duration']
            calls['user_id'] = user.id if user else False
            calls['partner_id'] = user.partner_id.id if user else False
            calls['direction'] = call['direction']
            calls['last_state'] = call['last_state']
            calls['type'] = call['type']
            calls['from_number'] = call['from_number']
            calls['to_number'] = call['to_number']
            last_call_created = call_register.sudo().create(calls)
            logging.info('Call created!')
        
        self.env['ir.config_parameter'].sudo().set_param(
            'call.last_cdr_id', last_call_created.cdr_id)
        return True

    def process_time(self, date_time):
        if date_time is None:
            date_time_general_2 = False
        else:
            date_time_general = date_time[0:10] + ' ' + date_time[11:19]
            date_time_general_1 = datetime.strptime(
                date_time_general, "%Y-%m-%d %H:%M:%S")
            date_time_general_2 = self.convert_utc(date_time_general_1)

        return date_time_general_2

    def convert_utc(self, date_time):
        if date_time is None:
            utc_dt = False
        else:
            local = pytz.timezone(self.env.user.tz)
            local_dt_1 = local.localize(date_time, is_dst=None)
            local_dt_2 = str(local_dt_1.astimezone(pytz.utc))[0:19]
            utc_dt = datetime.strptime(local_dt_2, "%Y-%m-%d %H:%M:%S")
        return utc_dt
