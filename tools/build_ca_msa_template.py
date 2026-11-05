#!/usr/bin/env python3
"""Build docassemble/cphda/data/templates/ca_msa.docx.

The MSA template is generated from this script so the clause text is
reviewable in version control and every Jinja2 tag is guaranteed to sit
in a single Word run. Edit the text here, then run:

    python3 tools/build_ca_msa_template.py

House style: Times New Roman 12 pt, justified, no line numbers (the
firm's pleading paper supplies them when needed).
"""
import os

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt

OUT = os.path.join(os.path.dirname(__file__), '..', 'docassemble', 'cphda', 'data', 'templates', 'ca_msa.docx')

P = '{{ petitioner.ref }}'
R = '{{ respondent.ref }}'
FONT = 'Times New Roman'

doc = Document()


# --------------------------------------------------------------- styles
def setup_styles():
    normal = doc.styles['Normal']
    normal.font.name = FONT
    normal.font.size = Pt(12)
    normal.element.rPr.rFonts.set(qn('w:eastAsia'), FONT)
    pf = normal.paragraph_format
    pf.space_before = Pt(0)
    pf.space_after = Pt(12)
    pf.line_spacing = 1.0
    for section in doc.sections:
        section.top_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1)
        section.right_margin = Inches(1)


def _run(par, text, bold=False, italic=False, underline=False):
    run = par.add_run(text)
    run.bold = bold
    run.italic = italic
    run.underline = underline
    run.font.name = FONT
    run.font.size = Pt(12)
    return run


def ctl(tag):
    """A docxtpl paragraph-level control tag on its own paragraph."""
    par = doc.add_paragraph()
    par.paragraph_format.space_after = Pt(0)
    _run(par, tag)
    return par


def text(body, align='justify', indent=0.0, first=0.0, bold=False, space_after=12, keep=False):
    par = doc.add_paragraph()
    par.alignment = {'justify': WD_ALIGN_PARAGRAPH.JUSTIFY, 'center': WD_ALIGN_PARAGRAPH.CENTER,
                     'left': WD_ALIGN_PARAGRAPH.LEFT, 'right': WD_ALIGN_PARAGRAPH.RIGHT}[align]
    fmt = par.paragraph_format
    fmt.left_indent = Inches(indent)
    fmt.first_line_indent = Inches(first)
    fmt.space_after = Pt(space_after)
    fmt.keep_with_next = keep
    _run(par, body, bold=bold)
    return par


def article(title):
    par = doc.add_paragraph()
    par.alignment = WD_ALIGN_PARAGRAPH.CENTER
    par.paragraph_format.space_before = Pt(12)
    par.paragraph_format.keep_with_next = True
    _run(par, 'ARTICLE {{ sec.article() }}', bold=True)
    par.add_run().add_break()
    _run(par, title, bold=True)
    return par


def para(heading, body):
    """Numbered paragraph: bold "N.N  Heading." followed by the body."""
    par = doc.add_paragraph()
    par.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    par.paragraph_format.first_line_indent = Inches(0.5)
    _run(par, '{{ sec.para() }}\t' + heading + '. ', bold=True)
    _run(par, body)
    return par


def item(body):
    """Indented list item inside a {%p for %} loop."""
    return text(body, indent=1.0, first=-0.5, space_after=6)


def loop(var, seq, body):
    ctl('{%p for ' + var + ' in ' + seq + ' %}')
    item('({{ loop.index }})\t' + body)
    ctl('{%p endfor %}')


def page_break():
    par = doc.add_paragraph()
    par.add_run().add_break(WD_BREAK.PAGE)


def blank():
    text('', space_after=0)


def field(par, code):
    run = par.add_run()
    run.font.name = FONT
    run.font.size = Pt(10)
    fld = OxmlElement('w:fldSimple')
    fld.set(qn('w:instr'), code)
    r = OxmlElement('w:r')
    t = OxmlElement('w:t')
    t.text = '1'
    r.append(t)
    fld.append(r)
    run._r.addnext(fld)


def footer():
    ftr = doc.sections[0].footer
    par = ftr.paragraphs[0]
    par.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = par.add_run('{{ agreement_title | title }} - Page ')
    run.font.name = FONT
    run.font.size = Pt(10)
    field(par, 'PAGE')


def signature(name_expr, role):
    text('Dated: {{ "____________________" if blank_sign_dates else format_date(today()) }}', align='left', space_after=24, keep=True)
    text('______________________________________', align='left', space_after=0, keep=True)
    text(name_expr + ', ' + role, align='left', space_after=24)


def boxed(body):
    """Paragraph inside a single bordered cell, as on the statutory notary form."""
    tbl = doc.add_table(rows=1, cols=1)
    tbl.style = 'Table Grid'
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = tbl.rows[0].cells[0]
    cell.width = Inches(6.5)
    par = cell.paragraphs[0]
    par.alignment = WD_ALIGN_PARAGRAPH.LEFT
    par.paragraph_format.space_before = Pt(4)
    par.paragraph_format.space_after = Pt(4)
    _run(par, body)
    blank()
    return tbl


def notary(name_expr):
    text('CALIFORNIA ALL-PURPOSE ACKNOWLEDGMENT', align='center', bold=True)
    boxed('A notary public or other officer completing this certificate verifies only the identity of the individual who signed the document to which this certificate is attached, and not the truthfulness, accuracy, or validity of that document.')
    text('State of California\nCounty of ______________________', align='left')
    text('On ____________________ before me, ______________________________ (insert name and title of the officer), personally appeared ' + name_expr + ', who proved to me on the basis of satisfactory evidence to be the person(s) whose name(s) is/are subscribed to the within instrument and acknowledged to me that he/she/they executed the same in his/her/their authorized capacity(ies), and that by his/her/their signature(s) on the instrument the person(s), or the entity upon behalf of which the person(s) acted, executed the instrument.')
    text('I certify under PENALTY OF PERJURY under the laws of the State of California that the foregoing paragraph is true and correct.')
    text('WITNESS my hand and official seal.', align='left', space_after=36)
    text('Signature ______________________________          (Seal)', align='left')


# =============================================================== content
setup_styles()
footer()

# ---------------------------------------------------------- caption
ctl("{%p if doc_format == 'attachment' %}")
text('{{ caption_name }}{% if caption_sbn %} (SBN {{ caption_sbn }}){% endif %}', align='left', space_after=0)
ctl('{%p if caption_firm %}')
text('{{ caption_firm }}', align='left', space_after=0)
ctl('{%p endif %}')
text('{{ caption_contact.address.address }}', align='left', space_after=0)
text('{{ caption_contact.address.city }}, {{ caption_contact.address.state }} {{ caption_contact.address.zip }}', align='left', space_after=0)
text('Telephone: {{ caption_contact.phone_number }}', align='left', space_after=0)
ctl('{%p if caption_contact.email %}')
text('Email: {{ caption_contact.email }}', align='left', space_after=0)
ctl('{%p endif %}')
text('{{ caption_for }}', align='left', space_after=24)
text('SUPERIOR COURT OF CALIFORNIA', align='center', bold=True, space_after=0)
text('COUNTY OF {{ case_county | upper }}', align='center', bold=True, space_after=24)
cap = doc.add_table(rows=1, cols=2)
cap.style = 'Table Grid'
left, right = cap.rows[0].cells
left.width = Inches(3.5)
right.width = Inches(3.0)
lp = left.paragraphs[0]
_run(lp, "In re the {{ 'Domestic Partnership' if relationship_type == 'rdp' else 'Marriage' }} of:")
for line in ['', 'Petitioner: {{ petitioner.name.full() | upper }}', '', 'and', '', 'Respondent: {{ respondent.name.full() | upper }}']:
    left.add_paragraph().add_run(line)
rp = right.paragraphs[0]
_run(rp, "Case No.: {{ case_number if case_filed else '(to be assigned)' }}")
right.add_paragraph()
_run(right.add_paragraph(), '{{ agreement_title }}', bold=True)
right.add_paragraph().add_run('(Attachment to Judgment)')
blank()
ctl('{%p endif %}')

# ---------------------------------------------------------- title and preamble
text('{{ sec.reset() }}{{ agreement_title }}', align='center', bold=True, space_after=24)
text('This ' + "{{ agreement_title | title }}" + ' ("Agreement") is made by {{ petitioner }} ("' + P + '") and {{ respondent }} ("' + R + '"), referred to together as "the parties."', first=0.5)

# ---------------------------------------------------------- recitals
article('RECITALS')
para('{{ "Domestic Partnership" if relationship_type == "rdp" else "Marriage" }}',
     '{% if relationship_type == "rdp" %}The parties registered as domestic partners with the California Secretary of State on {{ format_date(marriage_date) }}.{% else %}The parties were married on {{ format_date(marriage_date) }}.{% endif %}')
para('Date of Separation',
     'The parties separated on {{ format_date(separation_date) }}. The parties stipulate that {{ format_date(separation_date) }} is their date of separation for all purposes{% if dos_compromise %}, and acknowledge that this date is a negotiated compromise of a disputed issue{% endif %}. The {{ marriage_word }} lasted {{ marriage_length_words }} from the date of {{ "registration" if relationship_type == "rdp" else "marriage" }} to the date of separation.')
ctl('{%p if has_minor_children %}')
para('Children',
     'The parties have {{ children | length }} minor {{ "child" if children | length == 1 else "children" }} together (the "children"):')
loop('child', 'children', '{{ child.name.full() }}, born {{ format_date(child.birthdate) }}')
ctl('{%p elif pregnancy %}')
para('Children',
     'The parties have no minor children together. The parties acknowledge that a pregnancy exists, and all issues of parentage, custody, visitation, and support concerning any child born as a result are reserved for later determination.')
ctl('{%p else %}')
para('Children',
     'The parties have no minor children together, none were adopted during the {{ marriage_word }}, and none are expected.')
ctl('{%p endif %}')
para('The Action',
     '{% if case_filed %}{{ petitioner }} filed a petition for {{ proceeding_words }} in the Superior Court of California, County of {{ case_county }}, Case No. {{ case_number }} (the "Action").{% else %}{{ petitioner }} intends to file a petition for {{ proceeding_words }} in the Superior Court of California, County of {{ case_county }} (the "Action").{% endif %}')
para('Purpose',
     'The parties intend this Agreement to be a final and complete settlement of all of their rights and obligations arising from the {{ marriage_word }}, including custody and support of any children, {{ "partner" if relationship_type == "rdp" else "spousal" }} support, the division of community and quasi-community property and debts, the confirmation of separate property and debts, and attorney\'s fees and costs, except as this Agreement expressly provides otherwise.')
para('Representation',
     '{% if pet_has_counsel %}' + P + ' has been represented in the negotiation of this Agreement by {{ pet_counsel_name }}{% if pet_counsel_firm %} of {{ pet_counsel_firm }}{% endif %}.{% else %}' + P + ' has not been represented by an attorney. ' + P + ' has been advised to obtain independent legal advice before signing this Agreement, has had a full opportunity to do so, and signs it voluntarily{% if resp_has_counsel %}, understanding that {{ resp_counsel_name }} represents only ' + R + '{% endif %}.{% endif %} '
     '{% if resp_has_counsel %}' + R + ' has been represented in the negotiation of this Agreement by {{ resp_counsel_name }}{% if resp_counsel_firm %} of {{ resp_counsel_firm }}{% endif %}.{% else %}' + R + ' has not been represented by an attorney. ' + R + ' has been advised to obtain independent legal advice before signing this Agreement, has had a full opportunity to do so, and signs it voluntarily{% if pet_has_counsel %}, understanding that {{ pet_counsel_name }} represents only ' + P + '{% endif %}.{% endif %}')
ctl('{%p if translation_needed %}')
para('Translation',
     'This Agreement was translated into {{ translation_language }}{% if translator_name %} by {{ translator_name }}{% endif %} before it was signed. The parties confirm that they read or had read to them the translated Agreement and understand its terms.')
ctl('{%p endif %}')

# ---------------------------------------------------------- custody
ctl('{%p if has_minor_children %}')
article('CHILD CUSTODY AND PARENTING TIME')
para('Jurisdiction',
     '{% if uccjea_ok %}California is the home state of the children, and the{% else %}The parties stipulate that the{% endif %} Superior Court of California, County of {{ case_county }}, has jurisdiction to make child custody orders under the Uniform Child Custody Jurisdiction and Enforcement Act (Family Code sections 3400 through 3465). The country of habitual residence of the children is {{ habitual_residence }}. The parties understand that a violation of the custody and parenting time orders in this Agreement may result in civil or criminal penalties, or both.')
para('Best Interest',
     'The parties agree that the custody and parenting time provisions of this Agreement are in the best interest of the children and assure them frequent and continuing contact with both parents (Family Code sections 3011 and 3020).')
para('Legal Custody',
     '{% if legal_custody == "joint" %}The parties shall share joint legal custody of the children. The parties shall confer and agree on all major decisions concerning the children\'s health, education, and welfare, including non-emergency medical, dental, and mental health treatment; choice of school and educational programs; religious upbringing; enrollment in long-term extracurricular activities; and applications for passports. Under Family Code section 3083, mutual consent is required only for the decisions listed in this paragraph; in all other matters, either parent acting alone may exercise legal control of the children while they are in that parent\'s care. Either parent may consent to emergency medical treatment, with notice to the other parent as soon as practical. If the parties cannot agree on a decision requiring mutual consent, either may ask the court to decide it.'
     '{% else %}{{ party_ref["pet" if legal_custody == "sole_pet" else "resp"] }} shall have sole legal custody of the children and the right to make decisions concerning their health, education, and welfare, and shall keep {{ party_ref["resp" if legal_custody == "sole_pet" else "pet"] }} reasonably informed of significant decisions.{% endif %}'
     ' Both parents shall have access to the children\'s school, medical, and dental records and information (Family Code section 3025).')
para('Physical Custody',
     '{% if physical_custody == "joint" %}The parties shall share joint physical custody of the children.'
     '{% elif physical_custody in ["primary_pet", "primary_resp"] %}The parties shall share joint physical custody of the children. The residence of {{ party_ref["pet" if physical_custody == "primary_pet" else "resp"] }} is the children\'s primary residence for school enrollment and all other purposes requiring a single residence.'
     '{% else %}{{ party_ref["pet" if physical_custody == "sole_pet" else "resp"] }} shall have sole physical custody of the children, subject to the parenting time of {{ party_ref["resp" if physical_custody == "sole_pet" else "pet"] }} stated in this Article.{% endif %}')
para('Regular Parenting Schedule',
     '{% if parenting_schedule == "alt_weeks" %}The children shall alternate weeks with each parent, with the exchange each {{ period(alt_week_exchange) }} The parties shall agree in writing on the start date of the rotation.'
     '{% elif parenting_schedule == "2255" %}The parties shall follow a 2-2-5-5 schedule: ' + P + ' shall have the children every Monday and Tuesday overnight, ' + R + ' shall have the children every Wednesday and Thursday overnight, and the parties shall alternate weekends from Friday after school until Monday return to school.'
     '{% elif parenting_schedule == "223" %}The parties shall follow a 2-2-3 schedule: in the first week, ' + P + ' shall have Monday and Tuesday, ' + R + ' shall have Wednesday and Thursday, and ' + P + ' shall have Friday through Sunday; in the following week the days reverse, and the rotation repeats.'
     '{% elif parenting_schedule in ["eow_midweek", "eow"] %}{{ party_ref["resp" if secondary_parent == "pet" else "pet"] }} shall have the children at all times not designated to {{ party_ref[secondary_parent] }}. {{ party_ref[secondary_parent] }} shall have the children on alternate weekends from {{ weekend_start }} until {% if parenting_schedule == "eow_midweek" %}{{ weekend_end }}, and {{ period(midweek_text) }}{% else %}{{ period(weekend_end) }}{% endif %}'
     '{% elif parenting_schedule == "supervised" %}The parenting time of {{ party_ref[secondary_parent] }} shall be supervised, as follows: {{ period(supervision_terms) }} {{ party_ref["resp" if secondary_parent == "pet" else "pet"] }} shall have the children at all other times.'
     '{% elif parenting_schedule == "custom" %}{{ custom_schedule | manual_line_breaks }}'
     '{% else %}The parties shall follow the parenting schedule in the {{ attached_plan_name }}, which is attached to this Agreement and incorporated by reference.{% endif %}')
para('Exchanges',
     'Unless the parties agree otherwise in writing, exchanges of the children shall take place {{ exchange_location }}, and the parent beginning their parenting time shall provide transportation.{% if exchange_notes %} {{ period(exchange_notes) }}{% endif %}')
para('Holidays and Vacations',
     '{% if holiday_plan == "alternate" %}Holiday time takes priority over the regular schedule. In odd-numbered years, {{ party_ref[odd_year_thanksgiving] }} shall have the children for Thanksgiving (from Wednesday after school until Sunday at 6:00 p.m.) and the first half of winter break, and {{ party_ref["resp" if odd_year_thanksgiving == "pet" else "pet"] }} shall have spring break and the second half of winter break. In even-numbered years, the schedule reverses. Winter break is divided at noon on its midpoint day.'
     '{% elif holiday_plan == "custom" %}{{ holiday_custom | manual_line_breaks }}'
     '{% else %}Holidays are governed by the attached parenting plan.{% endif %}'
     '{% if parent_days %} The children shall spend Mother\'s Day with their mother and Father\'s Day with their father, from 10:00 a.m. until 6:00 p.m.{% endif %}'
     '{% if summer_weeks %} Each parent may have up to {{ summer_weeks }} {{ "week" if summer_weeks == 1 else "weeks" }} of vacation time with the children each summer, not necessarily consecutive, by giving the other parent written notice of the selected dates at least {{ summer_notice_days }} days in advance. If selected dates conflict, ' + P + ' has priority in odd-numbered years and ' + R + ' in even-numbered years.{% endif %}')
ctl('{%p if right_first_refusal %}')
para('Right of First Refusal',
     'If a parent will be unable to care for the children personally for more than {{ rfr_hours }} hours during that parent\'s time, that parent shall first offer the time to the other parent before arranging other child care. The other parent shall respond promptly and shall provide transportation for the additional time.')
ctl('{%p endif %}')
para('Travel',
     'Either parent may travel with the children within the United States during that parent\'s time. A parent traveling overnight away from that parent\'s residence shall give the other parent an itinerary and contact information in advance. '
     '{% if international_travel == "consent" %}Travel outside the United States requires the prior written consent of the other parent, which shall not be unreasonably withheld, and a written itinerary.'
     '{% elif international_travel == "notice" %}A parent may travel outside the United States with the children after giving the other parent at least 30 days\' written notice and a written itinerary.'
     '{% else %}Neither parent shall take the children outside the United States without a court order.{% endif %}'
     '{% if passport_holder != "none" %} {{ party_ref[passport_holder] }} shall hold the children\'s passports and shall make them available to the other parent for authorized travel.{% endif %}')
para('Communication',
     'The parents shall communicate about the children {% if coparent_method == "app" %}through {{ coparent_app }}, except in an emergency, with each parent paying their own subscription cost{% else %}by text message and email, except in an emergency{% endif %}, and shall keep communications civil and focused on the children. Neither parent shall make disparaging remarks about the other in the children\'s presence or use the children to carry messages.{% if child_contact %} The children may call or video chat with the other parent at reasonable times.{% endif %}')
para('Change of Residence',
     'If either parent plans to change the residence of the children for more than 30 days, that parent shall give the other parent written notice of the planned change, by certified mail, return receipt requested, at least 45 days before the move, including the new address if known (Family Code section 3024). A move that would materially affect the parenting schedule requires the written agreement of both parents or a court order.')
para('Continuing Jurisdiction',
     'The court retains jurisdiction to modify the custody and parenting time orders as required by the best interest of the children.')

# ---------------------------------------------------------- child support
article('CHILD SUPPORT')
para('Incomes and Timeshare',
     'For purposes of child support, ' + P + '\'s gross income is {{ currency(pet_gross_income) }} per month and ' + R + '\'s gross income is {{ currency(resp_gross_income) }} per month. ' + P + ' has primary physical responsibility for the children {{ pet_timeshare }}% of the time and ' + R + ' {{ 100 - pet_timeshare }}% of the time. The parties\' guideline calculation shall be attached to the judgment.')
para('Guideline Amount',
     '{% if guideline_payor == "none" %}The guideline child support amount under Family Code section 4055 is $0.{% else %}The guideline child support amount under Family Code section 4055 is {{ currency(guideline_amt) }} per month, payable by {{ party_ref[guideline_payor] }}.{% endif %}')
para('Child Support',
     '{% if cs_payor == "none" %}Neither party shall pay child support to the other at this time. The court retains jurisdiction to order child support.'
     '{% else %}Beginning {{ format_date(cs_start_date) }}, {{ party_ref[cs_payor] }} shall pay to {{ party_ref[cs_payee] }} child support of {{ currency(cs_amount) }} per month for the children{% if cs_schedule == "semi_monthly" %}, payable one-half on the first and one-half on the fifteenth day of each month{% else %}, payable on the first day of each month{% endif %}. Support for each child shall continue until the child marries, dies, is emancipated, reaches age 18, or reaches age 19 if the child is unmarried, a full-time high school student, and not self-supporting, whichever occurs first (Family Code section 3901), or until further order of the court.{% endif %}')
ctl('{%p if cs_deviates %}')
para('Stipulation to Non-Guideline Support',
     'The agreed child support differs from the guideline amount. Under Family Code section 4065(a), the parties declare that: (1) they are fully informed of their rights concerning child support; (2) this order is being agreed to without coercion or duress; (3) the agreement is in the best interests of the children; (4) the needs of the children will be adequately met by the stipulated amount; and (5) the right to support has not been assigned to the county under Family Code section 17402, and no public assistance application is pending.{% if cs_deviation_reason %} The parties agree to this amount because {{ period(cs_deviation_reason) }}{% endif %}{% if cs_below_guideline %} Because the stipulated amount is below the guideline amount, no change of circumstances is required to modify it (Family Code section 4065(d)).{% endif %}')
ctl('{%p endif %}')
para('Child Care Costs',
     P + ' shall pay {{ addon_pet_share }}% and ' + R + ' shall pay {{ addon_resp_share }}% of the reasonable costs of child care related to either parent\'s employment or reasonably necessary education or training for employment skills (Family Code section 4062(a)(1)).')
para('Uninsured Health Care Costs',
     'The parties shall pay the children\'s reasonable uninsured health care costs, including deductibles and copayments for medical, dental, vision, orthodontic, and mental health care, in the same percentages (Family Code section 4062(a)(2)). The parties shall follow the procedures in the Notice of Rights and Responsibilities (form FL-192): a parent who pays a cost shall give the other parent an itemized statement and proof of payment within 30 days, and the other parent shall reimburse their share within 30 days after receiving it.')
ctl('{%p if extracurricular_shared %}')
para('Extracurricular and Educational Expenses',
     'The parties shall share the costs of extracurricular activities, private school or tutoring, and other educational expenses in the same percentages, but only for activities and expenses both parties agree to in writing in advance. Agreement shall not be unreasonably withheld.')
ctl('{%p endif %}')
para('Health Insurance',
     '{% if health_ins_provider in ["pet", "resp"] %}{{ party_ref[health_ins_provider] }} shall maintain health, dental, and vision insurance for the children{% elif health_ins_provider == "both" %}Each party shall maintain health, dental, and vision insurance for the children if available through that party\'s employment{% else %}The parent who has health, dental, and vision insurance available for the children at no or reasonable cost shall maintain it{% endif %}, as long as it is available at no or reasonable cost (Family Code section 3751), and shall provide the other parent with insurance cards, claim forms, and plan information. Each party shall notify the other of any change in employment or in the availability of insurance within 10 days.')
para('Tax Credits and Dependency',
     '{% if dependency_plan in ["pet", "resp"] %}{{ party_ref[dependency_plan] }} may claim the children as dependents and for the child tax credit on federal and state income tax returns.'
     '{% elif dependency_plan == "alternate" %}The parties shall alternate claiming the children as dependents and for the child tax credit on federal and state income tax returns, with ' + P + ' claiming them in {{ dependency_alt_start }} and every other year after that, and ' + R + ' claiming them in the other years.'
     '{% else %}{{ period(dependency_custom) }}{% endif %}'
     ' The parent who is the custodial parent for federal tax purposes shall sign IRS Form 8332, or its successor, as needed to carry out this paragraph{% if cs_payor != "none" %}, provided the parent claiming the children is current on child support as of December 31 of that tax year{% endif %}.')
ctl('{%p if cs_payor != "none" and cs_life_insurance %}')
para('Life Insurance',
     '{{ party_ref[cs_payor] }} shall maintain life insurance on {{ party_ref[cs_payor] }}\'s life with a death benefit of at least {{ currency(cs_life_amount) }}, naming {{ party_ref[cs_payee] }} as trustee for the children as beneficiary, for as long as child support is payable, and shall provide proof of coverage on request.')
ctl('{%p endif %}')
ctl('{%p if cs_payor != "none" %}')
para('Earnings Assignment',
     'An earnings assignment order for child support shall issue (Family Code section 5230). {% if wage_assignment == "stay" %}Under Family Code section 5260, the parties agree that service of the earnings assignment is stayed as long as {{ party_ref[cs_payor] }} pays support in full and on time. If any payment is late, {{ party_ref[cs_payee] }} may serve the earnings assignment without further notice or court order.{% else %}The earnings assignment shall be served on {{ party_ref[cs_payor] }}\'s employer. Until the employer begins withholding, {{ party_ref[cs_payor] }} shall pay support directly.{% endif %}')
ctl('{%p endif %}')
ctl('{%p if public_assistance or lcsa_involved %}')
para('Local Child Support Agency',
     'The parties acknowledge that the local child support agency is or may be a party to the Action. The support provisions of this Agreement shall be submitted to the local child support agency for its approval before entry of judgment.')
ctl('{%p endif %}')
para('Modification',
     'The child support provisions of this Agreement are separate and severable from its other provisions (Family Code section 3585) and remain subject to modification by the court. The parties cannot waive or limit the court\'s jurisdiction to modify child support.')
ctl('{%p endif %}')

# ---------------------------------------------------------- spousal support
article('{{ "PARTNER" if relationship_type == "rdp" else "SPOUSAL" }} SUPPORT')
ctl('{%p if ss_type == "pay" %}')
para('Support Payments',
     'Beginning {{ format_date(ss_start_date) }}, {{ party_ref[ss_payor] }} shall pay to {{ party_ref["resp" if ss_payor == "pet" else "pet"] }} as and for {{ "partner" if relationship_type == "rdp" else "spousal" }} support the sum of {{ currency(ss_amount) }} per month, payable on the first day of each month{% if ss_stepdown %}, subject to the following changes: {{ period(ss_stepdown) }}{% else %}.{% endif %}')
para('Duration',
     '{% if ss_end_type == "date" %}Support shall terminate on {{ format_date(ss_end_date) }}'
     '{% elif ss_end_type == "months" %}Support shall terminate after {{ ss_months }} monthly payments'
     '{% elif ss_end_type == "richmond" %}Support shall terminate on {{ format_date(ss_end_date) }}, unless before that date {{ party_ref["resp" if ss_payor == "pet" else "pet"] }} files and serves a request to extend support, in which case support shall continue until the court rules on the request (In re Marriage of Richmond (1980) 105 Cal.App.3d 352)'
     '{% else %}Support shall continue until further order of the court{% endif %}'
     ', or earlier on the death of either party{% if ss_terminate_remarriage %} or the remarriage or registration of a new domestic partnership by {{ party_ref["resp" if ss_payor == "pet" else "pet"] }}{% endif %}.'
     '{% if not ss_terminate_remarriage %} The parties expressly agree under Family Code section 4337 that support shall not terminate on the remarriage or new domestic partnership of {{ party_ref["resp" if ss_payor == "pet" else "pet"] }}.{% endif %}')
para('Jurisdiction',
     '{% if ss_end_type in ["date", "months"] and ss_jurisdiction_after == "terminate" %}When support terminates, the court\'s jurisdiction to award support to {{ party_ref["resp" if ss_payor == "pet" else "pet"] }} shall terminate permanently{% if long_duration %}. The parties acknowledge that their {{ marriage_word }} is of long duration and expressly agree in writing, under Family Code section 4336(a), that the court shall not retain jurisdiction over support after that date{% endif %}.'
     '{% else %}The court retains jurisdiction over support for {{ party_ref["resp" if ss_payor == "pet" else "pet"] }}{% if long_duration %}, which under Family Code section 4336 continues indefinitely unless terminated by court order{% endif %}.{% endif %}'
     ' {{ party_ref[ss_payor] }} waives any right to receive support from {{ party_ref["resp" if ss_payor == "pet" else "pet"] }}, and the court\'s jurisdiction to award support to {{ party_ref[ss_payor] }} is terminated.')
para('Modification',
     '{% if ss_modifiable %}The amount and duration of support may be modified by the court on a showing of a material change of circumstances, subject to the termination provisions of this Article.'
     '{% else %}Under Family Code section 3591(c), the parties expressly agree that the amount and duration of support stated in this Article are not subject to modification or termination by the court for any reason, except as stated in this Article, regardless of any change in circumstances, including changes in the income, health, or needs of either party.{% endif %}')
ctl('{%p if ss_cohabitation and ss_modifiable %}')
para('Cohabitation',
     'The parties acknowledge that if {{ party_ref["resp" if ss_payor == "pet" else "pet"] }} cohabits with a nonmarital partner, there is a rebuttable presumption of decreased need for support, which may be a basis for modification or termination (Family Code section 4323).')
ctl('{%p endif %}')
ctl('{%p if ss_life_insurance %}')
para('Life Insurance',
     '{{ party_ref[ss_payor] }} shall maintain life insurance on {{ party_ref[ss_payor] }}\'s life with a death benefit of at least {{ currency(ss_life_amount) }}, naming {{ party_ref["resp" if ss_payor == "pet" else "pet"] }} as beneficiary, for as long as support is payable, and shall provide proof of coverage on request (Family Code section 4360).')
ctl('{%p endif %}')
para('Earnings Assignment',
     'An earnings assignment order for support shall issue (Family Code section 5230). {% if wage_assignment == "stay" %}Under Family Code section 5260, service of the earnings assignment is stayed as long as {{ party_ref[ss_payor] }} pays support in full and on time. If any payment is late, {{ party_ref["resp" if ss_payor == "pet" else "pet"] }} may serve it without further notice or court order.{% else %}The earnings assignment shall be served on {{ party_ref[ss_payor] }}\'s employer.{% endif %}')
para('Tax Treatment',
     'The parties understand that support paid under this Agreement is not deductible by {{ party_ref[ss_payor] }} or includible in the income of {{ party_ref["resp" if ss_payor == "pet" else "pet"] }} for federal income tax purposes, and that its treatment for California income tax purposes may differ. Each party has been advised to obtain independent tax advice.')
ctl('{%p elif ss_type == "waive" %}')
para('Mutual Waiver of Support',
     'Each party knowingly, voluntarily, and permanently waives any right to receive {{ "partner" if relationship_type == "rdp" else "spousal" }} support from the other. Each party understands that: (a) this waiver is permanent and cannot be modified, even if circumstances change drastically; (b) the court will have no jurisdiction to award support to either party, now or in the future; (c) each party has considered their present and future health, income, and needs; and (d) each party has had the opportunity to consult independent counsel about this waiver. The court\'s jurisdiction to award support to either party is terminated permanently{% if long_duration %}, and the parties expressly agree in writing under Family Code section 4336(a) that the court shall not retain jurisdiction over support even though their {{ marriage_word }} is of long duration{% endif %}.')
ctl('{%p else %}')
para('Reservation of Support',
     'No support is ordered at this time. The court reserves jurisdiction to award {{ "partner" if relationship_type == "rdp" else "spousal" }} support to either party{% if long_duration %}, which under Family Code section 4336 continues indefinitely unless terminated by court order{% endif %}.')
ctl('{%p endif %}')
ctl('{%p if ss_type != "waive" %}')
para('Notice Under Family Code Section 4330(b)',
     'Each party is advised that it is the goal of this state that each party shall make reasonable good faith efforts to become self-supporting as provided in Family Code section 4320. The failure to make reasonable good faith efforts may be one of the factors considered by the court as a basis for modifying or terminating support.')
ctl('{%p endif %}')
ctl('{%p if support_arrears %}')
para('Temporary Support Arrears and Credits',
     '{{ period(arrears_terms) | manual_line_breaks }}')
ctl('{%p endif %}')

# ---------------------------------------------------------- property and debts
# Laid out like the LASC judgment form, items 501-504: property and debts
# awarded and confirmed to each party, whether community or separate.
def lines(seq, var):
    """Numbered list of one-line items, or "None." when the list is empty."""
    ctl('{%p if ' + seq + ' %}')
    loop(var, seq, '{% if loop.last %}{{ period(' + var + ') }}{% else %}{{ ' + var + ' }};{% endif %}')
    ctl('{%p else %}')
    item('None.')
    ctl('{%p endif %}')


article('DIVISION OF PROPERTY AND DEBTS')
ctl("{%p if assets_status == 'none' %}")
para('Property', 'There are no assets to be disposed of by the court.')
ctl('{%p else %}')
for who, other in ((P, R), (R, P)):
    var = 'pet_property' if who == P else 'resp_property'
    para('Property Awarded and Confirmed to ' + who,
         'The following property, whether community or separate, is awarded and confirmed to ' + who
         + ' as the separate property of ' + who + ', along with any and all encumbrances on it, and '
         + who + ' shall hold ' + other + ' harmless from those encumbrances:')
    lines(var, 'asset')
ctl('{%p endif %}')
ctl("{%p if debts_status == 'none' %}")
para('Debts', 'There are no debts to be disposed of by the court.')
ctl('{%p else %}')
for who, other in ((P, R), (R, P)):
    var = 'pet_debts' if who == P else 'resp_debts'
    para('Debts Awarded and Confirmed to ' + who,
         'The following debts (Family Code sections 2620 through 2627), whether community or separate, are awarded and confirmed to '
         + who + ' as ' + who + '\'s separate debts, and ' + who + ' shall hold ' + other + ' harmless from these obligations:')
    lines(var, 'debt')
ctl('{%p endif %}')
para('Omitted Assets and Debts',
     'Any community or quasi-community asset or debt not divided by this Agreement shall be divided equally between the parties on the request of either party, and the court retains jurisdiction to do so (Family Code section 2556). This paragraph does not limit any remedy for a breach of fiduciary duty or of the duty of disclosure.')
para('Transfer Documents',
     'Each party shall sign, acknowledge, and deliver any deed, title, transfer form, beneficiary change, or other document reasonably needed to carry out this Agreement within 15 days after a written request. If a party fails to do so, the court may appoint the clerk of the court or another person as elisor to sign it (Code of Civil Procedure section 128(a)(4)).')
para('Characterization',
     'To the extent this Agreement changes the character of any property, this Agreement is an express written declaration of transmutation by the party whose interest is adversely affected (Family Code section 852).')

# ---------------------------------------------------------- taxes
article('INCOME TAXES')
para('Tax Year {{ this_tax_year }}',
     '{% if tax_filing_current == "separate" %}For tax year {{ this_tax_year }} and later years, each party shall file separate income tax returns and report their own income and deductions.'
     '{% elif tax_filing_current == "joint_option" %}For tax year {{ this_tax_year }}, the parties may file joint {{ "California " if relationship_type == "rdp" else "" }}income tax returns if both agree in writing when the returns are prepared; otherwise, each shall file separately. If joint returns are filed, any refund or liability shall be divided in proportion to each party\'s income reported on them.'
     '{% else %}For tax year {{ this_tax_year }}, the parties shall file joint {{ "California " if relationship_type == "rdp" else "" }}income tax returns, and each shall timely provide the information needed to prepare them. Any refund or liability shall be divided in proportion to each party\'s income reported on them.{% endif %}')
ctl('{%p if filed_joint %}')
para('Prior Joint Returns',
     'Any tax, interest, or penalty later assessed, or refund received, on a joint return filed during the {{ marriage_word }} shall be {% if prior_tax_split == "equal" %}shared equally{% else %}paid by, or credited to, the party whose income, deductions, credits, or omissions gave rise to it, and shared equally if attributable to both or neither{% endif %}. Each party shall give the other a copy of any notice from a taxing authority concerning a joint return within 10 days after receiving it.')
ctl('{%p endif %}')
para('Tax Treatment of Transfers',
     '{% if relationship_type == "rdp" %}The parties understand that the federal income tax rules for transfers between spouses (26 U.S.C. section 1041) may not apply to transfers between registered domestic partners.{% else %}The parties intend that the transfers of property under this Agreement are transfers incident to divorce under 26 U.S.C. section 1041, and that each party takes the other\'s tax basis in property received.{% endif %} Each party has been advised to obtain independent tax advice.')

# ---------------------------------------------------------- fees
article("ATTORNEY'S FEES AND COSTS")
para("Fees and Costs",
     '{% if atty_fees == "own" %}Each party shall pay their own attorney\'s fees and costs incurred in the Action and in connection with this Agreement.'
     '{% else %}{{ party_ref["pet" if atty_fees == "pet_pays" else "resp"] }} shall pay {{ currency(atty_fees_amount) }} as a contribution to the attorney\'s fees and costs of {{ party_ref["resp" if atty_fees == "pet_pays" else "pet"] }} within {{ atty_fees_due_days }} days after the date this Agreement is signed{% if atty_fees == "pet_pays" and resp_has_counsel %}, payable directly to {{ resp_counsel_name }}{% elif atty_fees == "resp_pays" and pet_has_counsel %}, payable directly to {{ pet_counsel_name }}{% endif %}. Except as stated in this paragraph, each party shall pay their own attorney\'s fees and costs.{% endif %}')
ctl('{%p if enforcement_fees %}')
para('Enforcement',
     'In any proceeding to enforce this Agreement or the judgment incorporating it, the court shall award reasonable attorney\'s fees and costs to the prevailing party.')
ctl('{%p endif %}')

# ---------------------------------------------------------- disclosures
article('DISCLOSURES')
para('Preliminary Declarations of Disclosure',
     '{% if fl144_waiver %}Each party has completed and served a preliminary Declaration of Disclosure and a current Income and Expense Declaration, as confirmed in the parties\' Stipulation and Waiver of Final Declaration of Disclosure (form FL-144) (Family Code sections 2104 and 2105(d)).{% else %}'
     '{% if pet_prelim_served %}' + P + ' served a preliminary Declaration of Disclosure on {{ format_date(pet_prelim_date) }}.{% else %}' + P + ' shall serve a preliminary Declaration of Disclosure before entry of judgment.{% endif %} '
     '{% if resp_prelim_served %}' + R + ' served a preliminary Declaration of Disclosure on {{ format_date(resp_prelim_date) }}.{% else %}' + R + ' shall serve a preliminary Declaration of Disclosure before entry of judgment.{% endif %}'
     ' (Family Code section 2104.){% endif %}')
para('Final Declarations of Disclosure',
     '{% if final_status == "exchanged" %}The parties have exchanged final Declarations of Disclosure under Family Code section 2105.'
     '{% elif final_status == "waived" %}The parties waive the final Declaration of Disclosure under Family Code section 2105(d). Each party declares under penalty of perjury that: (1) the party has complied with Family Code section 2104 and the preliminary Declaration of Disclosure has been completed and exchanged; (2) the party has completed and exchanged a current Income and Expense Declaration that includes all material facts and information on the party\'s earnings, accumulations, and expenses; (3) the party has fully complied with Family Code section 2102 and has fully augmented the preliminary Declaration of Disclosure, if needed; (4) the waiver is knowingly, intelligently, and voluntarily entered into by the party; and (5) the party understands that this waiver does not limit the legal disclosure obligations of the parties, but rather is a statement under penalty of perjury that those obligations have been fulfilled. The parties shall also sign and file a Stipulation and Waiver of Final Declaration of Disclosure (form FL-144).'
     '{% else %}Each party shall serve a final Declaration of Disclosure before entry of judgment, unless the parties waive it in writing under Family Code section 2105(d).{% endif %}')
para('Full Disclosure',
     'Each party warrants that they have fully disclosed all assets and debts in which they have or may have an interest, their income and expenses, and all material facts and information concerning the characterization and valuation of those assets and debts and any investment opportunity that arose during the {{ marriage_word }} (Family Code sections 721, 1100, and 2100 through 2113). Each party understands that the duty to update and correct these disclosures continues until the assets and debts have been distributed (Family Code section 2102).')

# ---------------------------------------------------------- general
article('GENERAL PROVISIONS')
ctl('{%p if pet_restore_name or resp_restore_name %}')
para('Restoration of Former Name',
     '{% if pet_restore_name %}' + P + '\'s former name, {{ pet_former_name }}, shall be restored. {% endif %}{% if resp_restore_name %}' + R + '\'s former name, {{ resp_former_name }}, shall be restored.{% endif %}')
ctl('{%p endif %}')
ctl('{%p if spouse_coverage %}')
para('Health Insurance for the Parties',
     'Until marital status is terminated, each party shall maintain any existing health insurance coverage for the other party to the extent the plan allows. After that, the covered party may elect continuation coverage under COBRA or Cal-COBRA at their own expense, and the insured party shall give the plan timely notice of the termination of marital status.')
ctl('{%p endif %}')
ctl('{%p if own_insurance %}')
para('Other Insurance',
     'From the date of this Agreement, each party shall maintain, at their own expense, any life, automobile, homeowner\'s, renter\'s, and other insurance on their own life and on the property awarded to them, except as otherwise required by this Agreement.')
ctl('{%p endif %}')
para('Estate Planning',
     'The parties understand that the automatic temporary restraining orders in the Summons remain in effect until judgment is entered (Family Code section 2040). After judgment, each party may change their estate plan and beneficiary designations, except as required by this Agreement. Each party is advised to review their will, trust, powers of attorney, and the beneficiary designations on retirement plans, life insurance, and transfer-on-death accounts, because some of them are not changed automatically by the judgment.')
para('Dispute Resolution',
     '{% if dispute_resolution == "mediation" %}Except in an emergency or as needed to preserve a party\'s rights, before filing a request for court action concerning this Agreement, the parties shall attempt in good faith to resolve the dispute through mediation, with the cost shared equally. Disputes about custody or parenting time remain subject to child custody mediation or recommending counseling under Family Code section 3170.'
     '{% else %}Either party may ask the court to resolve any dispute concerning this Agreement.{% endif %}')
para('Incorporation in Judgment',
     'The parties shall submit this Agreement to the court and request that it be attached to and incorporated in the judgment in the Action, and that the parties be ordered to comply with all of its terms. On entry of judgment, this Agreement shall merge into the judgment, and its terms shall be enforceable as orders of the court.')
para('Effective Date and Enforcement',
     'This Agreement is effective and binding on the parties on the date the last party signs it, whether or not it is incorporated in a judgment. The parties request that the court retain jurisdiction under Code of Civil Procedure section 664.6 to enforce this Agreement until all of its terms are performed in full.')
para('Mutual Release',
     'Except for the obligations stated in this Agreement and claims based on assets or debts not disclosed, each party releases the other from all claims, demands, and obligations arising from their {{ marriage_word }}, including claims for breach of fiduciary duty.{% if has_minor_children %} This release does not affect any right of the children.{% endif %}')
para('Voluntary Agreement',
     'Each party has read this Agreement, understands it, believes it to be fair and equitable, and signs it voluntarily, free from duress, coercion, or undue influence. Each party acknowledges that no promise or representation not stated in this Agreement has been made to induce them to sign it.')
para('Entire Agreement',
     'This Agreement contains the entire agreement of the parties on its subject matter and supersedes all prior agreements, written or oral, except existing orders in the Action, which remain in effect until superseded by the judgment.')
para('Modification',
     'This Agreement may be modified only by a written agreement signed by both parties or by court order, except that provisions subject to the court\'s continuing jurisdiction may be modified by the court as allowed by law.')
para('Severability',
     'If any provision of this Agreement is held invalid or unenforceable, the remaining provisions shall remain in full force and effect.')
para('Governing Law',
     'This Agreement shall be governed by and interpreted under the laws of the State of California.')
para('Interpretation',
     'This Agreement is the product of negotiation by both parties and shall be interpreted fairly and not for or against either party as its drafter. Headings are for convenience only and do not affect its meaning.')
para('Counterparts and Electronic Signatures',
     'This Agreement may be signed in counterparts, each of which is an original and all of which together are one agreement. Signatures delivered electronically or by PDF are effective as originals.')

# ---------------------------------------------------------- additional
ctl('{%p if additional_paragraphs %}')
article('ADDITIONAL PROVISIONS')
ctl('{%p for provision in additional_paragraphs %}')
par = doc.add_paragraph()
par.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
par.paragraph_format.first_line_indent = Inches(0.5)
_run(par, '{{ sec.para() }}\t', bold=True)
_run(par, '{{ provision }}')
ctl('{%p endfor %}')
ctl('{%p endif %}')

# ---------------------------------------------------------- signatures
text('The parties have signed this Agreement on the dates stated below.', first=0.5, space_after=24, keep=True)
signature('{{ petitioner }}', 'Petitioner')
signature('{{ respondent }}', 'Respondent')
ctl('{%p if pet_has_counsel or resp_has_counsel %}')
text('APPROVED AS TO FORM:', align='left', bold=True, space_after=24, keep=True)
ctl('{%p if pet_has_counsel %}')
text('Dated: ____________________', align='left', space_after=24, keep=True)
text('______________________________________', align='left', space_after=0, keep=True)
text('{{ pet_counsel_name }} (SBN {{ pet_counsel_sbn }}){% if pet_counsel_firm %}, {{ pet_counsel_firm }}{% endif %}', align='left', space_after=0, keep=True)
text('Attorney for Petitioner', align='left', space_after=24)
ctl('{%p endif %}')
ctl('{%p if resp_has_counsel %}')
text('Dated: ____________________', align='left', space_after=24, keep=True)
text('______________________________________', align='left', space_after=0, keep=True)
text('{{ resp_counsel_name }} (SBN {{ resp_counsel_sbn }}){% if resp_counsel_firm %}, {{ resp_counsel_firm }}{% endif %}', align='left', space_after=0, keep=True)
text('Attorney for Respondent', align='left', space_after=24)
ctl('{%p endif %}')
ctl('{%p endif %}')

ctl('{%p if notarize %}')
page_break()
notary('{{ petitioner }}')
page_break()
notary('{{ respondent }}')
ctl('{%p endif %}')

os.makedirs(os.path.dirname(OUT), exist_ok=True)
doc.save(OUT)
print('wrote', os.path.normpath(OUT))
