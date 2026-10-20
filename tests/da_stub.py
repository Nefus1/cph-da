"""Minimal stand-ins for the docassemble objects and functions the CPH
interviews use, so code blocks and DOCX templates can be tested
without a docassemble server.

Only the behavior the interviews rely on is implemented. Install with
`install()` before importing `docassemble.cphda.msa_util`.
"""
import datetime
import sys
import types

from dateutil.relativedelta import relativedelta


class ValidationError(Exception):
    pass


def validation_error(message, field=None):
    raise ValidationError(message)


def currency(value, decimals=True):
    value = float(value or 0)
    if decimals:
        return '${:,.2f}'.format(value)
    return '${:,.0f}'.format(value)


class DADateTime(datetime.datetime):
    def plus(self, **kwargs):
        res = self + relativedelta(**kwargs)
        return DADateTime(res.year, res.month, res.day)

    def minus(self, **kwargs):
        res = self - relativedelta(**kwargs)
        return DADateTime(res.year, res.month, res.day)

    def format(self, fmt='long'):
        return format_date(self, format=fmt)


def as_date(text):
    d = datetime.date.fromisoformat(text)
    return DADateTime(d.year, d.month, d.day)


def today():
    t = datetime.date.today()
    return DADateTime(t.year, t.month, t.day)


def format_date(value, format='long'):
    if format == 'long':
        return value.strftime('%B ') + str(value.day) + value.strftime(', %Y')
    if format == 'MM/dd/yyyy':
        return value.strftime('%m/%d/%Y')
    if format == 'yyyy-MM-dd':
        return value.strftime('%Y-%m-%d')
    return value.isoformat()


def comma_and_list(items):
    items = [str(x) for x in items]
    if not items:
        return ''
    if len(items) == 1:
        return items[0]
    if len(items) == 2:
        return items[0] + ' and ' + items[1]
    return ', '.join(items[:-1]) + ', and ' + items[-1]


def space_to_underscore(text):
    return text.replace(' ', '_')


def word(text):
    return text


def yesno(value):
    return 'Yes' if value else 'No'


def action_menu_item(label, action):
    return {'label': label, 'action': action}


class DAObject:
    def __init__(self, *pargs, **kwargs):
        self.init(*pargs, **kwargs)

    def init(self, *pargs, **kwargs):
        for key, val in kwargs.items():
            setattr(self, key, val)


class Name(DAObject):
    middle = ''
    suffix = ''

    def full(self, middle='initial'):
        parts = [self.first]
        if self.middle:
            parts.append(self.middle[0] + '.' if middle == 'initial' else self.middle)
        parts.append(self.last)
        if self.suffix:
            parts.append(self.suffix)
        return ' '.join(parts)


class Address(DAObject):
    pass


class Individual(DAObject):
    def init(self, *pargs, **kwargs):
        self.name = Name()
        self.address = Address()
        super().init(*pargs, **kwargs)

    def __str__(self):
        return self.name.full()

    def age_in_years(self):
        return relativedelta(today(), self.birthdate).years


class DAList(list):
    def complete_elements(self):
        return list(self)


class DADict(dict):
    def all_true(self):
        return all(self.values())

    def true_values(self):
        return [k for k, v in self.items() if v]


def install():
    """Register fake docassemble.base.util so the package module imports."""
    util = types.ModuleType('docassemble.base.util')
    for name, obj in list(globals().items()):
        if not name.startswith('_'):
            setattr(util, name, obj)
    base = types.ModuleType('docassemble.base')
    base.util = util
    sys.modules.setdefault('docassemble.base', base)
    sys.modules['docassemble.base.util'] = util
    return util
