# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

from odoo.fields import Date
from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestRecruitmentProfileParametrization(TransactionCase):

    def setUp(self):
        super(TestRecruitmentProfileParametrization, self).setUp()
        self.hr_job = self.env['hr.job']
        self.hr_recr_experience = self.env['hr.recruitment.experience']
        self.hr_res_language = self.env['res.lang']
        self.hr_recr_language = self.env['hr.recruitment.language']
        self.hr_level = self.env['hr.recruitment.level']
        self.HrOrganizationalCompeten = self.env[
            'hr.recruitment.organizational.competencies']
        self.hrPositionsInChargeCompet = self.env[
            'hr.recruitment.positions.in.charge.competencies']
        self.HrResponsabilitiesCharge = self.env[
            'hr.recruitment.responsabilities.charge']
        self.HrSpecificCompetencies = self.env[
            'hr.recruitment.specific.competencies']
        self.HrTechnicalCompet = self.env[
            'hr.recruitment.technical.technological.competencies']
        self.HrWorkConditions = self.env[
            'hr.recruitment.work.conditions']

        # Relationship tables
        self.HrHasOrganizationalCompet = self.env[
            'hr.recruitment.has.organizational.competencies']
        self.HrHasPosiInChargeCompet = self.env[
            'hr.recruitment.has.positions.in.charge.competencies']
        self.HrHasResponsabilCharge = self.env[
            'hr.recruitment.has.responsabilities.charge']
        self.HrHasSpecificCompetencies = self.env[
            'hr.recruitment.has.specific.competencies']
        self.HrHasTechnicalCompet = self.env[
            'hr.recruitment.has.technical.technological.competencies']

        self.job = self.hr_job.create({
            'name': 'Job Name',
        })

        self.recr_experience = self.hr_recr_experience.create({
            'name': 'Experience'
        })

        self.res_language = self.hr_res_language.create({
            'name': 'Eng'
        })

        self.language = self.hr_recr_language.create({
            'langauge': self.res_language.id
        })

        self.level = self.hr_level.create({
            'name': 'Level Name'
        })

        self.OrganizationalCompet = self.HrOrganizationalCompeten.create(
            {'name': 'Organizational Competencies'})

        self.PositionsInChargeCompet = self.hrPositionsInChargeCompet.create(
            {'name': 'Positions in Charge Competencies'})

        self.ResponsabilitiesCharge = self.HrResponsabilitiesCharge.create(
            {'name': 'Responsabilities Charge'})

        self.SpecificCompetencies = self.HrSpecificCompetencies.create(
            {'name': 'Specific Competencies'})

        self.TechnicalCompet = self.HrTechnicalCompet.create(
            {'name': 'Technical Technological Competency'})

        self.WorkConditions = self.HrWorkConditions.create({
            'name': 'Work Conditions'
        })

        self.HasOrganizationalCompet = self.HrHasOrganizationalCompet.create({
            'charge_id': self.job.id,
            'organizational_competencies_id': self.OrganizationalCompet.id
        })

        self.HasPosiInChargeCompet = self.HrHasPosiInChargeCompet.create({
            'charge_id': self.job.id,
            'position_in_charge_ids': self.PositionsInChargeCompet.id
        })

        self.HasResponsabilCharge = self.HrHasResponsabilCharge.create({
            'charge_id': self.job.id,
            'responsabilities_id': self.ResponsabilitiesCharge.id
        })

        self.HasSpecificCompetencies = self.HrHasSpecificCompetencies.create({
            'charge_id': self.job.id,
            'specific_id': self.SpecificCompetencies.id
        })

        self.HasTechnicalCompet = self.HrHasTechnicalCompet.create({
            'charge_id': self.job.id,
            'technical_competencies_id': self.TechnicalCompet.id
        })
