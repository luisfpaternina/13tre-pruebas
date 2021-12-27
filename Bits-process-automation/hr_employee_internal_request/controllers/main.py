from odoo import http, models, fields, _
from odoo.http import request
from odoo.addons.portal.controllers.web import Home


class Website(Home):

    @http.route(['/website/publish'], type='json', auth="user", website=True)
    def publish(self, id, object):
        Model = request.env[object]
        record = Model.browse(int(id))

        values = {}
        if 'website_published' in Model._fields:
            values['website_published'] = not record.website_published

        if 'internal_request_ids' in Model._fields\
                and values['website_published']:
            print(record.read({'internal_request_ids'}))
            record.internal_request_ids\
                .action_request_process_by_publish()

        record.write(values)
        return bool(record.website_published)
