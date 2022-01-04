# -*- coding: utf-8 -*-

import calendar
import datetime
from datetime import datetime

from dateutil.relativedelta import relativedelta

from odoo import models, api
from odoo.http import request


class CallRegisterDashBoard(models.Model):
    _name = 'call_register.dashboard'

    @api.model
    def get_calls_total_this_year(self):
        user = self.env.user
        total = 0
        if user.has_group('call_register.group_call_register_manager'):
            query_calls_total = (''' select count(id) as calls from  call_register where
                                        Extract(YEAR FROM start_date) = Extract(YEAR FROM DATE(NOW()))                                                                     
                                            ''')
        else:
            query_calls_total = ('''
                                    select count(id) as calls from  call_register where user_id=%d and
                                        Extract(YEAR FROM start_date) = Extract(YEAR FROM DATE(NOW()))                                                                
                                ''') % (user.id)
        self._cr.execute(query_calls_total)
        record_query_calls_total = self._cr.fetchall()
        if record_query_calls_total[0][0]:
            total = record_query_calls_total[0][0]
        else:
            total = 0
        return total
    
    @api.model
    def get_calls_by_numbers(self):
        calls = self.env['call.register'].search([], order='from_number')
        totals = []
        period = []
        index = {}

        for call in calls:
            if call.from_number not in index:
                index.update({call.from_number: len(totals)})
                period.append(call.from_number)
                totals.append(1)
            else:
                totals[index[call.from_number]] += 1

        return {
            'period': period,
            'total': totals,
        }

    @api.model
    def get_calls_by_month(self):
        user = self.env.user
        period_en = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September',
                     'October', 'November', 'December']
        period_es = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre',
                     'Octubre', 'Noviembre', 'Diciembre']
        period = period_es
        lang = self.env.user.lang
        if not lang:
            lang = 'en_US'
            period = period_en
        total = list()
        for i in range(1, 13):
            if user.has_group('call_register.group_call_register_manager'):
                query_calls_total = ('''
                                            select count(id) as calls from  call_register where
                                                Extract(YEAR FROM start_date) = Extract(YEAR FROM DATE(NOW())) 
                                                and Extract(MONTH FROM start_date) = %s                          
                                                ''') % (str(i))
            else:
                query_calls_total = ('''
                                        select count(id) as calls from  call_register where user_id=%d and
                                            Extract(YEAR FROM start_date) = Extract(YEAR FROM DATE(NOW())) 
                                            and Extract(MONTH FROM start_date) = %s                          
                                    ''') % (user.id, str(i))
            self._cr.execute(query_calls_total)
            record_query_calls_total = self._cr.fetchall()
            if record_query_calls_total[0][0]:
                total.append(record_query_calls_total[0][0])
            else:
                total.append(0)

        result = {
            'period': period,
            'total': total

        }
        return result

    @api.model
    def get_duration_calls(self):
        user = self.env.user
        period_en = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September',
                     'October', 'November', 'December']
        period_es = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre',
                     'Octubre', 'Noviembre', 'Diciembre']
        period = period_es
        lang = self.env.user.lang
        if not lang:
            lang = 'en_US'
            period = period_en
        time_answered = list()
        time_not_answered = list()
        time_total = list()
        for i in range(1, 13):
            if user.has_group('call_register.group_call_register_manager'):
                query_duration_answered = ('''
                                    select sum(incall_duration) as calls from  call_register where
                                        Extract(YEAR FROM start_date) = Extract(YEAR FROM DATE(NOW())) 
                                        and Extract(MONTH FROM start_date) = %s                          
                                ''') % (str(i))
            else:
                query_duration_answered = ('''
                                                    select sum(incall_duration) as calls from  call_register where user_id=%d and
                                                        Extract(YEAR FROM start_date) = Extract(YEAR FROM DATE(NOW())) 
                                                        and Extract(MONTH FROM start_date) = %s                          
                                                ''') % (user.id, str(i))
            self._cr.execute(query_duration_answered)
            record_query_duration_answered = self._cr.fetchall()
            if record_query_duration_answered[0][0]:
                hours_a = record_query_duration_answered[0][0] / 3600
                time_answered.append(round(hours_a, 4))
            else:
                time_answered.append(0)
            if user.has_group('call_register.group_call_register_manager'):
                query_duration_not_answered = ('''
                        select sum(total_duration - incall_duration) as calls from  call_register where
                            Extract(YEAR FROM start_date) = Extract(YEAR FROM DATE(NOW())) 
                            and Extract(MONTH FROM start_date) = %s                          
                                            ''') % (str(i))
            else:
                query_duration_not_answered = ('''
                        select sum(total_duration - incall_duration) as calls from  call_register where user_id=%d and
                            Extract(YEAR FROM start_date) = Extract(YEAR FROM DATE(NOW())) 
                            and Extract(MONTH FROM start_date) = %s                          
                    ''') % (user.id, str(i))
            self._cr.execute(query_duration_not_answered)
            record_query_duration_not_answered = self._cr.fetchall()
            if record_query_duration_not_answered[0][0]:
                hours_n = record_query_duration_not_answered[0][0] / 3600
                time_not_answered.append(round(hours_n, 4))
            else:
                time_not_answered.append(0)
            if user.has_group('call_register.group_call_register_manager'):
                query_total_duration = ('''
                                    select sum(total_duration) as calls from  call_register where
                                        Extract(YEAR FROM start_date) = Extract(YEAR FROM DATE(NOW())) 
                                        and Extract(MONTH FROM start_date) = %s                          
                                                        ''') % (str(i))
            else:
                query_total_duration = ('''
                                        select sum(total_duration) as calls from  call_register where user_id=%d and
                                            Extract(YEAR FROM start_date) = Extract(YEAR FROM DATE(NOW())) 
                                            and Extract(MONTH FROM start_date) = %s                          
                                                            ''') % (user.id, str(i))
            self._cr.execute(query_total_duration)
            record_query_total_duration = self._cr.fetchall()
            if record_query_total_duration[0][0]:
                hours_t = record_query_total_duration[0][0] / 3600
                time_total.append(round(hours_t, 4))
            else:
                time_total.append(0)

        result = {
            'period': period,
            'time_answered': time_answered,
            'time_not_answered': time_not_answered,
            'time_total': time_total
        }
        return result
