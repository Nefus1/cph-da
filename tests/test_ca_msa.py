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
    'preparer is attorney', 'party references', 'relationship words', 'marriage length',
    'child support final values', 'addon percentages', 'spousal summary text',
    'equalization numbers', 'equalization final values', 'additional terms paragraphs',
    'filename', 'status date', 'award lists', 'drafting issues',
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


def test_code_blocks_and_equalization(scenario):
    name, ns = scenario
    eq = ns['eq']
    assert round(eq['pet_net'] - eq['resp_net'], 2) == round(
        (2 * eq['payment']) * (1 if eq['payor'] == 'pet' else -1 if eq['payor'] == 'resp' else 0), 2)
    for heading in ('Must be resolved before judgment', 'For attorney review', 'Key terms'):
        assert heading in ns['drafting_memo'], 'memo heading lost (Mako treats ## as a comment)'
    if name == 'full_case':
        # House equity 430,000 + RAV4 16,000 + dog 0 to Petitioner;
        # F-150 28,000 + Fidelity community 25,000 + LLC 60,000 - Capital One 6,500 to Respondent.
        assert eq['pet_net'] == 446000.0
        assert eq['resp_net'] == 106500.0
        assert eq['payor'] == 'pet' and eq['payment'] == 169750.0
        assert ns['cs_deviates'] and ns['cs_below_guideline']
        assert ns['addon_pet_share'] == 40
        assert ns['long_duration'] is True
    if name == 'rdp_sale_waiver':
        assert ns['eq_mode'] == 'waive' and ns['eq_payor'] is None
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
    if name == 'full_case':
        assert 'CHILD CUSTODY AND PARENTING TIME' in body
        assert 'Family Code section 4065(a)' in body
        assert 'Interspousal Transfer Grant Deed' in body
        assert 'CALIFORNIA ALL-PURPOSE ACKNOWLEDGMENT' in body
        assert 'Case No.: 25STFL01234' in full
        assert 'Maria Elena Torres' in body
    if name == 'rdp_sale_waiver':
        assert 'CHILD CUSTODY' not in body
        assert 'domestic partnership' in body
        assert 'Mutual Waiver of Support' in body
        assert 'shall be listed for sale' in body
    if name == 'long_marriage_pay':
        assert 'section 3591(c)' in body
        assert 'Family Code section 4336(a)' in body
    with open(out, 'rb') as f:
        assert io.BytesIO(f.read()).getbuffer().nbytes > 10000
