# CPH Docassemble Hub

`docassemble.cphda` is the firm's central package of [Docassemble](https://docassemble.org)
interviews and document templates for California practice. Each interview is a
guided questionnaire with practice notes, statutory help, and a defined-terms
glossary that assembles a finished Word/PDF document and an attorney drafting memo.

| Interview | File | Produces |
|---|---|---|
| Hub (start page) | `hub.yml` | Links to every interview |
| California Marital Settlement Agreement | `ca_msa.yml` | MSA or domestic partnership settlement agreement (DOCX + PDF), drafting memo (PDF + DOCX) |

## California Marital Settlement Agreement

A full MSA questionnaire for dissolution, legal separation, or nullity, for
spouses or registered domestic partners. It is organized into navigable
sections, and each one has a review screen:

1. **Case and parties.** Preparer role, case type, county and case number,
   party names and how the agreement refers to them, dates of marriage and
   separation (Fam. Code § 70), counsel, and translation.
2. **Children.** Children's names and birthdates, legal and physical custody,
   regular schedule (alternating weeks, 2-2-5-5, 2-2-3, alternate weekends,
   supervised, custom, or an attached FL-341), holidays, travel, communication,
   right of first refusal, and UCCJEA/§ 3048 recitals.
3. **Child support.** Incomes, timeshare, guideline amount, and the agreed
   amount. If the agreed amount differs from guideline, the interview requires
   the Fam. Code § 4065(a) declarations, and blocks a deviation when support
   is assigned to the county. It also covers § 4062 add-ons (equal,
   income-proportional, or custom split), health insurance, the dependency
   exemption and Form 8332, life insurance, and the earnings assignment or a
   § 5260 stay.
4. **Spousal / partner support.** Pay, mutual waiver, or reservation. Covers
   fixed-term, month-count, Richmond, or open-ended duration;
   modifiability (§ 3591(c)); remarriage (§ 4337); long-duration jurisdiction
   (§ 4336), which the interview detects automatically; cohabitation (§ 4323);
   the Gavron notice; and arrears.
5. **Property and debts.** Separate schedules for real estate, vehicles,
   financial accounts, retirement plans, businesses, other assets, and debts.
   Each item is characterized as community, mixed, or separate. The interview
   handles buyouts with refinance and deed deadlines, sales with occupancy and
   carrying costs, and QDRO/IRA division. A live summary computes the
   **§ 2550 equalizing payment**, which the parties can accept, renegotiate, or
   waive. Epstein, Watts, and § 2640 waivers are also covered.
6. **Other terms.** Taxes, attorney's fees, restoration of former names,
   insurance, estate planning (Prob. Code §§ 5600, 6122), dispute resolution,
   merger into the judgment, CCP § 664.6, and free-form additional provisions.
7. **Disclosures and signing.** Preliminary and final declarations of
   disclosure (including the § 2105(d) waiver language and FL-144), notary
   acknowledgment pages, and signature dates.
8. **Review and documents.** A final review lists every item that blocks
   judgment. The agreement renumbers its articles automatically as clauses
   drop in or out. Exhibit A is the schedule of assets, debts, and the equal
   division. The **drafting memo** lists blocking issues, attorney-review
   flags, and a filing checklist (FL-191, FL-192, FL-195/FL-435, FL-144, QDROs,
   deeds, DMV, the § 2339 status date).

Output follows house style: Times New Roman 12 pt with no line numbers, for use
on the firm's own pleading paper. The captioned "attachment" format adds the
attorney header and court caption.

## Repository layout

```
docassemble/cphda/
  msa_util.py                  # asset/debt classes, equalization math, section counter
  data/questions/
    hub.yml                    # start page listing all interviews
    cph_shared.yml             # shared CSS/footer; include first in every interview
    ca_msa.yml                 # MSA entry point: metadata, sections, interview order, case & parties
    ca_msa_children_support.yml
    ca_msa_property.yml
    ca_msa_terms.yml
    ca_msa_documents.yml       # final review, drafting memo, attachments
    ca_msa_glossary.yml        # {term} popover definitions
  data/templates/ca_msa.docx   # generated - do not edit by hand (see below)
  data/static/cph.css
tools/build_ca_msa_template.py # source of the MSA clause text; builds ca_msa.docx
tests/                         # offline tests with docassemble stubs
```

## Installing on the docassemble server

1. Go to **Package Management** and install from GitHub:
   `https://github.com/nefus1/cph-da` (choose the branch to deploy).
2. Start the hub at `/start/cphda/hub` or the MSA directly at `/start/cphda/ca_msa`.

To work on the package in the **Playground** instead, upload the
`data/questions/*.yml` files to Questions, `ca_msa.docx` to Templates,
`cph.css` to Static, and `msa_util.py` to Modules.

## Editing the MSA clause text

Do not edit `ca_msa.docx` in Word. The clause text lives in
`tools/build_ca_msa_template.py`, which places every Jinja2 tag in a single
Word run, so Word cannot split tags or insert smart quotes into them. To change
the text:

```bash
pip install -r requirements-dev.txt
python tools/build_ca_msa_template.py      # rewrites data/templates/ca_msa.docx
python -m pytest -q tests                   # renders four sample cases
```

Conventions used in the builder:

- `article('TITLE')` starts a numbered article. `para('Heading', 'text')` adds
  a numbered paragraph. Numbers come from `sec.article()` and `sec.para()`, so
  conditional clauses never leave gaps.
- Put conditional blocks between `ctl('{%p if ... %}')` and
  `ctl('{%p endif %}')`.
- Wrap any free text a user types that ends a sentence in `period(...)`, so
  "6:00 p.m." does not become "6:00 p.m..".

## Adding a new interview

1. Create `data/questions/<name>.yml` and include `cph_shared.yml` first.
2. Follow the MSA's structure: `metadata` → `features`/`sections` → `objects` →
   a single `interview order` block → questions in screen order, each with an
   `id`, a `section`, and a `help` block that cites the controlling authority.
3. Put Python helpers in a module under `docassemble/cphda/`, not in YAML.
4. Add the interview to the `catalog` in `hub.yml`.
5. Add sample scenarios and a test under `tests/`.

## Tests and checks

```bash
python -m pytest -q tests
for f in docassemble/cphda/data/questions/*.yml; do dayamlchecker --no-url-check "$f"; done
```

The tests stub Docassemble's objects and, for each sample case, they:

- run the interview's code blocks and validation code;
- render every Mako string on every screen (each screen must render in at
  least one case);
- evaluate the table columns;
- render the DOCX, checking that no tags are left and that the article and
  paragraph numbering is consecutive.

CI runs the same checks on every push. dayamlchecker's `EA510` (yes/no
shorthand) is a style preference and is ignored.

The tests do not replace a live run on the server. After any change, run the
interview in the Playground at least once and download both documents.

---

These interviews assemble drafts for review by a California-licensed attorney.
They are not legal advice.
