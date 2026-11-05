"""Offline tests for the California MSA interview.

For each sample scenario this runs the interview's code blocks, the
validation code, every Mako text on every screen, every table column,
and renders the DOCX template with docxtpl. A block whose text depends
on answers that a scenario does not have is skipped for that scenario,
but every block must render cleanly in at least one scenario.
"""
import io
import os
import re
import sys

import jinja2
import pytest
import yaml
from docx import Document
from docxtpl import DocxTemplate
import mako.runtime
from mako.template import Template

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, ROOT)

import da_stub  # noqa: E402
import msa_scenarios  # noqa: E402
from docassemble.cphda import msa_util  # noqa: E402

QDIR = os.path.join(ROOT, 'docassemble', 'cphda', 'data', 'questions')
TEMPLATE = os.path.join(ROOT, 'docassemble', 'cphda', 'data', 'templates', 'ca_msa.docx')
FILES = ['ca_msa.yml', 'ca_msa_children_support.yml', 'ca_msa_property.yml',
         'ca_msa_terms.yml', 'ca_msa_documents.yml']

# Code blocks run in this order, as the interview order would trigger them.
CODE_ORDER = [
    'case type', 'party references', 'relationship words', 'marriage length', 'caption header',
    'child support final values', 'addon percentages', 'spousal summary text',
    'property lists', 'final disclosure status', 'additional terms paragraphs',
    'filename', 'status date', 'tax year', 'drafting issues',
]
CHILD_ONLY = {'child support final values', 'addon percentages'}
NOT_APPLICABLE = (NameError, IndexError, KeyError, AttributeError)
SKIP_KEYS = {'code', 'validation code', 'js show if', 'js hide if', 'id', 'event', 'generic object',
             'if', 'table', 'rows', 'columns', 'edit', 'datatype', 'input type', 'variable', 'is',
             'docx template file', 'valid formats', 'metadata', 'comment', 'terms', 'sections',
             'features', 'objects', 'include', 'modules', 'show if', 'hide if', 'reconsider'}


def load_blocks():
    blocks = []
    for name in FILES:
        with open(os.path.join(QDIR, name), encoding='utf-8') as f:
            for block in yaml.safe_load_all(f):
                if isinstance(block, dict):
                    block['_file'] = name
                    blocks.append(block)
    return blocks


BLOCKS = load_blocks()
BY_ID = {b['id']: b for b in BLOCKS if 'id' in b}


class FakeList(da_stub.DAList):
    pass


def _add_list_helpers(ns):
    """Give DALists the .table / .add_action used in screen text."""
    for key, val in list(ns.items()):
        if isinstance(val, da_stub.DAList):
            new = FakeList(val)
            new.table = '[table of ' + key + ']'
            new.add_action = lambda label='Add', **kw: '<button>' + label + '</button>'
            ns[key] = new


def namespace(answers):
    ns = {}
    ns.update({k: getattr(da_stub, k) for k in dir(da_stub) if not k.startswith('_')})
    ns.update({k: getattr(msa_util, k) for k in msa_util.__all__})
    ns['url_action'] = lambda action, **kw: '#' + action
    ns['defined'] = lambda name: name in ns
    ns['name_suffix'] = lambda: ['Jr.', 'Sr.']
    ns['states_list'] = lambda: {'CA': 'California'}
    ns.update(answers)
    _add_list_helpers(ns)
    return ns


def run_code(ns):
    for block_id in CODE_ORDER:
        if block_id in CHILD_ONLY and not ns['has_minor_children']:
            continue
        if block_id == 'case type' and 'relationship_type' in ns:
            continue  # docassemble runs it only while the variables are undefined
        exec(compile(BY_ID[block_id]['code'], block_id, 'exec'), ns)
    for block in BLOCKS:
        if block.get('template') and 'content' in block:
            ns[block['template']] = render_mako(block['content'], ns)


class LazyUndefined:
    """Like docassemble: an undefined name fails only when it is used."""
    def _fail(self, *args, **kwargs):
        raise NameError('undefined variable used in Mako text')

    __bool__ = __str__ = __call__ = __getattr__ = __getitem__ = __iter__ = __len__ = _fail
    __eq__ = __ne__ = __lt__ = __gt__ = __add__ = __radd__ = __sub__ = __rsub__ = _fail
    __hash__ = object.__hash__


mako.runtime.UNDEFINED = LazyUndefined()


def render_mako(text, ns):
    return Template(text).render(**ns)


def mako_strings(obj, key=None):
    """Every string in a block that docassemble would treat as Mako."""
    if key in SKIP_KEYS:
        return
    if isinstance(obj, str):
        if '${' in obj or re.search(r'^\s*%', obj, re.M):
            yield obj
    elif isinstance(obj, dict):
        for k, v in obj.items():
            if k.startswith('_'):
                continue
            if isinstance(k, str) and '${' in k:
                yield k
            yield from mako_strings(v, k)
    elif isinstance(obj, list):
        for v in obj:
            yield from mako_strings(v, key if key in ('fields', 'choices', 'review', 'buttons', 'attachments') else None)


SCREEN_RESULTS = {}


@pytest.fixture(params=sorted(msa_scenarios.SCENARIOS))
def scenario(request):
    answers = msa_scenarios.SCENARIOS[request.param]()
    ns = namespace(answers)
    run_code(ns)
    return request.param, ns


def test_code_blocks(scenario):
    name, ns = scenario
    for heading in ('Must be resolved before judgment', 'For attorney review', 'Key terms'):
        assert heading in ns['drafting_memo'], 'memo heading lost (Mako treats ## as a comment)'
    if name == 'full_case':
        # Typed numbering and bullets are stripped; blank lines are dropped.
        assert len(ns['pet_property']) == 5
        assert ns['pet_property'][0].startswith('The real property commonly known as 123 Main Street')
        assert ns['pet_property'][2] == 'Schwab savings account ending in 2222'
        assert len(ns['resp_property']) == 3 and len(ns['pet_debts']) == 2
        assert ns['final_status'] == 'waived'
        assert any('FL-144' in t for t in ns['issues_todo'])
        assert not any('preliminary Declaration' in r for r in ns['issues_required'])
        assert ns['caption_name'] == 'Dana Lee' and ns['caption_for'].startswith('Attorney for Petitioner')
        assert ns['cs_deviates'] and ns['cs_below_guideline']
        assert ns['addon_pet_share'] == 40
        assert ns['long_duration'] is True
    if name == 'rdp_sale_waiver':
        assert ns['pet_property'] == [] and len(ns['resp_property']) == 2
        assert ns['final_status'] == 'pending'
        assert ns['spouse_word'] == 'domestic partner'
        assert any('pregnant' in i for i in ns['issues_required'])


def test_validation_code_accepts_sample_answers(scenario):
    _, ns = scenario
    for block in BLOCKS:
        if 'validation code' not in block:
            continue
        local = dict(ns)
        if '[i]' in block['validation code']:
            local['i'] = 0
        try:
            exec(block['validation code'], local)
        except NOT_APPLICABLE:
            pass


def test_screen_text_renders(scenario):
    name, ns = scenario
    for block in BLOCKS:
        if 'id' not in block or 'code' in block and 'question' not in block:
            continue
        local = dict(ns)
        local['i'] = 0
        ok = True
        for text in mako_strings(block):
            try:
                render_mako(text, local)
            except NOT_APPLICABLE:
                ok = False
                break
        SCREEN_RESULTS.setdefault(block['id'], set())
        if ok:
            SCREEN_RESULTS[block['id']].add(name)


def test_every_screen_rendered_somewhere():
    if len(SCREEN_RESULTS) == 0:
        pytest.skip('run with the screen test')
    never = sorted(k for k, v in SCREEN_RESULTS.items() if not v)
    assert not never, 'These blocks never rendered in any scenario: %s' % never


def test_table_columns(scenario):
    _, ns = scenario
    for block in BLOCKS:
        if 'table' not in block or 'rows' not in block:
            continue
        for row in ns[block['rows']]:
            for col in block['columns']:
                for expr in col.values():
                    eval(expr, dict(ns, row_item=row))


def _jinja_env():
    env = jinja2.Environment(undefined=jinja2.StrictUndefined)
    env.filters['manual_line_breaks'] = lambda s: s
    return env


def test_docx_renders(scenario, tmp_path):
    name, ns = scenario
    ns['sec'].reset()
    tpl = DocxTemplate(TEMPLATE)
    tpl.render(ns, jinja_env=_jinja_env())
    out = tmp_path / (name + '.docx')
    tpl.save(str(out))
    doc = Document(str(out))
    body = '\n'.join(p.text for p in doc.paragraphs)
    tables = '\n'.join(c.text for t in doc.tables for r in t.rows for c in r.cells)
    full = body + '\n' + tables
    assert '{{' not in full and '{%' not in full
    articles = [int(n) for n in re.findall(r'^ARTICLE (\d+)', body, re.M)]
    assert articles == list(range(1, len(articles) + 1))
    paras = re.findall(r'^(\d+)\.(\d+)\t', body, re.M)
    for art in set(a for a, _ in paras):
        subs = [int(s) for a, s in paras if a == art]
        assert subs == list(range(1, len(subs) + 1)), 'paragraph numbering in article ' + art
    assert ns['agreement_title'] in body
    for gone in ('Initials', 'Exhibit A', 'EXHIBIT A', 'Equalizing Payment', 'mediator'):
        assert gone not in full, gone + ' should no longer appear in the agreement'
    for kept in ('Omitted Assets and Debts.', 'Transfer Documents.', 'Characterization.'):
        assert kept in body
    footer = '\n'.join(p.text for s in doc.sections for p in s.footer.paragraphs)
    assert 'Initials' not in footer
    if ns['assets_status'] == 'none':
        assert 'There are no assets to be disposed of by the court.' in body
        assert 'Property Awarded and Confirmed' not in body
    if ns['debts_status'] == 'none':
        assert 'There are no debts to be disposed of by the court.' in body
    if name == 'full_case':
        assert 'CHILD CUSTODY AND PARENTING TIME' in body
        assert 'Family Code section 4065(a)' in body
        assert 'Property Awarded and Confirmed to Petitioner. The following property, whether community or separate, is awarded and confirmed to Petitioner as the separate property of Petitioner, along with any and all encumbrances on it, and Petitioner shall hold Respondent harmless from those encumbrances:' in body
        assert '(1)\tThe real property commonly known as 123 Main Street' in body
        assert '(5)\tThe family dog, Luna.' in body
        assert 'shall hold Petitioner harmless from these obligations:' in body
        assert 'Stipulation and Waiver of Final Declaration of Disclosure (form FL-144)' in body
        assert 'CALIFORNIA ALL-PURPOSE ACKNOWLEDGMENT' in body
        # The notary disclaimer sits inside a bordered one-cell table.
        boxed = [t for t in doc.tables if len(t.rows) == 1 and len(t.columns) == 1]
        assert len(boxed) == 2
        assert boxed[0].style.name == 'Table Grid'
        assert boxed[0].cell(0, 0).text.startswith('A notary public or other officer completing this certificate')
        assert 'Case No.: 25STFL01234' in full
        assert 'Dana Lee (SBN 123456)' in body and 'Attorney for Petitioner Maria E. Gomez' in body
        assert 'Maria Elena Torres' in body
    if name == 'rdp_sale_waiver':
        assert 'CHILD CUSTODY' not in body
        assert 'domestic partnership' in body
        assert 'Mutual Waiver of Support' in body
        assert 'Property Awarded and Confirmed to Maria.' in body
        assert '\nNone.\n' in body
    if name == 'bare_minimum':
        assert 'Attorney for Respondent' in body
    if name == 'long_marriage_pay':
        assert 'section 3591(c)' in body
        assert 'Family Code section 4336(a)' in body
    with open(out, 'rb') as f:
        assert io.BytesIO(f.read()).getbuffer().nbytes > 10000
