from datetime import datetime, timedelta
from odoo.tests.common import TransactionCase, tagged
from odoo.exceptions import ValidationError
from odoo.fields import Date


@tagged('-standard', 'hr_recruitment_bank_resumes')
class TestHrRecruitmentBankResumesRequestBase(TransactionCase):

    def setUp(self):
        super(TestHrRecruitmentBankResumesRequestBase, self).setUp()
        self.hr_bank_resumes = self.env['hr.recruitment.bank.resumes']
        self.hr_job = self.env['hr.job']

        self.job = self.hr_job.create({
            "name": "Job Test"
        })

        self.bank_resumes = self.hr_bank_resumes.create({
            "name": "John Doe",  # nombre
            "vacant": self.job.id,  # vacante hr.job
            "email": "abc@abc.com",  # correo Electrónico
            "contact_phone": '033020024534',  # teléfono de Contacto
            "linkedin": "abcLinkedin",  # linkedin
            "laboral_experience": "without_exp",  # experiencia Laboral
            "english_level": "medium",  # nivel de Ingles
            "studies": "technologist",  # estudios
            "salary_aspiration": 4000000,  # aspiración Salarial
            "technologies": "javascript",  # tecnologías
            "availability": "inmediata"  # disponibilidad
        })
