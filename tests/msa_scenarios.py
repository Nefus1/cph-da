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


def item(cls, **attrs):
    obj = cls()
    for key, val in attrs.items():
        setattr(obj, key, val)
    obj.complete = True
    return obj


def base():
    """Answers shared by every scenario."""
    a = dict(
        intro_seen=True,
        preparer_role='atty_pet',
        relationship_type='marriage',
        proceeding_type='dissolution',
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
        household_goods='possession',
        reimbursement_waivers=DADict(epstein=True, watts=True, s2640=False, other=True),
        reimbursement_exceptions='',
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
        merge_judgment='merge',
        binding_without_judgment=True,
        additional_terms='',
        pet_prelim_served=True,
        pet_prelim_date=as_date('2026-04-01'),
        resp_prelim_served=True,
        resp_prelim_date=as_date('2026-04-15'),
        final_disclosures='exchanged',
        ied_exchanged=True,
        notarize=False,
        blank_sign_dates=True,
        review_done=True,
    )
    a['petitioner'] = person('Maria', 'Gomez', 'Elena')
    a['respondent'] = person('David', 'Gomez')
    prep = person('Dana', 'Lee')
    prep.address.address = '350 S. Grand Ave., Suite 1200'
    prep.address.city = 'Los Angeles'
    prep.address.state = 'CA'
    prep.address.zip = '90071'
    prep.phone_number = '(213) 555-0100'
    prep.email = 'dlee@example.com'
    a['preparer'] = prep
    a['preparer_sbn'] = '123456'
    a['preparer_firm'] = 'CPH Law'
    for name in ('children', 'real_property', 'vehicles', 'accounts', 'retirement_plans',
                 'businesses', 'other_assets', 'debts'):
        a[name] = DAList()
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
        arrears_terms='Respondent owes $2,400 in temporary spousal support through September 30, 2026, to be paid from the equalizing payment.',
        spousal_reviewed=True,
        eq_approach='pay',
        eq_payment_method='lump',
        eq_due_days=30,
        eq_interest=True,
        final_disclosures='waived',
        notarize=True,
        pet_restore_name=True,
        pet_former_name='Maria Elena Torres',
        atty_fees='resp_pays',
        atty_fees_amount=7500.0,
        atty_fees_due_days=30,
        additional_terms='Respondent will return the family photo albums within 30 days.\n\nEach party may attend school events.',
    )
    a['real_property'] = DAList([item(
        m.RealProperty, description='123 Main Street\nLos Angeles, CA 90012', apn='5123-004-012',
        vesting='Husband and wife as community property', value=950000.0, encumbrance=520000.0,
        lenders='Wells Fargo', character='community', disposition='pet', refinance_days=180,
        refi_fallback='sell', deed_days=30)])
    a['vehicles'] = DAList([
        item(m.Vehicle, description='2021 Toyota RAV4', vin_last4='4821', value=24000.0, encumbrance=8000.0,
             character='community', awarded_to='pet'),
        item(m.Vehicle, description='2019 Ford F-150', vin_last4='', value=28000.0, encumbrance=0.0,
             character='community', awarded_to='resp'),
    ])
    a['accounts'] = DAList([
        item(m.FinancialAccount, description='Chase', account_type='checking', last4='1111', value=12000.0,
             value_date=None, character='community', awarded_to='split'),
        item(m.FinancialAccount, description='Fidelity', account_type='brokerage', last4='', value=40000.0,
             value_date=None, character='mixed', community_portion=25000.0, awarded_to='resp'),
        item(m.FinancialAccount, description='Schwab', account_type='savings', last4='2222', value=15000.0,
             value_date=None, character='sp_pet'),
    ])
    a['retirement_plans'] = DAList([
        item(m.RetirementPlan, description='Acme Corp. 401(k) Plan', plan_type='dc', participant='resp',
             character='mixed', value=180000.0, community_portion=150000.0, division='qdro',
             order_preparer='specialist', order_cost='equal'),
        item(m.RetirementPlan, description='CalPERS', plan_type='calpers', participant='pet',
             character='community', value=0.0, division='qdro', order_preparer='pet', order_cost='participant',
             survivor_benefit=True),
        item(m.RetirementPlan, description='Vanguard IRA', plan_type='ira', participant='pet',
             character='community', value=30000.0, division='qdro'),
    ])
    a['businesses'] = DAList([item(
        m.BusinessInterest, description='Gomez Landscaping LLC', entity_type='llc', ownership_pct=100.0,
        value=60000.0, character='community', awarded_to='resp')])
    a['other_assets'] = DAList([item(
        m.OtherAsset, description='Family dog, Luna', value=0.0, character='community', awarded_to='pet')])
    a['debts'] = DAList([
        item(m.Debt, description='Capital One', debt_type='credit_card', last4='9988', value=6500.0,
             character='community', assigned_to='resp'),
        item(m.Debt, description='Discover', debt_type='credit_card', last4='', value=3000.0,
             character='community', assigned_to='split'),
        item(m.Debt, description='Navient', debt_type='student', last4='', value=22000.0, character='sp_pet'),
    ])
    return a


def rdp_sale_waiver():
    """Domestic partners, no children, pregnancy, house sold, support waived, unequal division."""
    a = base()
    a.update(
        relationship_type='rdp',
        preparer_role='mediator',
        case_filed=False,
        party_reference='first',
        pet_has_counsel=False,
        resp_has_counsel=False,
        pregnancy=True,
        marriage_date=as_date('2021-01-10'),
        ss_type='waive',
        ss_waiver_ack=DADict(permanent=True, no_jurisdiction=True, considered=True, counsel=True),
        eq_approach='waive',
        eq_custom_reason='Respondent receives the larger share in exchange for the support waiver',
        household_goods='list',
        household_goods_list='To Maria: the piano.\nTo David: the sofa.',
        reimbursement_waivers=DADict(epstein=False, watts=False, s2640=False, other=False),
        reimbursement_exceptions='Respondent receives a $5,000 Section 2640 reimbursement.',
        tax_filing_current='joint_option',
        prior_tax_split='equal',
        dispute_resolution='court',
        merge_judgment='no_merge',
        binding_without_judgment=False,
        spouse_coverage=False,
        own_insurance=False,
        final_disclosures='pending',
        resp_prelim_served=False,
        ied_exchanged=False,
        blank_sign_dates=False,
        resp_restore_name=True,
        resp_former_name='David Chen',
    )
    a['real_property'] = DAList([item(
        m.RealProperty, description='9 Ocean View Dr., Long Beach, CA 90802', apn='', vesting='',
        value=700000.0, encumbrance=400000.0, lenders='', character='community', disposition='sell',
        list_days=60, agent='joint', occupant='resp', carrying_costs='reimbursed', price_terms='')])
    a['accounts'] = DAList([item(
        m.FinancialAccount, description='Bank of America', account_type='checking', last4='', value=30000.0,
        value_date=None, character='community', awarded_to='resp')])
    a['debts'] = DAList([item(
        m.Debt, description='Amex', debt_type='credit_card', last4='', value=2000.0, character='sp_resp')])
    return a


def bare_minimum():
    """No children, no assets, support reserved, custom party labels."""
    a = base()
    a.update(
        party_reference='custom',
        pet_custom_ref='Wife',
        resp_custom_ref='Husband',
        preparer_role='atty_resp',
        pet_has_counsel=False,
        filed_joint=False,
        enforcement_fees=False,
        pet_prelim_served=False,
        final_disclosures='pending',
    )
    a['reimbursement_waivers'] = DADict(epstein=False, watts=False, s2640=False, other=False)
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
        eq_approach='custom',
        eq_custom_amount=10000.0,
        eq_custom_payor='pet',
        eq_custom_reason='the parties agree to offset the Watts charges',
        eq_payment_method='installments',
        eq_installments='$1,000 per month beginning January 1, 2027.',
        eq_interest=False,
        atty_fees='pet_pays',
    )
    a['real_property'][0].disposition = 'resp'
    a['real_property'][0].refinance_days = 0
    a['real_property'][0].refi_fallback = 'court'
    return a


SCENARIOS = {
    'full_case': full_case,
    'rdp_sale_waiver': rdp_sale_waiver,
    'bare_minimum': bare_minimum,
    'long_marriage_pay': long_marriage_pay,
}
