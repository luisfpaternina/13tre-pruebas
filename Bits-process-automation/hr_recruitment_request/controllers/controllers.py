# -*- coding: utf-8 -*-
# from odoo import http


# class HrRecruitmentRequest(http.Controller):
#     @http.route('/hr_recruitment_request/hr_recruitment_request/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/hr_recruitment_request/hr_recruitment_request/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('hr_recruitment_request.listing', {
#             'root': '/hr_recruitment_request/hr_recruitment_request',
#             'objects': http.request.env['hr_recruitment_request.hr_recruitment_request'].search([]),
#         })

#     @http.route('/hr_recruitment_request/hr_recruitment_request/objects/<model("hr_recruitment_request.hr_recruitment_request"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('hr_recruitment_request.object', {
#             'object': obj
#         })
