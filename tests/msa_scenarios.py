"""Sample answer sets for the California MSA interview.

Each function returns a dict of interview variables as docassemble
would hold them after a complete run, before any code block runs.
"""
import da_stub
from da_stub import DADict, DAList, Individual, as_date

da_stub.install()

from docassemble.cphda import msa_util as m  # noqa: E402


def person(first, last, middle=''):
    p = Individual()
    p.name.first = first
    p.name.middle = middle
    p.name.last = last
    return p


def base():
    """Answers shared by every scenario."""
    a = dict(
        intro_seen=True,
        case_county='Los Angeles',
        case_filed=True,
        case_number='25STFL01234',
        service_date=as_date('2026-03-02'),
        doc_format='standalone',
        party_reference='roles',
        marriage_date=as_date('2012-06-16'),
        separation_date=as_date('2025-11-01'),
        dos_compromise=False,
        pet_has_counsel=True,
        pet_counsel_name='Dana Lee',
        pet_counsel_sbn='123456',
        pet_counsel_firm='CPH Law',
        resp_has_counsel=True,
        resp_counsel_name='Sam Ortiz',
        resp_counsel_sbn='234567',
        resp_counsel_firm='',
        translation_needed=False,
        translator_name='',
        case_reviewed=True,
        has_minor_children=False,
        pregnancy=False,
        ss_type='reserve',
        support_arrears=False,
        assets_status='none',
        debts_status='none',
        property_summary_reviewed=True,
        tax_filing_current='separate',
        prior_tax_split='responsible',
        filed_joint=True,
        atty_fees='own',
        enforcement_fees=True,
        pet_restore_name=False,
        resp_restore_name=False,
        spouse_coverage=True,
        own_insurance=True,
        dispute_resolution='mediation',
        additional_terms='',
        fl144_waiver=False,
        pet_prelim_served=True,
        pet_prelim_date=as_date('2026-04-01'),
        resp_prelim_served=True,
        resp_prelim_date=as_date('2026-04-15'),
        final_disclosures='exchanged',
        notarize=False,
        blank_sign_dates=True,
        review_done=True,
    )
    a['petitioner'] = person('Maria', 'Gomez', 'Elena')
    a['respondent'] = person('David', 'Gomez')
    contact = person('', '')
    contact.address.address = '350 S. Grand Ave., Suite 1200'
    contact.address.city = 'Los Angeles'
    contact.address.state = 'CA'
    contact.address.zip = '90071'
    contact.phone_number = '(213) 555-0100'
    contact.email = 'dlee@example.com'
    a['caption_contact'] = contact
    a['children'] = DAList()
    a['sec'] = m.SectionCounter()
    return a


def full_case():
    """Children, house buyout, QDRO, below-guideline support, Richmond spousal support."""
    a = base()
    kid1 = person('Lucia', 'Gomez')
    kid1.birthdate = as_date('2015-02-10')
    kid1.complete = True
    kid2 = person('Mateo', 'Gomez')
    kid2.birthdate = as_date('2018-09-03')
    kid2.complete = True
    a['children'] = DAList([kid1, kid2])
    a.update(
        has_minor_children=True,
        doc_format='attachment',
        dos_compromise=True,
        translation_needed=True,
        translation_language='Spanish',
        translator_name='Ana Ruiz',
        legal_custody='joint',
        physical_custody='primary_pet',
        pet_timeshare=70,
        uccjea_ok=True,
        habitual_residence='United States of America',
        parenting_schedule='eow_midweek',
        secondary_parent='resp',
        weekend_start='Friday after school',
        weekend_end='Sunday at 6:00 p.m.',
        midweek_text='every Wednesday from after school until 7:30 p.m.',
        exchange_location='curbside at the receiving parent\'s residence',
        exchange_notes='',
        holiday_plan='alternate',
        odd_year_thanksgiving='pet',
        parent_days=True,
        summer_weeks=2,
        summer_notice_days=60,
        right_first_refusal=True,
        rfr_hours=4,
        international_travel='consent',
        passport_holder='pet',
        coparent_method='app',
        coparent_app='OurFamilyWizard',
        child_contact=True,
        public_assistance=False,
        lcsa_involved=False,
        pet_gross_income=6500.0,
        resp_gross_income=9800.0,
        guideline_payor='resp',
        guideline_cs=1850.0,
        cs_follow_guideline=False,
        agreed_payor='resp',
        agreed_cs=1600.0,
        cs_start_date=as_date('2026-11-01'),
        cs_schedule='semi_monthly',
        cs_deviation_ack=DADict(informed=True, no_coercion=True, best_interest=True, needs_met=True, not_assigned=True),
        cs_deviation_reason='Respondent will pay the children\'s private school tuition directly.',
        addon_split='proportional',
        extracurricular_shared=True,
        health_ins_provider='resp',
        dependency_plan='alternate',
        dependency_alt_start=2026,
        cs_life_insurance=True,
        cs_life_amount=250000.0,
        wage_assignment='stay',
        children_reviewed=True,
        ss_type='pay',
        ss_payor='resp',
        ss_amount=1200.0,
        ss_start_date=as_date('2026-11-01'),
        ss_end_type='richmond',
        ss_end_date=as_date('2031-10-31'),
        ss_stepdown='',
        ss_modifiable=True,
        ss_terminate_remarriage=True,
        ss_life_insurance=True,
        ss_life_amount=100000.0,
        ss_cohabitation=True,
        support_arrears=True,
        arrears_terms='Respondent owes $2,400 in temporary spousal support through September 30, 2026, to be paid within 60 days.',
        spousal_reviewed=True,
        assets_status='some',
        pet_property_text=('1. The real property commonly known as 123 Main Street, Los Angeles, CA 90012 (APN 5123-004-012)\n'
                           '2. 2021 Toyota RAV4 (VIN ending 4821)\n\n'
                           '- Schwab savings account ending in 2222\n'
                           'One-half of the Chase checking account ending in 1111\n'
                           'The family dog, Luna'),
        resp_property_text=('2019 Ford F-150\n'
                            'Gomez Landscaping LLC, including its goodwill, assets, and accounts receivable\n'
                            'All of the community interest in the Acme Corp. 401(k) Plan, subject to a QDRO awarding Petitioner one-half of it.'),
        debts_status='some',
        pet_debts_text='Navient student loan\nOne-half of the Discover credit card balance',
        resp_debts_text='Capital One credit card ending in 9988',
        fl144_waiver=True,
        notarize=True,
        pet_restore_name=True,
        pet_former_name='Maria Elena Torres',
        atty_fees='resp_pays',
        atty_fees_amount=7500.0,
        atty_fees_due_days=30,
        additional_terms='Respondent will return the family photo albums within 30 days.\n\nEach party may attend school events.',
    )
    return a


def rdp_sale_waiver():
    """Domestic partners, no children, pregnancy, house sold, support waived, unequal division."""
    a = base()
    a.update(
        relationship_type='rdp',
        proceeding_type='dissolution',
        case_filed=False,
        party_reference='first',
        pet_has_counsel=False,
        resp_has_counsel=False,
        pregnancy=True,
        marriage_date=as_date('2021-01-10'),
        ss_type='waive',
        ss_waiver_ack=DADict(permanent=True, no_jurisdiction=True, considered=True, counsel=True),
        assets_status='some',
        pet_property_text='',
        resp_property_text='9 Ocean View Dr., Long Beach, CA 90802\nBank of America checking account',
        debts_status='some',
        pet_debts_text='',
        resp_debts_text='Amex credit card',
        tax_filing_current='joint_option',
        prior_tax_split='equal',
        dispute_resolution='court',
        spouse_coverage=False,
        own_insurance=False,
        final_disclosures='pending',
        resp_prelim_served=False,
        blank_sign_dates=False,
        resp_restore_name=True,
        resp_former_name='David Chen',
    )
    return a


def bare_minimum():
    """No children, no assets, support reserved, custom party labels."""
    a = base()
    a.update(
        party_reference='custom',
        pet_custom_ref='Wife',
        resp_custom_ref='Husband',
        pet_has_counsel=False,
        doc_format='attachment',
        filed_joint=False,
        enforcement_fees=False,
        pet_prelim_served=False,
        final_disclosures='pending',
    )
    return a


def long_marriage_pay():
    """Long marriage, fixed-term non-modifiable support with jurisdiction terminated, custody variants."""
    a = full_case()
    a.update(
        marriage_date=as_date('2005-05-05'),
        legal_custody='sole_resp',
        physical_custody='sole_resp',
        parenting_schedule='supervised',
        secondary_parent='pet',
        supervision_terms='Visits supervised by a professional provider for 4 hours each Saturday.',
        holiday_plan='custom',
        holiday_custom='Holidays per agreement of the parties.',
        summer_weeks=0,
        right_first_refusal=False,
        passport_holder='none',
        coparent_method='text_email',
        international_travel='prohibited',
        guideline_payor='pet',
        guideline_cs=900.0,
        cs_follow_guideline=True,
        cs_schedule='monthly',
        addon_split='custom',
        addon_pet_pct=40,
        dependency_plan='custom',
        dependency_custom='Respondent claims both children every year.',
        cs_life_insurance=False,
        wage_assignment='serve',
        public_assistance=True,
        lcsa_involved=True,
        ss_payor='pet',
        ss_end_type='months',
        ss_months=48,
        ss_jurisdiction_after='terminate',
        ss_modifiable=False,
        ss_terminate_remarriage=False,
        ss_life_insurance=False,
        ss_stepdown='Beginning November 1, 2028, support reduces to $800 per month.',
        atty_fees='pet_pays',
    )
    return a


SCENARIOS = {
    'full_case': full_case,
    'rdp_sale_waiver': rdp_sale_waiver,
    'bare_minimum': bare_minimum,
    'long_marriage_pay': long_marriage_pay,
}
