"""Helpers for the California Marital Settlement Agreement interview.

Asset and debt classes, the Family Code section 2550 equal-division
math, marriage-length helpers, and a section counter that numbers the
articles of the generated agreement after conditional articles drop out.
"""
from dateutil.relativedelta import relativedelta

from docassemble.base.util import DAObject, currency, validation_error

__all__ = [
    'CA_COUNTIES',
    'MSAItem',
    'RealProperty',
    'Vehicle',
    'FinancialAccount',
    'RetirementPlan',
    'BusinessInterest',
    'OtherAsset',
    'Debt',
    'SectionCounter',
    'equalization',
    'marriage_length',
    'marriage_length_text',
    'party_key_label',
    'preparer_role_label',
    'is_bar_number',
    'custody_label',
    'schedule_label',
    'items_for',
    'period',
]

CA_COUNTIES = [
    'Alameda', 'Alpine', 'Amador', 'Butte', 'Calaveras', 'Colusa',
    'Contra Costa', 'Del Norte', 'El Dorado', 'Fresno', 'Glenn', 'Humboldt',
    'Imperial', 'Inyo', 'Kern', 'Kings', 'Lake', 'Lassen', 'Los Angeles',
    'Madera', 'Marin', 'Mariposa', 'Mendocino', 'Merced', 'Modoc', 'Mono',
    'Monterey', 'Napa', 'Nevada', 'Orange', 'Placer', 'Plumas', 'Riverside',
    'Sacramento', 'San Benito', 'San Bernardino', 'San Diego',
    'San Francisco', 'San Joaquin', 'San Luis Obispo', 'San Mateo',
    'Santa Barbara', 'Santa Clara', 'Santa Cruz', 'Shasta', 'Sierra',
    'Siskiyou', 'Solano', 'Sonoma', 'Stanislaus', 'Sutter', 'Tehama',
    'Trinity', 'Tulare', 'Tuolumne', 'Ventura', 'Yolo', 'Yuba',
]

SEPARATE_OWNER = {'sp_pet': 'pet', 'sp_resp': 'resp'}


def _num(val):
    try:
        return float(val or 0)
    except (TypeError, ValueError):
        return 0.0


def _one_line(text):
    return ', '.join(line.strip() for line in str(text).splitlines() if line.strip())


def period(text):
    """End user-entered text with exactly one period, so "6:00 p.m." stays "6:00 p.m."."""
    text = str(text or '').strip()
    if not text:
        return ''
    return text if text[-1] in '.!?' else text + '.'


def items_for(lists, alloc, separate=False):
    """Items from several lists allocated to 'pet', 'resp' or 'split'.

    With separate=True, returns the items confirmed as that party's
    separate property instead of community items awarded to them.
    """
    out = []
    for items in lists:
        for item in items:
            if item.is_separate() == separate and item.allocation() == alloc:
                out.append(item)
    return out


def party_key_label(key):
    """Plain label for a party key, used in tables before party names are final."""
    return {'pet': 'Petitioner', 'resp': 'Respondent', 'split': 'Divided equally'}.get(key, key)


def preparer_role_label(role):
    return {
        'atty_pet': 'Attorney for Petitioner',
        'atty_resp': 'Attorney for Respondent',
        'mediator': 'Mediator',
        'staff': 'Staff, for attorney review',
    }.get(role, role)


def is_bar_number(value):
    """California State Bar numbers are 1 to 6 digits."""
    digits = str(value).strip()
    if not digits.isdigit() or len(digits) > 6:
        validation_error('Enter the State Bar number using digits only (up to 6).')
    return True


def custody_label(key, kind):
    """Short label for a legal or physical custody choice."""
    base = {
        'joint': 'joint %s custody',
        'primary_pet': 'joint %s custody, primary residence with Petitioner',
        'primary_resp': 'joint %s custody, primary residence with Respondent',
        'sole_pet': 'sole %s custody to Petitioner',
        'sole_resp': 'sole %s custody to Respondent',
    }.get(key, key + ' %s')
    return base % kind


def schedule_label(key):
    return {
        'alt_weeks': 'Alternating weeks',
        '2255': '2-2-5-5 rotation',
        '223': '2-2-3 rotation',
        'eow_midweek': 'Alternate weekends plus midweek',
        'eow': 'Alternate weekends',
        'supervised': 'Supervised visitation',
        'custom': 'Custom schedule',
        'attached': 'Attached parenting plan',
    }.get(key, key)


class MSAItem(DAObject):
    """Base class for every asset or debt in the agreement.

    Subclasses set `category` and `has_encumbrance`. Every item has
    `description`, `value` (fair market value or balance), `character`
    ('community', 'mixed', 'sp_pet', 'sp_resp') and an allocation.
    """
    category = 'Asset'
    has_encumbrance = False
    is_debt = False

    def gross_value(self):
        return _num(self.value)

    def net_value(self):
        if self.has_encumbrance:
            return _num(self.value) - _num(self.encumbrance)
        return _num(self.value)

    def is_separate(self):
        return self.character in SEPARATE_OWNER

    def community_value(self):
        """Net community interest that counts toward the equal division."""
        if self.character == 'community':
            return self.net_value()
        if self.character == 'mixed':
            return _num(self.community_portion)
        return 0.0

    def allocation(self):
        """'pet', 'resp' or 'split' - who receives the item (or its community interest)."""
        if self.is_separate():
            return SEPARATE_OWNER[self.character]
        return self.awarded_to

    def other_party(self):
        """Key of the party who does not receive the item."""
        return 'resp' if self.allocation() == 'pet' else 'pet'

    def short_desc(self):
        return _one_line(self.description)

    def character_label(self):
        return {
            'community': 'Community',
            'mixed': 'Mixed (community and separate)',
            'sp_pet': "Petitioner's separate",
            'sp_resp': "Respondent's separate",
        }.get(self.character, self.character)


class RealProperty(MSAItem):
    category = 'Real property'
    has_encumbrance = True

    def short_name(self):
        return _one_line(self.description)

    def legal_text(self):
        txt = 'The real property commonly known as ' + _one_line(self.description)
        if self.apn:
            txt += ' (APN ' + self.apn + ')'
        txt += ', together with all improvements and fixtures'
        if _num(self.encumbrance) > 0:
            txt += ', subject to all encumbrances'
            if self.lenders:
                txt += ', including the loan(s) held by ' + self.lenders
        return txt

    def allocation(self):
        if self.is_separate():
            return SEPARATE_OWNER[self.character]
        return 'split' if self.disposition == 'sell' else self.disposition


class Vehicle(MSAItem):
    category = 'Vehicle'
    has_encumbrance = True

    def legal_text(self):
        txt = 'The ' + self.description
        if self.vin_last4:
            txt += ' (VIN ending ' + self.vin_last4 + ')'
        if _num(self.encumbrance) > 0:
            txt += ', subject to the loan secured by it'
        return txt


class FinancialAccount(MSAItem):
    category = 'Financial account'
    type_words = {
        'checking': 'checking account', 'savings': 'savings account',
        'cd': 'certificate of deposit', 'brokerage': 'brokerage account',
        'hsa': 'health savings account', 'education': '529 education savings plan',
        'crypto': 'cryptocurrency account', 'life': 'life insurance policy (cash value)',
        'other': 'account',
    }

    def legal_text(self):
        txt = 'The ' + self.description + ' ' + self.type_words.get(self.account_type, 'account')
        if self.last4:
            txt += ' ending in ' + self.last4
        return txt + ', including all funds and accrued earnings'


class RetirementPlan(MSAItem):
    category = 'Retirement'

    def allocation(self):
        if self.is_separate():
            return SEPARATE_OWNER[self.character]
        if self.division == 'qdro':
            return 'split'
        return self.division

    def legal_text(self):
        return 'All of the community interest in ' + self.description

    def needs_order(self):
        """IRAs move by transfer incident to divorce; employer plans need a QDRO/DRO."""
        return self.plan_type not in ('ira', 'roth_ira')

    def offers_survivor(self):
        """Plans with a survivor-benefit election to address in the order."""
        return self.plan_type in ('db', 'calpers', 'calstrs', 'county', 'federal', 'military')


class BusinessInterest(MSAItem):
    category = 'Business interest'
    entity_words = {
        'sole': 'a sole proprietorship', 'partnership': 'a partnership',
        'llc': 'a limited liability company', 'corporation': 'a corporation',
        'pc': 'a professional corporation',
    }

    def legal_text(self):
        pct = _num(self.ownership_pct)
        pct_text = ('%g%% ' % pct) if pct and pct < 100 else 'entire '
        return ("The parties' " + pct_text + 'interest in ' + self.description + ', '
                + self.entity_words.get(self.entity_type, 'a business')
                + ', including its goodwill, assets, accounts receivable, and name, '
                + 'subject to its liabilities')


class OtherAsset(MSAItem):
    category = 'Other asset'

    def legal_text(self):
        return _one_line(self.description)


class Debt(MSAItem):
    category = 'Debt'
    is_debt = True

    def community_value(self):
        if self.character == 'community':
            return _num(self.value)
        return 0.0

    def allocation(self):
        if self.is_separate():
            return SEPARATE_OWNER[self.character]
        return self.assigned_to

    def legal_text(self):
        txt = 'The debt owed to ' + self.description
        if self.last4:
            txt += ' (account ending in ' + self.last4 + ')'
        return txt + ', with an approximate balance of ' + currency(_num(self.value))


def equalization(asset_lists, debts):
    """Compute the equal division of the community estate (Fam. Code 2550).

    Items awarded 'split' are divided in kind and do not move the
    equalizing payment. Returns a dict of totals plus the payment and payor.
    """
    totals = {'pet_assets': 0.0, 'resp_assets': 0.0, 'pet_debts': 0.0,
              'resp_debts': 0.0, 'split_assets': 0.0, 'split_debts': 0.0}
    for items in asset_lists:
        for item in items:
            cv = item.community_value()
            if not cv or item.is_separate():
                continue
            totals[item.allocation() + '_assets'] += cv
    for debt in debts:
        cv = debt.community_value()
        if not cv or debt.is_separate():
            continue
        totals[debt.allocation() + '_debts'] += cv
    pet_net = totals['pet_assets'] - totals['pet_debts']
    resp_net = totals['resp_assets'] - totals['resp_debts']
    diff = pet_net - resp_net
    totals.update({
        'pet_net': pet_net,
        'resp_net': resp_net,
        'community_total': pet_net + resp_net
        + totals['split_assets'] - totals['split_debts'],
        'payment': round(abs(diff) / 2.0, 2),
        'payor': 'pet' if diff > 0 else ('resp' if diff < 0 else None),
    })
    totals['payee'] = {'pet': 'resp', 'resp': 'pet'}.get(totals['payor'])
    totals['payment_text'] = currency(totals['payment'])
    return totals


def marriage_length(start, end):
    """(years, months) between the date of marriage and the date of separation."""
    delta = relativedelta(end.date() if hasattr(end, 'date') else end,
                          start.date() if hasattr(start, 'date') else start)
    return delta.years, delta.months


def marriage_length_text(start, end):
    years, months = marriage_length(start, end)
    parts = []
    if years:
        parts.append('%d year%s' % (years, '' if years == 1 else 's'))
    if months or not years:
        parts.append('%d month%s' % (months, '' if months == 1 else 's'))
    return ' and '.join(parts)


class SectionCounter(DAObject):
    """Numbers articles and paragraphs in the DOCX template.

    Call `reset()` at the top of the template, `article()` for each
    ARTICLE heading and `para()` for each numbered paragraph. Articles
    inside a false `{%p if %}` are never evaluated, so numbering stays
    consecutive whatever is included.
    """
    def init(self, *pargs, **kwargs):
        self.art = 0
        self.sub = 0
        super().init(*pargs, **kwargs)

    def reset(self):
        self.art = 0
        self.sub = 0
        return ''

    def article(self):
        self.art += 1
        self.sub = 0
        return str(self.art)

    def para(self):
        self.sub += 1
        return '%d.%d' % (self.art, self.sub)
