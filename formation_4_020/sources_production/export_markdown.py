"""Exporter une version Markdown avec tableaux et figures du dossier Word."""
from pathlib import Path
import os,re
from docx import Document
from docx.text.paragraph import Paragraph
from docx.table import Table
root=Path(os.environ.get('FORMATION_ROOT',str(Path(__file__).resolve().parents[1])))
doc=Document(root/'documents/Dossier_pedagogique_4_020.docx');lines=[]
def escape(t):return t.replace('|','\\|').replace('\n','<br>')
for e in doc.element.body:
 if e.tag.endswith('}p'):
  p=Paragraph(e,doc);t=p.text.strip()
  if not t:continue
  if p.style.name.startswith('Heading'):
   n=int(p.style.name[-1]);lines+=['#'*n+' '+t,'']
  else:
   m=re.match(r'Figure (J[12]-\d{3})\.',t)
   if m:lines+=['!['+m.group(1)+'](../illustrations/'+m.group(1)+'.png)','']
   lines+=[t,'']
 elif e.tag.endswith('}tbl'):
  rows=Table(e,doc).rows
  for i,r in enumerate(rows):
   lines+=['| '+' | '.join(escape(c.text) for c in r.cells)+' |']
   if i==0:lines+=['| '+' | '.join('---' for _ in r.cells)+' |']
  lines+=['']
(root/'documents/Dossier_pedagogique_4_020.md').write_text('\n'.join(lines),encoding='utf-8')
