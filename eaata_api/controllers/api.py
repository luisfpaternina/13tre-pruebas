# -*- coding: utf-8 -*-

import sys
from odoo import http
from odoo.http import request
from odoo.http import Response
from odoo.exceptions import UserError
import json
from datetime import datetime

import logging
_logger = logging.getLogger(__name__)

class EAATARestApi(http.Controller):

    @http.route('/CADASTRA_CLIENTE', type='json', methods=['POST'], auth='user')
    def action_cadastro_cliente(self, **kwargs):

        data = request.httprequest.data
        data_dict = json.loads(data)

        partner_data = {}

        partner_id = False
        if data_dict.get("ID"):
            partner_id = request.env["res.partner"].sudo().search([("id","=",data_dict.get("ID"))], limit=1)

        if not data_dict.get("Email") and not partner_id:
            raise UserError('Email is required.')

        email = data_dict.get("Email") or (partner_id.email if partner_id else False)
        x_mail2 = data_dict.get("Email 2") or (partner_id.x_mail2 if partner_id else False)
        name = data_dict.get("Nome") or (partner_id.name if partner_id else False)
        phone = data_dict.get("Telefone") or (partner_id.phone if partner_id else False)

        vat = data_dict.get("Número") or (partner_id.vat if partner_id else False)

        if not data_dict.get("Idioma") and not partner_id:
            raise UserError('Idioma is required.')

        lang = data_dict.get("Idioma") or (partner_id.lang if partner_id else False)

        if not data_dict.get("Company Type") and not partner_id:
            raise UserError('Company Type is required.')

        company_type = data_dict.get("Company Type") or (partner_id.company_type if partner_id else False)
        partner_name = data_dict.get("Nome da Empresa") or (partner_id.name if partner_id else False)
        comment = data_dict.get("Nota Interna") or (partner_id.comment if partner_id else False)

        if not data_dict.get("Numero de Identificação") and not partner_id:
            raise UserError('Numero de Identificação is required.')

        l10n_latam_identification_type_id = request.env["l10n_latam.identification.type"].sudo().search([("id","=",data_dict.get("Numero de Identificação") or (partner_id.l10n_latam_identification_type_id.id if partner_id else False))], limit=1)
        if not l10n_latam_identification_type_id:
            raise UserError('Numero de Identificação not found.')

        country_id = False
        if data_dict.get("País") or (partner_id.country_id if partner_id else False):
            country_id = request.env["res.country"].sudo().search([("id","=",data_dict.get("País") or (partner_id.country_id.id if partner_id else False))], limit=1)
            if not country_id:
                raise UserError('País not found.')

        property_product_pricelist = False
        if data_dict.get("Tarifa") or (partner_id.property_product_pricelist if partner_id else False):
            property_product_pricelist = request.env["product.pricelist"].sudo().search([("id","=",data_dict.get("Tarifa") or (partner_id.property_product_pricelist.id if partner_id else False))], limit=1)
            if not property_product_pricelist:
                raise UserError('Tarifa not found.')

        parent_id = False
        if data_dict.get("Empresa Pai") or (partner_id.parent_id if partner_id else False):
            parent_id = request.env["res.partner"].sudo().search([("id","=",data_dict.get("Empresa Pai") or (partner_id.parent_id.id if partner_id else False))], limit=1)
            if not parent_id:
                raise UserError('Empresa Pai not found.')

        category_id = False
        if data_dict.get("Categorias") or (partner_id.category_id if partner_id else False):
            category_id = request.env["res.partner.category"].sudo().search([("id","=",data_dict.get("Categorias") or (partner_id.category_id.id if partner_id else False))], limit=1)
            if not category_id:
                raise UserError('Categorias not found.')

        if not data_dict.get("Company") and not partner_id:
            raise UserError('Company is required.')

        company_id = request.env["res.company"].sudo().search([("id","=",data_dict.get("Company") or (partner_id.company_id.id if partner_id else False))], limit=1)
        if not company_id:
            raise UserError('Company not found.')

        if not data_dict.get("Comercial") and not partner_id:
            raise UserError('Comercial is required.')

        user_id = request.env["res.users"].sudo().search([("id","=",data_dict.get("Comercial") or (partner_id.user_id.id if partner_id else False))], limit=1)
        if not user_id:
            raise UserError('Comercial not found.')

        if not data_dict.get("Sales Team") and not partner_id:
            raise UserError('Sales Team is required.')

        team_id = request.env["crm.team"].sudo().search([("id","=",data_dict.get("Sales Team") or (partner_id.team_id.id if partner_id else False))], limit=1)
        if not team_id:
            raise UserError('Sales Team not found.')

        partner_data["email"] = email
        partner_data["x_mail2"] = x_mail2
        partner_data["name"] = name or partner_name
        partner_data["phone"] = phone
        partner_data["vat"] = vat
        partner_data["lang"] = lang
        partner_data["company_type"] = company_type
        #partner_data["partner_name"] = partner_name
        partner_data["comment"] = comment
        partner_data["l10n_latam_identification_type_id"] = l10n_latam_identification_type_id.id if l10n_latam_identification_type_id else False
        partner_data["country_id"] = country_id.id if country_id else False
        partner_data["property_product_pricelist"] = property_product_pricelist.id if property_product_pricelist else False
        partner_data["parent_id"] = parent_id.id if parent_id else False
        partner_data["category_id"] = [(6,0,[category_id.id])] if category_id else False
        partner_data["company_id"] = company_id.id if company_id else False
        partner_data["user_id"] = user_id.id if user_id else False
        partner_data["team_id"] = team_id.id if team_id else False

        if data_dict.get("tool_ids"):
            tool_ids = []
            for item in data_dict.get("tool_ids"):

                name = item.get("Serial")

                tool_id = False
                if partner_id:
                    tool_id = request.env["res.partner.tool"].sudo().search([("partner_id","=",partner_id.id),("name","=",name)], limit=1)

                if not item.get("Marca") and not tool_id:
                    raise UserError('Tool Brand is required.')

                tool_brand_id = request.env["helpdesk.tool.brand"].sudo().search([("id","=",item.get("Marca"))], limit=1)
                if not tool_brand_id and not tool_id:
                    raise UserError('Tool Brand not found.')

                if not item.get("Modelo") and not tool_id:
                    raise UserError('Tool Model is required.')

                tool_model_id = request.env["helpdesk.tool.model"].sudo().search([("id","=",item.get("Modelo"))], limit=1)
                if not tool_model_id and not tool_id:
                    raise UserError('Tool Model not found.')


                date_from = item.get("Desde")
                date_to = item.get("Hasta")
                support_active = item.get("Soporte Activo")
                fecha_actualizacion = item.get("Fecha de Actualización")

                tool_data = {}
                tool_data["tool_brand_id"] = tool_brand_id.id or (tool_id.tool_brand_id.id if tool_id else False)
                tool_data["tool_model_id"] = tool_model_id.id or (tool_id.tool_model_id.id if tool_id else False)
                tool_data["name"] = name or (tool_id.name if tool_id else "")
                tool_data["date_from"] = date_from or (tool_id.date_from if tool_id else False)
                tool_data["date_to"] = date_to or (tool_id.date_to if tool_id else False)
                tool_data["support_active"] = support_active or (tool_id.support_active if tool_id else False)
                tool_data["fecha_actualizacion"] = fecha_actualizacion or (tool_id.fecha_actualizacion if tool_id else False)

                if tool_id:
                    tool_ids.append((1,tool_id.id,tool_data))
                else:
                    tool_ids.append((0,0,tool_data))

            if tool_ids:
                partner_data["tool_ids"] = tool_ids

        if not partner_id:
            partner_id = request.env["res.partner"].sudo().create(partner_data)
        else:
            partner_id.sudo().write(partner_data)

        values = {}
        values["ID"] = partner_id.id
        data = [values]
        data = [dict(t) for t in {tuple(d.items()) for d in data}]
        return json.dumps(data)


    @http.route('/CONSULTA_CADASTRO/<string:email>', type='http', methods=['GET'], auth='user')

    def action_consulta_cadastro(self, email, **kwargs):

        try:

            try:

                if not email:
                    raise UserError('E-mail is required.')

                partner_id = request.env["res.partner"].sudo().search(["|",("email","=",email),("x_mail2","=",email)], limit=1)
                lead_id = request.env["crm.lead"].sudo().search([("email_from","=",email)],limit=1)
                archived_lead_id = request.env["crm.lead"].sudo().search([("active","=",False),("email_from","=",email)],limit=1)

                values = {}
                values["ID"] = partner_id.id if partner_id else False

                values["Status"] = "ATIVADO"
                
                if lead_id and lead_id.probability < 100:                
                    values["Status"] = "EM PROCESSO"

                if not lead_id and archived_lead_id:
                    values["Status"] = "NEGADO"

                if not lead_id and not archived_lead_id and not partner_id:
                    values["Status"] = "NAO EXISTE"

                data = [values]
                data = [dict(t) for t in {tuple(d.items()) for d in data}]
                return json.dumps(data)

            except Exception as e:
                return Response('400 Bad Request (%s)' % str(e), content_type='text/html;charset=utf-8', status=404)

        except Exception as e:
            return Response('400 Bad Request (%s)' % str(e), content_type='text/html;charset=utf-8', status=404)

    @http.route('/SOLICITA_CADASTRO', type='json', methods=['POST'], auth='user')
    def action_solicita_cadastro(self, **kwargs):

        try:

            try:

                data = request.httprequest.data
                data_dict = json.loads(data)

            except Exception as e:
                return Response('400 Bad Request (%s)' % str(e), content_type='text/html;charset=utf-8', status=404)

            try:

                lead_data = {}

                partner_id = False
                if data_dict.get("ID"):
                    partner_id = request.env["res.partner"].sudo().search([("id","=",data_dict.get("ID"))], limit=1)
                    if not partner_id:
                        raise UserError('Partner not found.')

                if not data_dict.get("Email"):
                    raise UserError('Email is required.')

                email_from = data_dict.get("Email")
                contact_name = data_dict.get("Nome")
                phone = data_dict.get("Telefone")

                country_id = request.env["res.country"].sudo().search([("id","=",data_dict.get("País"))], limit=1)
                if not country_id:
                    raise UserError('Country not found.')

                partner_name = data_dict.get("Nome da Empresa")
                x_studio_nif = data_dict.get("NIF")

                tag_id = False
                if data_dict.get("Marcador"):
                    tag_id = request.env["crm.lead.tag"].sudo().search([("id","=",data_dict.get("Marcador"))], limit=1)
                    if not tag_id:
                        raise UserError('Tag not found.')

                description = data_dict.get("Nota Interna")

                if not data_dict.get("Company"):
                    raise UserError('Company is required.')

                company_id = request.env["res.company"].sudo().search([("id","=",data_dict.get("Company"))], limit=1)
                if not company_id:
                    raise UserError('Company not found.')

                if not data_dict.get("Comercial"):
                    raise UserError('Comercial is required.')

                user_id = request.env["res.users"].sudo().search([("id","=",data_dict.get("Comercial"))], limit=1)
                if not user_id:
                    raise UserError('Comercial not found.')

                if not data_dict.get("Sales Team"):
                    raise UserError('Sales Team is required.')

                team_id = request.env["crm.team"].sudo().search([("id","=",data_dict.get("Sales Team"))], limit=1)
                if not team_id:
                    raise UserError('Sales Team not found.')

                lead_data["partner_id"] = partner_id.id if partner_id else False
                lead_data["email_from"] = email_from
                lead_data["contact_name"] = contact_name
                lead_data["phone"] = phone
                lead_data["country_id"] = country_id.id if country_id else False
                lead_data["partner_name"] = partner_name
                lead_data["x_studio_nif"] = x_studio_nif
                lead_data["tag_ids"] = [(6,0,[tag_id.id])] if tag_id else False
                lead_data["description"] = description
                lead_data["company_id"] = company_id.id
                lead_data["user_id"] = user_id.id
                lead_data["team_id"] = team_id.id
                lead_data["name"] = partner_id.name if partner_id else contact_name
                lead_data["probability"] = 99.90
                lead_data["type"] = "opportunity"
                lead_data["priority"] = "0"
                
                if data_dict.get("tool_ids"):
                    tool_ids = []
                    for item in data_dict.get("tool_ids"):

                        if not item.get("Marca"):
                            raise UserError('Tool Brand is required.')

                        tool_brand_id = request.env["helpdesk.tool.brand"].sudo().search([("id","=",item.get("Marca"))], limit=1)
                        if not tool_brand_id:
                            raise UserError('Tool Brand not found.')

                        if not item.get("Modelo"):
                            raise UserError('Tool Model is required.')

                        tool_model_id = request.env["helpdesk.tool.model"].sudo().search([("id","=",item.get("Modelo"))], limit=1)
                        if not tool_model_id:
                            raise UserError('Tool Model not found.')
                        
                        name = item.get("Serie")

                        tool_data = {}
                        tool_data["tool_brand_id"] = tool_brand_id.id
                        tool_data["tool_model_id"] = tool_model_id.id
                        tool_data["name"] = name
                        
                        tool_ids.append((0,0,tool_data))
                    
                    if tool_ids:
                        lead_data["tool_ids"] = tool_ids

                # {'partner_id': False, 'email_from': 'rafael.petrella@ciel-it.com', 'contact_name': 'Rafael Petrella', 'phone': '', 'country_id': 31, 'partner_name': 'CIEL IT', 'x_studio_nif': '', 'tag_ids': [(6, 0, [1])], 'description': 'TESTE', 'company_id': 2, 'user_id': 15, 'team_id': 34, 'name': 'Rafael Petrella', 'probability': 99.9, 'type': 'lead', 'priority': '0', 'tool_ids': [(0, 0, {'tool_brand_id': 1, 'tool_model_id': 83, 'name': None}), (0, 0, {'tool_brand_id': 1, 'tool_model_id': 19, 'name': None})]}
                lead_id = request.env["crm.lead"].sudo().create(lead_data)
                values = {}
                values["ID"] = lead_id.id
                data = [values]
                data = [dict(t) for t in {tuple(d.items()) for d in data}]
                return json.dumps(data)

            except Exception as e:
                return Response('400 Bad Request (%s)' % str(e), content_type='text/html;charset=utf-8', status=404)

        except Exception as e:
            return Response('400 Bad Request (%s)' % str(e), content_type='text/html;charset=utf-8', status=404)

    @http.route('/CONSULTA_EQUIPAMENTO/<int:id>', type='http', methods=['GET'], auth='user')
    def action_consulta_equipamento(self, id, **kwargs):

        try:

            try:

                if not id:
                    raise UserError('Partner is required.')

                partner_id = request.env["res.partner"].sudo().search([("id","=",id)], limit=1)
                if not partner_id:
                    raise UserError('Partner not found.')

                data = []
                for item in partner_id.tool_ids:
                    values = {}
                    values["Marca"] = item.tool_brand_id.id
                    values["Modelo"] = item.tool_model_id.id
                    values["Serial"] = item.name
                    values["Desde"] = datetime.strftime(item.date_from,'%d/%m/%Y') if item.date_from else ""
                    values["Hasta"] = datetime.strftime(item.date_to,'%d/%m/%Y') if item.date_to else ""
                    values["Soporte Activo"] = item.support_active
                    values["Fecha de Actualización"] = item.fecha_actualizacion
                    
                    data.append(values)

                data = [dict(t) for t in {tuple(d.items()) for d in data}]
                return json.dumps(data)

            except Exception as e:
                return Response('400 Bad Request (%s)' % str(e), content_type='text/html;charset=utf-8', status=404)

        except Exception as e:
            return Response('400 Bad Request (%s)' % str(e), content_type='text/html;charset=utf-8', status=404)

    @http.route('/CRIAR_TICKET', type='json', methods=['POST'], auth='user')
    def action_criar_ticket(self, **kwargs):

        try:

            try:

                data = request.httprequest.data
                data_dict = json.loads(data)

            except Exception as e:
                return Response('400 Bad Request (%s)' % str(e), content_type='text/html;charset=utf-8', status=404)

            try:

                ticket_data = {}

                if not data_dict.get("ID"):
                    raise UserError('Partner is required.')

                partner_id = request.env["res.partner"].sudo().search([("id","=",data_dict.get("ID"))], limit=1)
                if not partner_id:
                    raise UserError('Partner not found.')

                product_id = False
                if data_dict.get("Servicio"):
                    product_id = request.env["product.product"].sudo().search([("id","=",data_dict.get("Servicio"))], limit=1)
                    if not product_id:
                        raise UserError('Product not found.')

                if not data_dict.get("Company"):
                    raise UserError('Company is required.')

                company_id = request.env["res.company"].sudo().search([("id","=",data_dict.get("Company"))], limit=1)
                if not company_id:
                    raise UserError('Company not found.')

                if not data_dict.get("Helpdesk Team"):
                    raise UserError('Helpdesk Team is required.')

                team_id = request.env["helpdesk.team"].sudo().search([("id","=",data_dict.get("Helpdesk Team"))], limit=1)
                if not team_id:
                    raise UserError('Helpdesk Team not found.')

                if not data_dict.get("Tipo de Ticket"):
                    raise UserError('Ticket Type is required.')

                ticket_type_id = request.env["helpdesk.ticket.type"].sudo().search([("id","=",data_dict.get("Tipo de Ticket"))], limit=1)
                if not ticket_type_id:
                    raise UserError('Ticket Type not found.')

                tool_brand_id = False
                if data_dict.get("Marca do Equipamento"):
                    tool_brand_id = request.env["helpdesk.tool.brand"].sudo().search([("id","=",data_dict.get("Marca do Equipamento"))], limit=1)
                    if not tool_brand_id:
                        raise UserError('Tool Brand not found.')

                tool_model_id = False
                if data_dict.get("Modelo do Equipamento"):
                    tool_model_id = request.env["helpdesk.tool.model"].sudo().search([("id","=",data_dict.get("Modelo do Equipamento"))], limit=1)
                    if not tool_model_id:
                        raise UserError('Tool Model not found.')

                vehicle_brand_id = False
                if data_dict.get("Marca do Veículo"):
                    vehicle_brand_id = request.env["helpdesk.vehicle.brand"].sudo().search([("id","=",data_dict.get("Marca do Veículo"))], limit=1)
                    if not vehicle_brand_id:
                        raise UserError('Vehicle Brand not found.')

                vehicle_model = data_dict.get("Modelo do Veículo")

                year_id = False
                if data_dict.get("Ano"):
                    year_id = request.env["helpdesk.year"].sudo().search([("id","=",data_dict.get("Ano"))], limit=1)
                    if not year_id:
                        raise UserError('Year not found.')

                image = data_dict.get("Imagem")

                description = data_dict.get("Descrição")

                ticket_data["name"] = request.env['ir.sequence'].sudo().next_by_code('helpdesk.ticket')
                ticket_data["description"] = description
                ticket_data["active"] = True
                ticket_data["company_id"] = company_id.id
                ticket_data["ticket_type_id"] = ticket_type_id.id
                ticket_data["partner_id"] = partner_id.id
                ticket_data["partner_email"] = partner_id.email
                ticket_data["team_id"] = team_id.id
                ticket_data["product_id"] = product_id.id if product_id else False
                ticket_data["tool_brand_id"] = tool_brand_id.id if tool_brand_id else False
                ticket_data["tool_model_id"] = tool_model_id.id if tool_model_id else False
                ticket_data["vehicle_brand_id"] = vehicle_brand_id.id if vehicle_brand_id else False
                ticket_data["vehicle_model"] = vehicle_model
                ticket_data["year_id"] = year_id.id if year_id else False
                ticket_data["image"] = image if image else False
                
                ticket_id = request.env["helpdesk.ticket"].sudo().create(ticket_data)

                #if image:
                #    attachment_id = request.env['ir.attachment'].sudo().create({
                #        'name': 'image',
                #        'datas': image,
                #        'res_id': ticket_id.id,
                #        'res_model': 'helpdesk.ticket',
                #    })
                    
                data = [{ "ID": ticket_id.id, "Name": ticket_id.name }]
                data = [dict(t) for t in {tuple(d.items()) for d in data}]
                return json.dumps(data)

            except Exception as e:
                return Response('400 Bad Request (%s)' % str(e), content_type='text/html;charset=utf-8', status=404)

        except Exception as e:
            return Response('400 Bad Request (%s)' % str(e), content_type='text/html;charset=utf-8', status=404)

    @http.route('/CADASTRA_ASSINATURA', type='json', methods=['POST'], auth='user')
    def action_solicita_cadastro_assinatura(self, **kwargs):

        try:

            try:

                data = request.httprequest.data
                data_dict = json.loads(data)

            except Exception as e:
                _logger.info(str(e))
                return '400 Bad Request (%s)' % str(e)

            try:

                subscription_data = {}

                subscription_id = False
                if data_dict.get("id"):
                    subscription_id = request.env["sale.subscription"].sudo().search([("id","=",data_dict.get("id"))], limit=1)
                    if not subscription_id:
                        raise UserError('Subscription not found.')

                stage_id = False
                if data_dict.get("Stage"):
                    stage_id = request.env["sale.subscription.stage"].sudo().search([("id","=",data_dict.get("Stage"))], limit=1)
                    if not stage_id:
                        raise UserError('Stage not found.')
                
                if not stage_id and subscription_id:
                    stage_id = subscription_id.stage_id

                if not data_dict.get("Cliente") and not subscription_id:
                    raise UserError('Cliente is required.')

                partner_id = request.env["res.partner"].sudo().search([("id","=",data_dict.get("Cliente") or subscription_id and subscription_id.partner_id.id)], limit=1)
                if not partner_id:
                    raise UserError('Cliente not found.')

                partner_id2 = subscription_id.partner_id2 if subscription_id else False
                if data_dict.get("Cliente Assinatura"):
                    partner_id2 = request.env["res.partner"].sudo().search([("id","=",data_dict.get("Cliente Assinatura") or subscription_id and subscription_id.partner_id2.id)], limit=1)
                    if not partner_id2:
                        raise UserError('Cliente Assinatura not found.')

                date_start = data_dict.get("Fecha de Inicio") or subscription_id and subscription_id.date_start
                recurring_next_date = data_dict.get("Fecha de la próxima Factura") or subscription_id and subscription_id.recurring_next_date
                date = data_dict.get("Fecha de Fim") or subscription_id and subscription_id.date
                
                if not data_dict.get("Plantilla de la suscripción") and not subscription_id:
                    raise UserError('Plantilla de la suscripción is required.')

                template_id = request.env["sale.subscription.template"].sudo().search([("id","=",data_dict.get("Plantilla de la suscripción") or subscription_id and subscription_id.template_id.id)], limit=1)
                if not template_id:
                    raise UserError('Plantilla de la suscripción.')

                user_id = False or subscription_id and subscription_id.user_id
                if data_dict.get("Comercial"):
                    user_id = request.env["res.users"].sudo().search([("id","=",data_dict.get("Comercial"))], limit=1)
                    if not user_id:
                        raise UserError('Comercial not found.')

                team_id = False or subscription_id and subscription_id.team_id
                if data_dict.get("Equipo de Ventas"):
                    team_id = request.env["crm.team"].sudo().search([("id","=",data_dict.get("Equipo de Ventas"))], limit=1)
                    if not team_id:
                        raise UserError('Equipo de Ventas not found.')

                company_id = False or subscription_id and subscription_id.company_id
                if data_dict.get("Compañia"):
                    company_id = request.env["res.company"].sudo().search([("id","=",data_dict.get("Compañia"))], limit=1)
                    if not company_id:
                        raise UserError('Compañia not found.')

                notes = data_dict.get("Notas") or subscription_id and subscription_id.notes

                subscription_data["stage_id"] = stage_id.id if stage_id else False
                subscription_data["partner_id"] = partner_id.id if partner_id else False
                subscription_data["partner_id2"] = partner_id2.id if partner_id2 else False
                subscription_data["date_start"] = date_start
                subscription_data["recurring_next_date"] = recurring_next_date
                subscription_data["date"] = date
                subscription_data["description"] = notes

                if template_id:
                    subscription_data["template_id"] = template_id.id
                
                if user_id:
                    subscription_data["user_id"] = user_id.id
                
                if team_id:
                    subscription_data["team_id"] = team_id.id

                if company_id:
                    subscription_data["company_id"] = company_id.id
                    subscription_data["pricelist_id"] = subscription_id and subscription_id.pricelist_id.id or request.env['product.pricelist'].sudo().search([('currency_id', '=', company_id.currency_id.id),('company_id', '=', company_id.id)], limit=1).id

                if data_dict.get("Tarifa"):
                    pricelist_id = request.env["product.pricelist"].sudo().search([("id","=",data_dict.get("Tarifa"))], limit=1)
                    if not pricelist_id:
                        raise UserError('Tarifa not found.')
                    subscription_data["pricelist_id"] = pricelist_id.id

                if data_dict.get("tool_ids"):
                    
                    tool_ids = []
                    
                    if subscription_id:
                        for item in subscription_id.tool_ids:
                            tool_ids.append((2, item.id))

                    for item in data_dict.get("tool_ids"):

                        if not item.get("Marca de Herramienta"):
                            raise UserError('Tool Marca de Herramienta is required.')

                        tool_brand_id = request.env["helpdesk.tool.brand"].sudo().search([("id","=",item.get("Marca de Herramienta"))], limit=1)
                        if not tool_brand_id:
                            raise UserError('Tool Marca de Herramienta not found.')

                        if not item.get("Modelo de Herramienta"):
                            raise UserError('Tool Modelo de Herramienta is required.')

                        tool_model_id = request.env["helpdesk.tool.model"].sudo().search([("id","=",item.get("Modelo de Herramienta"))], limit=1)
                        if not tool_model_id:
                            raise UserError('Tool Modelo de Herramienta not found.')
                        
                        name = item.get("No. De Serie")

                        if not item.get("Desde"):
                            raise UserError('Tool Desde is required.')
                        
                        date_from = item.get("Desde")
                        date_to = item.get("Hasta")
                        support_active = item.get("Soporte Activo")
                        fecha_actualizacion = item.get("Fecha de Actualización")
                        
                        tool_data = {}
                        tool_data["tool_brand_id"] = tool_brand_id.id
                        tool_data["tool_model_id"] = tool_model_id.id
                        tool_data["name"] = name
                        tool_data["date_from"] = date_from
                        tool_data["date_to"] = date_to
                        tool_data["support_active"] = support_active
                        tool_data["fecha_actualizacion"] = fecha_actualizacion

                        tool_ids.append((0,0,tool_data))

                    if tool_ids:
                        subscription_data["tool_ids"] = tool_ids

                if data_dict.get("product_ids"):
                    product_ids = []

                    if subscription_id:
                        for item in subscription_id.recurring_invoice_line_ids:
                            product_ids.append((2, item.id))

                    for item in data_dict.get("product_ids"):

                        if not item.get("Producto"):
                            raise UserError('Producto is required.')

                        product_id = request.env["product.product"].sudo().search([("product_tmpl_id","=",item.get("Producto"))], limit=1)
                        if not product_id:
                            raise UserError('Producto not found.')

                        quantity = item.get("Cantidad")
                        price_unit = item.get("Precio")
                        discount = item.get("Desc")

                        product_data = {}
                        product_data["product_id"] = product_id.id
                        product_data["uom_id"] = product_id.uom_id.id
                        product_data["quantity"] = quantity
                        product_data["price_unit"] = price_unit
                        product_data["discount"] = discount

                        product_ids.append((0,0,product_data))

                    if product_ids:
                        subscription_data["recurring_invoice_line_ids"] = product_ids

                _logger.info(subscription_data)
                with request.env.cr.savepoint():
                    if subscription_id:
                        subscription_id.sudo().write(subscription_data)
                    else:
                        subscription_id = request.env["sale.subscription"].sudo().create(subscription_data)

                values = {}
                values["ID"] = subscription_id.id
                data = [values]
                data = [dict(t) for t in {tuple(d.items()) for d in data}]
                return json.dumps(data)

            except Exception as e:
                _logger.info(sys.exc_info()[2].tb_lineno)
                _logger.info(str(e))
                return '400 Bad Request (%s)' % str(e)

        except Exception as e:
            _logger.info(str(e))
            return '400 Bad Request (%s)' % str(e)

    @http.route('/CONSULTA_ASSINATURA', type='json', methods=['POST'], auth='user')
    def action_consulta_assinatura(self, **kwargs):
        try:

            try:

                data = request.httprequest.data
                data_dict = json.loads(data)

            except Exception as e:
                _logger.info(str(e))
                return '400 Bad Request (%s)' % str(e)

            try:

                if not data_dict.get("ID"):
                    raise UserError('ID is required.')

                partner_id = request.env["res.partner"].sudo().search([("id","=",data_dict.get("ID"))], limit=1)
                if not partner_id:
                    raise UserError('Cliente not found.')

                date_start = data_dict.get("Fecha de Inicio")
                date = data_dict.get("Fecha de Fim")

                domain = ["|",("partner_id","=",partner_id.id),("partner_id2","=",partner_id.id)]
                if date_start and len(date_start) == 2:
                    domain.append(("date_start",">=",date_start[0]))
                    domain.append(("date_start","<=",date_start[1]))

                if date and len(date) == 2:
                    domain.append(("date",">=",date[0]))
                    domain.append(("date","<=",date[1]))

                subscription_ids = request.env["sale.subscription"].sudo().search(domain)

                data = []
                for item in subscription_ids:
                    subscription_data = {}

                    subscription_data["id"] = item.id
                    subscription_data["Stage"] = item.stage_id.id
                    subscription_data["Cliente"] = item.partner_id.id
                    subscription_data["Fecha de Inicio"] = datetime.strftime(item.date_start,'%d/%m/%Y') if item.date_start else ""
                    subscription_data["Fecha de la próxima Factura"] = datetime.strftime(item.recurring_next_date,'%d/%m/%Y') if item.recurring_next_date else ""
                    subscription_data["Fecha de Fim"] = datetime.strftime(item.date,'%d/%m/%Y') if item.date else ""
                    subscription_data["Plantilla de la suscripción"] = item.template_id.id
                    subscription_data["Comercial"] = item.user_id.id
                    subscription_data["Equipo de Ventas"] = item.team_id.id
                    subscription_data["Compañia"] = item.company_id.id
                    
                    tool_ids = []
                    for tool_id in item.tool_ids:
                        tool_data = {}
                        tool_data["Modelo de Herramienta"] = tool_id.tool_model_id.id
                        tool_data["No. De Serie"] = tool_id.name
                        tool_data["Desde"] = datetime.strftime(tool_id.date_from,'%d/%m/%Y') if tool_id.date_from else ""
                        tool_data["Hasta"] = datetime.strftime(tool_id.date_to,'%d/%m/%Y') if tool_id.date_to else ""
                        tool_data["Soporte Activo"] = tool_id.support_active
                        tool_data["Fecha de Actualización"] = tool_id.fecha_actualizacion

                        tool_ids.append(tool_data)

                    tool_ids = [dict(t) for t in {tuple(d.items()) for d in tool_ids}]
                    subscription_data["tool_ids"] = json.dumps(tool_ids)

                    product_ids = []
                    for product_id in item.recurring_invoice_line_ids:
                        tool_data = {}
                        tool_data["Producto"] = product_id.product_id.id
                        tool_data["Cantidad"] = product_id.quantity
                        tool_data["Precio"] = product_id.price_unit
                        tool_data["Desc"] = product_id.discount

                        product_ids.append(tool_data)
                    
                    product_ids = [dict(t) for t in {tuple(d.items()) for d in product_ids}]
                    subscription_data["product_ids"] = json.dumps(product_ids)
                    
                    data.append(subscription_data)

                data = [dict(t) for t in {tuple(d.items()) for d in data}]
                return json.dumps(data)

            except Exception as e:
                _logger.info(str(e))
                return '400 Bad Request (%s)' % str(e)

        except Exception as e:
            _logger.info(str(e))
            return '400 Bad Request (%s)' % str(e)

