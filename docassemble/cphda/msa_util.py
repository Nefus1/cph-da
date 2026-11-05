"""Helpers for the California Marital Settlement Agreement interview.

Property and debt list parsing, marriage-length helpers, labels, and a
section counter that numbers the articles of the generated agreement
after conditional articles drop out.
"""
import re

from dateutil.relativedelta import relativedelta

from docassemble.base.util import DAObject, validation_error

__all__ = [
    'CA_COUNTIES',
    'SectionCounter',
    'item_lines',
    'marriage_length',
    'marriage_length_text',
    'is_bar_number',
    'custody_label',
    'schedule_label',
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


def period(text):
    """End user-entered text with exactly one period, so "6:00 p.m." stays "6:00 p.m."."""
    text = str(text or '').strip()
    if not text:
        return ''
    return text if text[-1] in '.!?' else text + '.'


def item_lines(text):
    """Split a box of "one item per line" text into a list of items.

    Blank lines are dropped, and any bullet or number the user typed
    ("-", "*", "1.", "(2)") is removed, because the agreement numbers
    the items itself.
    """
    items = []
    for line in str(text or '').splitlines():
        line = re.sub(r'^\s*(?:[-*\u2022]+\s*|\(?\d{1,3}[.)]\s+)', '', line).strip()
        line = line.rstrip(';,').strip()
        if line:
            items.append(line)
    return items


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
