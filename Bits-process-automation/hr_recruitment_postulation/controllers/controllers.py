import base64
import sys
from odoo.addons.website_form.controllers.main import WebsiteForm
import json
from psycopg2 import IntegrityError
from odoo import http, SUPERUSER_ID
from odoo.http import request
from odoo.tools.translate import _
from werkzeug.exceptions import BadRequest

from odoo.exceptions import ValidationError


class HrRecruitmentPostulation(WebsiteForm):

    record = 0
    bank_resume_model = 'hr.recruitment.bank.resumes'

    def insert_attachment_bank_resumes(self, applicant, files):
        orphan_attachment_ids = []
        for file in files:
            attachment_value = dict(
                name=file.filename,
                datas=base64.encodestring(file.read()),
                res_model=self.bank_resume_model,
                res_id=self.record.id
            )

            attachment_id = request.env['ir.attachment'].sudo().create(
                attachment_value)
            attachment_applicant = request.env['ir.attachment'].sudo()\
                .search([
                    ('name', '=', file.filename),
                    ('res_model', '=', 'hr.applicant'),
                    ('res_id', '=', applicant.id)
                ], limit=1)

            attachment_id.write({
                'store_fname': attachment_applicant.store_fname,
                'file_size': attachment_applicant.file_size
            })

            orphan_attachment_ids.append(attachment_id.id)

            values = dict(
                body=_('<p>Attached files : </p>'),
                model=self.bank_resume_model,
                message_type='comment',
                no_auto_thread=False,
                res_id=self.record.id,
                attachment_ids=[(6, 0, orphan_attachment_ids)],
                subtype_id=request.env['ir.model.data'].xmlid_to_res_id(
                    'mail.mt_comment')
            )
            request.env['mail.message'].with_user(
                SUPERUSER_ID).create(values)

            for attachment_id_id in orphan_attachment_ids:
                self.record.attachment_ids = [(4, attachment_id_id)]

    def insert_record(self, request, model, values, custom, meta=None):
        applicant_id = super(HrRecruitmentPostulation, self)\
            .insert_record(request, model, values, custom, meta=None)

        self.record = request.env[self.bank_resume_model]\
            .create(dict(
                # TODO: falta asociar modulo de documentos al banco de
                # hojas de vida
                # Para almacenar la hoja de vida
                name=values.get('partner_name'),
                email=values.get('email_from'),
                contact_phone=values.get('partner_phone'),
                availability=values.get('description'),
                vacant=values.get('job_id'),
                # TODO:revisar estos campos obligatorios en banco
                # de hojas de vida
                laboral_experience='without_exp',
                english_level='low',
                studies='technician',
                technologies='net'
            ))
        return applicant_id

    def insert_attachment(self, model, id_record, files):
        res = super(HrRecruitmentPostulation, self).insert_attachment(
            model, id_record, files)

        model_name = model.sudo().model
        if model_name == 'hr.applicant':
            applicant = request.env['hr.applicant'].browse(id_record)
            self.insert_attachment_bank_resumes(applicant, files)
        return res
