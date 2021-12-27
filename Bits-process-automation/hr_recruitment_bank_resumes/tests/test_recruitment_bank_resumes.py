from datetime import date
from odoo.addons.hr_recruitment_bank_resumes.tests.common\
    import TestHrRecruitmentBankResumesRequestBase
from odoo.exceptions import UserError, ValidationError


class TestHrRecruitmentBankResumes (TestHrRecruitmentBankResumesRequestBase):

    def setUp(self):
        super(TestHrRecruitmentBankResumes, self).setUp()

    def test_validate_data(self):
        self.bank_resumes._validate_data()

    def test_error_email(self):
        with self.assertRaises(ValidationError):
            self.hr_bank_resumes.create({
                "name": "John Doe",  # nombre
                "vacant": self.job.id,  # vacante hr.job
                "email": "abc",  # correo Electrónico
                "contact_phone": 'abc',  # teléfono de Contacto
                "linkedin": "abcLinkedin",  # linkedin
                "laboral_experience": "without_exp",  # experiencia Laboral
                "english_level": "medium",  # nivel de Ingles
                "studies": "technologist",  # estudios
                "salary_aspiration": 4000000,  # aspiración Salarial
                "technologies": "javascript",  # tecnologías
                "availability": "inmediata"  # disponibilidad
            })

    def test_error_phone(self):
        with self.assertRaises(ValidationError):
            self.hr_bank_resumes.create({
                "name": "John Doe",  # nombre
                "vacant": self.job.id,  # vacante hr.job
                "email": "abc@abc.com",  # correo Electrónico
                "contact_phone": 'abc',  # teléfono de Contacto
                "linkedin": "abcLinkedin",  # linkedin
                "laboral_experience": "without_exp",  # experiencia Laboral
                "english_level": "medium",  # nivel de Ingles
                "studies": "technologist",  # estudios
                "salary_aspiration": 4000000,  # aspiración Salarial
                "technologies": "javascript",  # tecnologías
                "availability": "inmediata"  # disponibilidad
            })

    def test_error_without_email_phone(self):
        resume = self.hr_bank_resumes.create({
            "name": "John Doe",  # nombre
            "vacant": self.job.id,  # vacante hr.job
            "linkedin": "abcLinkedin",  # linkedin
            "laboral_experience": "without_exp",  # experiencia Laboral
            "english_level": "medium",  # nivel de Ingles
            "studies": "technologist",  # estudios
            "salary_aspiration": 4000000,  # aspiración Salarial
            "technologies": "javascript",  # tecnologías
            "availability": "inmediata"  # disponibilidad
        })
        resume._validate_data()
