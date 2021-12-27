# -*- coding: utf-8 -*-
from datetime import datetime, timedelta, date
from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestHrRecruitmentScheduling(TransactionCase):

    def setUp(self):
        super(TestHrRecruitmentScheduling, self).setUp()
        self.hr_applicant = self.env['hr.applicant']
        self.calendar_event = self.env['calendar.event']
        self.res_partner = self.env['res.partner']

        self.stage_job1 = self.env['hr.recruitment.stage']\
            .browse(self.ref('hr_recruitment.stage_job1'))

        self.stage_job2 = self.env['hr.recruitment.stage']\
            .browse(self.ref('hr_recruitment.stage_job2'))

        self.partner_test = self.res_partner.create({
            'name': 'Applicant one test',
            'email': 'applicant@gmail.com'
        })

        self.stage_job1.write({
            'assigned_to': self.partner_test.id
        })

        self.applicant = self.hr_applicant.create({
            'name': 'applicant test',
            'email_from': 'email@test.com',
            'stage_id': self.stage_job1.id
        })

        self.event = self.calendar_event.create({
            'name': 'calendar event test',
            'start': '2018-11-12 21:00:00',
            'stop': '2018-11-13 00:00:00',
        })

        self.event_applicant = self.calendar_event.create({
            'name': 'calendar event test applicant',
            'start': '2018-11-12 21:00:00',
            'stop': '2018-11-13 00:00:00',
            'applicant_id': self.applicant.id
        })
