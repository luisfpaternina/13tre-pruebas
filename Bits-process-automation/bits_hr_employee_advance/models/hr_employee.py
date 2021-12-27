from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from .compute import calculeAge
import re


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    # INFORMARCIÓN PRINCIPAL #PRINCIPAL
    names = fields.Char('Names', size=40, default='')
    surnames = fields.Char('Surnames', size=40, default='')
    known_as = fields.Char('Known as', size=75, default='')
    time_at_bits = fields.Integer(
        'Time at bits', compute='_compute_time_at_bits')
    # tipos de contrato bits
    contract_type = fields.Selection([
        ('1', 'fixed term contract'),
        ('2', 'indefinite term contract'),
        ('3', 'work o labor'),
        ('4', 'Learning'),
        ('5', 'Interpships')
    ], string='Contract type', compute='_compute_contract_type')
    # Fecha de ingreso/terminación
    begin_date = fields.Date('Begin date')
    end_date = fields.Date('End date')
    document_type = fields.Selection([
        ('12', "Identity card"),
        ('13', "Citizenship card"),
        ('22', 'Foreigner ID'),
        ('41', 'Passport'),
        ('OT', 'Others')
    ], string="Document type", required=True, default='13')
    expedition_date = fields.Date('Expedition date')
    expedition_city = fields.Char('Expedition city', size=40)
    # INFORMACIÓN PRIVADA
    # PRIVATE CONTACT
    address_location = fields.Char('Location', size=40)
    # Barrio
    address_neighborhood = fields.Char('Neighborhood', size=40)
    allergies = fields.Char('Allergies', size=40)
    food_preferences = fields.Char('food preferences', size=40)

    # CITIZENSHIP
    # Edad del colaborador
    age = fields.Integer(compute='_compute_age', string='Age')

    # FAMILIAR
    # Edad de la pareja
    spouse_names = fields.Char('spouse names')
    spouse_surnames = fields.Char('spouse surnames')
    spouse_age = fields.Integer(compute='_compute_age', string='Spouse age')
    # información del conyugue
    spouse_document_type = fields.Selection([
        ('12', "Identity card"),
        ('13', "Citizenship card"),
        ('22', 'Foreigner ID'),
        ('41', 'Passport'),
        ('OT', 'Others')
    ], string="spouse document type", required=True, default='13')
    spouse_indentification_number = fields.Char(
        'Spouse identification number', size=15)
    # tipo de recidencia
    residence_type = fields.Selection([
        ('cp', 'Own house'),
        ('ca', 'Leased house'),
        ('ap', 'Own apartment'),
        ('aa', 'Leased apartment'),
        ('aep', 'Own studio apartment'),
        ('aea', 'Leased studio apartment')
    ], string='Residence type')

    # EMERGENCY
    # Parentesco
    kinship = fields.Char('Kinship', size=50)
    # grupo sanguineo
    bloody_group = fields.Selection([
        ('o', 'O'),
        ('a', 'A'),
        ('b', 'B'),
        ('ab', 'AB')
    ], string="bloody group")
    # factor rh
    rh_factor = fields.Selection([
        ('plus', '+'),
        ('minus', '-')
    ], string='RH factor')
    contact_address_emergency = fields.Char(
        'Contact address emergency', size=90)
    email_emergency_contact = fields.Char('Email emergency contact', size=60)

    # EDUCACION
    # type_id = fields.Many2one('hr.recruitment.degree', "Title")
    title_type = fields.Selection([
        ('1', 'Bachiller'),
        ('2', 'Técnico'),
        ('3', 'Técnologo'),
        ('4', 'Profesional'),
        ('5', 'Postgrado')
    ], string='Title')
    # fecha renovacion de examenes
    exam_renewal = fields.Date('Exam renewal')

    # Centro de costo
    employee_center_cost_ids = fields.One2many(
        'hr.employee.center.cost', 'employee_id', string='Center cost')

    @api.depends('contract_ids')
    def _compute_contract_type(self):
        for record in self:
            if record.contract_ids:
                for contract in record.contract_ids:
                    if contract.state == 'open':
                        record.contract_type = contract.type_contract
                        break
                    else:
                        record.contract_type = False
            
            else:
                record.contract_type = False

    @api.constrains('employee_center_cost_ids')
    def _check_workload(self):
        percentage_required = float(self.env['ir.config_parameter'].sudo()
                                    .get_param('percentage_workload'))
        sum = 0
        for center in self.employee_center_cost_ids:
            sum += float(center.percentage)
        if sum != percentage_required:
            raise ValidationError(
                _('The employee is not complying ' +
                    f'with the {percentage_required}% ' +
                    'workload within the cost centers')
            )

    @api.onchange('birthday', 'spouse_birthdate')
    def _compute_age(self):
        for applicant in self:
            applicant.age = 0
            applicant.spouse_age = 0

            if applicant.birthday:
                applicant.age = calculeAge(applicant.birthday)

            if applicant.spouse_birthdate:
                applicant.spouse_age = calculeAge(applicant.spouse_birthdate)

    @api.onchange('time_at_bits')
    def _compute_time_at_bits(self):
        for applicant in self:
            applicant.time_at_bits = 0

            if applicant.begin_date:
                applicant.time_at_bits = calculeAge(applicant.begin_date)

    @api.constrains('email_emergency_contact')
    def _validate_email(self):
        if self.email_emergency_contact:
            re_validate_email = re.compile(
                r'^[_a-z0-9-]+(\.[_a-z0-9-]+)'
                r'*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$'
            )

            validate_email = re.match(
                re_validate_email,
                self.email_emergency_contact)

            if validate_email is None:
                raise ValidationError(
                    _(
                        "It's not a valid format email for:"
                        'email_emergency_contact'
                    )
                )

    def validation_number_id_alphanumeric(self, identification_id):
        # Verification that the string is numeric
        if not identification_id.isdigit():
            raise ValidationError(
                _('The document number cannot be alphanumeric')
            )

    @api.model_create_multi
    def create(self, vals):
        for val in vals:
            document_type = val.get('document_type', False)
            identification_id = val.get('identification_id', False)
            self.validate_field_requireds(val)
            self._validate_identification_id(document_type, identification_id)
        return super(HrEmployee, self).create(vals)

    def write(self, vals):
        for record in self:
            document_type = (vals.get('document_type', False) if vals.get(
                'document_type', False) else record.document_type)
            identification_id = (vals.get('identification_id', False)
                                 if vals.get('identification_id', False)
                                 else record.identification_id)
            self._validate_identification_id(document_type, identification_id)
        return super(HrEmployee, self).write(vals)

    @api.model
    def _validate_identification_id(self, document_type, identification_id):

        if not document_type:
            raise ValidationError(
                _('The file document type is required')
            )

        if identification_id:
            if (document_type == '12' or
                    document_type == '13'):
                self.validation_number_id_alphanumeric(identification_id)

                if len(identification_id) > 10 or len(identification_id) < 7:
                    raise ValidationError(
                        _('The length of the document '
                          'number must be between 7 and 10')
                    )

            elif document_type == '41':
                # It is verified that the string is alphanumeric and
                #  that its length is not less than 7
                if identification_id.isalnum() and identification_id.isdigit():
                    raise ValidationError(
                        _('The passport number must contain '
                          'numbers and characters')
                    )

                if len(identification_id) < 7:
                    raise ValidationError(
                        _('The lenght of the passport '
                          'number cannot be less than 7')
                    )

            elif document_type == '22':
                self.validation_number_id_alphanumeric(identification_id)
                #  Verification that the identity number is not more
                #  than 15 digits and less than 6 for ce (22)
                if (len(identification_id) > 15
                        or len(identification_id) < 6):
                    raise ValidationError(
                        _('The length of the document '
                          'number must be between 6 and 15')
                    )

            else:
                if document_type != 'OT':
                    raise ValidationError(
                        _('the entered value does '
                          'not match the selection values')
                    )
        else:
            raise ValidationError(
                _('The field indentification_id for '
                  'the document number cannot be empty')
            )

    @api.model
    def validate_field_requireds(self, vals):
        if not vals.get('names'):
            raise ValidationError(
                _("The field 'names' cannot be empty")
            )

        if not vals.get('surnames'):
            raise ValidationError(
                _("The field 'surnames' cannot be empty")
            )

        if not vals.get('known_as'):
            raise ValidationError(
                _("The field 'known_as' cannot be empty")
            )

    _sql_constraints = [
        ('uk_document_identification',
         'unique(document_type, identification_id)',
         'You cannot have two users with the same identification number')
    ]


