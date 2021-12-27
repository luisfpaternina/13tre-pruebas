# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

# class to add fields required by Hr


class ResPartner(models.Model):
    _inherit = 'res.partner'

    # validation is added so that the document number and document type are
    # unique
    _sql_constraints = [
        ('bist_res_partner_unique_constraint',
         'UNIQUE (document_type, number_identification)',
         'A constraint is being violated: bits_res_partner_unique_constraint')
    ]

    # field to add a list of document type options
    document_type = fields.Selection(
        selection=[
            ('11', 'Birth certificate'),
            ('12', 'Identity card'), ('13', 'Citizenship card'),
            ('21', 'Foreigner identity card'),
            ('22', 'Foreigner ID'), ('41', 'Passport'), ('31', 'NIT'),
            ('42', 'Foreigner identity document'),
            ('43', 'Without outside identification, for defined use DIAN'),
            ('id_document', 'Cédula'),
            ('external_id', 'ID del Exterior'),
            ('diplomatic_card', 'Carné Diplomatico'),
            ('residence_document', 'Salvoconducto de Permanencia'),
            ('OT', 'Others')
        ]
    )

    country_code = fields.Char(related='country_id.code')

    # field to store the document number
    number_identification = fields.Char()

    # field to store the full name
    first_name = fields.Char()
    second_name = fields.Char()
    first_surname = fields.Char()
    second_surname = fields.Char()

    # Field document type list
    l10n_co_document_type = fields.Selection(selection_add=[
        ('21', 'Tarjeta de Extranjeria'),
        ('42', 'Documento Identificación Extranjero'),
        ('43', 'Sin identificación del exterior, para uso definido DIAN')
    ])

    # Standardization of document type fields
    document_type_data = {
        "civil_registration": "11",
        "id_card": "12",
        "national_citizen_id": "13",
        "21": "21",
        "foreign_id_card": "22",
        "rut": "31",
        "passport": "41",
        "42": "42",
        "43": "43",
        "id_document": "id_document",
        "external_id": "external_id",
        "diplomatic_card": "diplomatic_card",
        "residence_document": "residence_document",
        "id_document" : "13",
    }

    # Field partner relation HU 8753
    partner_relation_id = fields.Many2one(
        "res.partner",
        string=_("Company"),
        domain=[('is_company', '=', True)]
    )

    # Compute field employee
    display_employee = fields.Char(
        _("Display Employee"),
        compute="_display_employee"
    )

    def _display_employee(self):
        for line in self:
            line.display_employee = _("EMPLOYEE")\
                if line.employee else ""

    def validation_number_id_alphanumeric(self):
        # Verification that the string is numeric
        if not self.number_identification.isdigit():
            raise ValidationError(
                _('The document number cannot be alphanumeric')
            )

    def validations_for_basics_documents(self):
        self.validation_number_id_alphanumeric()

        # Verification that the identity number is not more
        #  than 10 digits and less than 7 for cc(13) and ti(12)
        if len(
                self.number_identification) > 10 or len(
                self.number_identification) < 7:
            raise ValidationError(
                _('The length of the document number must be between 7 and 10')
            )

    def validations_for_passport(self):
        # It is verified that the string is alphanumeric and
        #  that its length is not less than 7
        if not(self.number_identification.isalnum() and
               not self.number_identification.isdigit()):
            raise ValidationError(
                _('The passport number must contain numbers and characters')
            )

        if len(self.number_identification) < 7:
            raise ValidationError(
                _('The length of the passport number cannot be less than 9')
            )

    def validations_for_ce(self):
        self.validation_number_id_alphanumeric()
        #  Verification that the identity number is not more
        #  than 15 digits and less than 6 for ce (22)
        if (
            len(self.number_identification) > 15
            or len(self.number_identification) < 6
        ):
            raise ValidationError(
                _('The length of the document number must be between 6 and 15')
            )

    def general_validations(self):
        if self.number_identification:
            if (
                self.company_type == "company"
                and self.document_type != "31"
                and self.country_id.code == 'CO'
            ):
                raise ValidationError(
                    _('The type of document for companies is the NIT')
                )
            elif (
                self.document_type == "12"
                or self.document_type == "13"
            ):
                self.validations_for_basics_documents()
            elif (
                self.document_type == "41"
            ):
                self.validations_for_passport()
            elif (
                self.document_type == "22"
            ):
                self.validations_for_ce()
            elif (
                not self.document_type
            ):
                raise ValidationError(
                    _('The field for the document type must not be empty')
                )
        else:
            raise ValidationError(
                _('The field for the document number cannot be empty')
            )

    @api.onchange('number_identification')
    def delete_spaces_in_id(self):
        # Verification that there are no spaces in the string
        if self.number_identification:
            self.number_identification = self.number_identification \
                if not self.number_identification.find(" ") > 0 \
                else self.number_identification.replace(" ", "")

    # set of validations for correct data storage
    @api.constrains('number_identification', 'document_type', 'company_type')
    def _check_number_identification(self):
        self.general_validations()

    # Create name field
    @api.onchange(
        'first_name',
        'second_name',
        'first_surname',
        'second_surname')
    def _on_change_name(self):
        second_name = " " + self.second_name if self.second_name else ''
        first_surname = " " + self.first_surname if self.first_surname else ''
        second_surname = " " + \
            self.second_surname if self.second_surname else ''
        if self.first_name:
            self.name = self.first_name + \
                second_name + first_surname + second_surname

    # Match document type fields
    @api.onchange(
        'l10n_co_document_type'
    )
    def _on_change_l10n_co_document_type(self):
        document_type = self.document_type_data.\
            get(self.l10n_co_document_type, 'OT')
        self.document_type = document_type

    # Match number identification
    @api.onchange('vat')
    def _on_change_vat(self):
        if self.vat:
            self.number_identification = self.vat

    # NIT Rule Verification Code
    @api.depends('l10n_co_document_type')
    def _compute_verification_code(self):
        if self.l10n_co_document_type == 'rut':
            super(ResPartner, self)._compute_verification_code()
        else:
            self.l10n_co_verification_code = ''

    @api.constrains('vat', 'country_id', 'l10n_co_document_type')
    def check_vat(self):
        return True
