"""Print the text of a DOCX (body, tables, footers) for diffing templates."""
import sys

from docx import Document

doc = Document(sys.argv[1])
for par in doc.paragraphs:
    print(par.text)
for table in doc.tables:
    for row in table.rows:
        print(' | '.join(cell.text for cell in row.cells))
for section in doc.sections:
    for par in section.footer.paragraphs:
        print(par.text)
