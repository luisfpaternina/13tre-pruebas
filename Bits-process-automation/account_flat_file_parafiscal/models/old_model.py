
"""
    # Fields to the file's header
    header_record_type = fields.Char(
        required=True, size=2, default='01')
    header_template_modality = fields.Selection([
        ('0', '0'),
        ('1', '1'),
        ('2', '2')
    ], required=True, default='0')
    header_sequence = fields.Char(
        required=True, size=4, default='0001')
    header_company_name_taxpayer = fields.Char(
        required=True, size=200)
    header_type_document_taxpayer = fields.Selection([
        ('ni', 'NI'),
        ('cc', 'CC'),
        ('ce', 'CE'),
        ('ti', 'TI'),
        ('pa', 'PA'),
        ('cd', 'CD'),
        ('sc', 'SC')
    ],required=True, default="NI")
    header_identifiacion_number_taxpayer = fields.Char(
        required=True, size=16, default="900207800")
    header_taxpayer_verification_digit = fields.Char(
        required=True, size=1, default='0')
    header_template_type = fields.Selection([
        ('e', 'E'),
        ('y', 'Y'),
        ('a', 'A'),
        ('i', 'I'),
        ('s', 'S'),
        ('m', 'M'),
        ('n', 'N'),
        ('h', 'H'),
        ('t', 'T'),
        ('f', 'F'),
        ('j', 'J'),
        ('x', 'X'),
        ('k', 'K')
    ], required=True, default="E")
    header_template_association_number = fields.Char(
        required=True, size=10)
    header_pay_date_association_template = fields.Date()
    header_form_presentation = fields.Selection([
        ('u', 'U'),
        ('s', 'S')
    ], required=True, default="U")
    header_taxpayer_branch_code = fields.Char(
        required=True, size=10)
    header_branch_name = fields.Char(
        required=True, size=40)
    header_taxpayer_arl_code = fields.Char(
        required=True, size=6)
    #Date(aaaa-mm)
    header_pay_period_other_than_health = Char(
        required=True, size=7)
    #Date(aaaa-(mm+1))
    header_pay_period_health = fields.Char(
        required=True, size=7)
    #Valor unico y automatico generado por el sistema
    header_contribution_settlement_filing_number = fields.Char(
        required=True, size=10)
    header_pay_date = fields.Char(
        required=True, size=10)
    header_total_number_employees = fields.Char(
        required=True, size=5)
    header_payroll_total_value = fields.Char(
        required=True, size=12)
    header_taxpayer_type = fields.Selection([
        ('01', '01'),
        ('02', '02'),
        ('03', '03'),
        ('04', '04'),
        ('05', '05'),
        ('06', '06'),
        ('07', '07'),
        ('08', '08'),
        ('09', '09')
    ], required=True, default='01')
    header_informacion_operator_code = fields.Char(
        required=True, size=2, default='00')

    #Fields to the file's report
    report_record_type = fields.Char(
        required=True, size=2)
    report_sequence = fields.Char(
        required=True, size=5)
    report_type_document_contributor = fields.Selection([
        ('cc', 'CC'),
        ('ce', 'CE'),
        ('ti', 'TI'),
        ('pa', 'PA'),
        ('cd', 'CD'),
        ('sc', 'SC'),
        ('rc', 'RC')
    ], required=True)
    #Falta validacion de numeros y caracteres
    report_identification_number_contributor = Char(
        required=True, size=16)
    report_contributor_type = fields.Selection([
        ('1', '1'),
        ('12', '12'),
        ('19', '19')
    ], required=True)
    report_contributor_subtype = fields.Char(
        required=True, size=2)
    report_foreigner_not_obliget_contribute_pensions = fields.Char(
        required=True, size=1)
    report_colombian_abroad = fields.Char(
        required=True, size=1)
    report_code_department_work_location = fields.Char(
        required=True, size=2)
    #Field 10
    report_code_municipality_work_location = fields.Char(
        required=True, size=3)
    report_first_lastname = fields.Char(
        required=True, size=20)
    report_second_lastname = fields.Char(
        required=True, size=30)
    report_first_name = fields.Char(
        required=True, size=20)
    report_second_name = fields.Char(
        required=True, size=30)
    report_ING = fields.Selection([
        ('none', ' '),
        ('r', 'R'),
        ('x', 'X'),
        ('c', 'C')
    ],required=True)
    report_RET = fields.Selection([
        ('none', ' '),
        ('p', 'P'),
        ('r', 'R'),
        ('x', 'X'),
        ('c', 'C')
    ], required=True)
    report_TDE = fields.Selection([
        ('none', ' '),
        ('x', 'X')
    ], required=True)
    report_TAE = fields.Selection([
        ('none', ' '),
        ('x', 'X')
    ], required=True)
    report_TDP = fields.Selection([
        ('none', ' '),
        ('x', 'X')
    ], required=True)
    #Field 20
    report_TAP = fields.Selection([
        ('none', ' '),
        ('x', 'X')
    ], required=True)
    report_VSP = fields.Selection([
        ('none', ' '),
        ('x', 'X')
    ], required=True)
    report_corrections = fields.Selection([
        ('none', ' '),
        ('x', 'X'),
        ('c', 'C')
    ], required=True)
    report_VST = fields.Selection([
        ('none', ' '),
        ('x', 'X')
    ], required=True)
    report_SLN = fields.Selection([
        ('none', ' '),
        ('x', 'X'),
        ('c', 'C')
    ], required=True)
    report_IGE = fields.Selection([
        ('none', ' '),
        ('x', 'X')
    ], required=True)
    report_VAC = fields.Selection([
        ('none', ' '),
        ('x', 'X'),
        ('l', 'L'),
    ], required=True)
    report_AVP = fields.Selection([
        ('none', ' '),
        ('x', 'X')
    ], required=True)
    report_VCT = fields.Selection([
        ('none', ' '),
        ('x', 'X')
    ], required=True)
    report_IRL = fields.Char(
        required=True, size=2)
    # Fied 30
    report_pension_fund_administrator_code_affiliate_belongs = fields.Char(
        required=True, size=6)
    report_pension_fund_administrator_code_affiliate_moves = fields.Char(
        required=True, size=6)
    report_health_code_affiliate_belongs = fields.Char(
        required=True, size=6)
    report_health_code_affiliate_move = fields.Char(
        required=True, size=6)
    report_CCF_code_affiliate_belongs = fields.Char(
        required=True, size=6)
    report_number_days_quoted_pension = fields.Char(
        required=True, size=2)
    report_number_days_quoted_health = fields.Char(
        required=True, size=2)
    report_number_days_quoted_arl = fields.Char(
        required=True, size=2)
    report_number_days_quoted_family_compensation_box = fields.Char(
        required=True, size=2)
    report_basic_salary = fields.Char(
        required=True, size=9)
    # Field 40
    report_integral_salary = fields.Char(
        required=True, size=1)
    report_IBC_pension = fields.Char(
        required=True, size=9)
    report_IBC_health = fields.Char(
        required=True, size=9)
    report_IBC_arl = fields.Char(
        required=True, size=9)
    report_IBC_CCF = fields.Char(
        required=True, size=9)
    report_pension_contribution_rate = fields.Char(
        required=True, size=7)
    report_mandatory_quote_pension = fields.Char(
        required=True, size=9)
    report_voluntary_con_affiliate_mandatory_pension_fund = fields.Char(
        required=True, size=9)
    report_voluntary_con_contributor_mandatory_pension_fund = fields.Char(
        required=True, size=9)
    report_total_con_general_pension_system = fields.Char(
        required=True, size=9)
    # Field 50
    report_con_pension_solidarity_fund_solidarity_subaccount = fields.Char(
        required=True, size=9)
    report_con_pension_solidarity_fund_subsistence_subaccount = fields.Char(
        required=True, size=9)
    report_value_not_retained_voluntary_contributions = fields.Char(
        required=True, size=9)
    report_health_contribution_rate = fields.Char(
        required=True, size=7)
    report_mandatory_health_contribution = fields.Char(
        required=True, size=9)
    report_additional_UPC_value = fields.Char(
        required=True, size=9)
    report_authorization_number_disability_due_general_illness = fields.Char(
        required=True, size=15)
    report_value__disability_due_general_illness = fields.Char(
    required=True, size=9)
    report_maternity_paternity_leave_authorization_number = fields.Char(
        required=True, size=15)
    report_value_maternity_leave = fields.Char(
        required=True, size=9)
    # Field 60
    report_arl_contribution_rate = fields.Char(
        required=True, size=9)
    report_CT_work_center = fields.Char(
        required=True, size=9)
    report_mandatory_con_general_system_occupational_risk = fields.Char(
        required=True, size=9)
    report_CCF_contribution_rate = fields.Char(
        required=True, size=7)
    report_CCF_contribution_value_provided_contributor = fields.Char(
        required=True, size=9)
    report_SENA_contribution_rate = fields.Char(
        required=True, size=7)
    report_SENA_contributions_value = fields.Char(
        required=True, size=9)
    report_ICBF_contributions_rate = fields.Char(
        required=True, size=7)
    report_ICBF_contribution_value = fields.Char(
        required=True, size=9)
    report_ESAP_contributions_rate = fields.Char(
        required=True, size=7)
    # Field 70
    report_ESAP_contribution_value = fields.Char(
        required=True, size=9)
    report_MEN_contribution_rate_provided_contributor = fields.Char(
        required=True, size=7)
    report_contribution_value_MEN_provided_contributor = fields.Char(
        required=True, size=9)
    report_document_type_main_contributor = fields.Selection([
        ('cc', 'CC'),
        ('ce', 'CE'),
        ('ti', 'TI'),
        ('pa', 'PA'),
        ('cd', 'CD'),
        ('sc', 'SC')
    ],required=True)
    report_identification_number_main_contributor = fields.Char(
        required=True, size=16)
    report_exonerated_contributor_payment_con_health_SENA_ICBF = fields.Char(
        required=True, size=1)
    code_occupational_risk_manager_which_affiliate_belongs = fields.Char(
        required=True, size=6)
    report_risk_class_affiliate_is_in = fields.Char(
        required=True, size=1)
    report_pension_special_rate_indicator = fields.Char(
        required=True, size=1)
    # Todos los campos tipo Date deben tener una long min-max de 10
    report_date_admission = fields.Date(
        required=True)
    # Field 80
    report_retirement_date = fields.Date(
        required=True)
    report_VSP_start_date = fields.Date(
        required=True)
    report_SLN_start_date = fields.Date(
        required=True)
    report_SLN_end_date = fields.Date(
        required=True)
    report_IGE_start_date = fields.Date(
        required=True)
    report_IGE_end_date = fields.Date(
        required=True)
    report_LMA_start_date = fields.Date(
        required=True)
    report_end_date_AML = fields.Date(
        required=True)
    report_start_date_VAC_LR = fields.Date(
        required=True)
    report_end_date_VAC_LR = fields.Date(
        required=True)
    # Field 90
    report_VCT_start_date = fields.Date(
        required=True)
    report_end_date_VCT = fields.Date(
        required=True)
    report_IRL_start_date = fields.Date(
        required=True)
    report_IRL_end_date = fields.Date(
        required=True)
    report_IBC_other_parafiscales_other_than_CCF = fields.Char(
        required=True, size=9)
    report_number_hours_worked = fields.Char(
        required=True, size=3)
"""
