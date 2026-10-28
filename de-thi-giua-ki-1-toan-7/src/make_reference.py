"""Tạo reference.docx (font Times New Roman 13, khổ A4, bảng có viền) cho pandoc."""
import re, shutil, subprocess, sys, tempfile, zipfile, os

out = sys.argv[1]
tmp = tempfile.mkdtemp()
base = os.path.join(tmp, "base.docx")
subprocess.run(["pandoc", "-o", base, "--print-default-data-file", "reference.docx"], check=True)
with zipfile.ZipFile(base) as z:
    files = {n: z.read(n) for n in z.namelist()}

s = files["word/styles.xml"].decode()
FONT = '<w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:eastAsia="Times New Roman" w:cs="Times New Roman" />'
s = re.sub(r'<w:rFonts w:asciiTheme="minorHAnsi"[^>]*/>', FONT, s, count=1)
s = s.replace('<w:sz w:val="24" />\n        <w:szCs w:val="24" />', '<w:sz w:val="26" />\n        <w:szCs w:val="26" />', 1)
s = s.replace('<w:spacing w:after="200" />', '<w:spacing w:after="0" w:line="264" w:lineRule="auto" />', 1)
s = s.replace('<w:spacing w:before="180" w:after="180" />', '<w:spacing w:before="40" w:after="40" />')
# Heading: Times New Roman, màu đen, căn giữa
s = re.sub(r'<w:rFonts w:asciiTheme="majorHAnsi"[^>]*/>', FONT, s)
s = re.sub(r'<w:color w:val="[0-9A-F]+" w:themeColor="accent1" />', '<w:color w:val="000000" />', s)
for lvl, size in (("1", 28), ("2", 26), ("3", 26)):
    s = re.sub(r'(w:styleId="Heading%s".*?<w:sz w:val=")\d+(" />\s*<w:szCs w:val=")\d+' % lvl,
               r'\g<1>%d\g<2>%d' % (size, size), s, count=1, flags=re.S)
s = re.sub(r'(w:styleId="Heading1".*?<w:spacing )w:before="480" w:after="0"', r'\1w:before="120" w:after="60"', s, count=1, flags=re.S)
s = re.sub(r'(w:styleId="Heading1".*?<w:pPr>)', r'\1<w:jc w:val="center" />', s, count=1, flags=re.S)
s = re.sub(r'(w:styleId="Heading2".*?<w:spacing )w:before="200" w:after="0"', r'\1w:before="160" w:after="40"', s, count=1, flags=re.S)
s = re.sub(r'(w:styleId="Heading3".*?<w:spacing )w:before="200" w:after="0"', r'\1w:before="80" w:after="20"', s, count=1, flags=re.S)
# Bảng: viền đơn toàn bộ
borders = ''.join('<w:%s w:val="single" w:sz="4" w:space="0" w:color="000000"/>' % b
                  for b in ("top", "left", "bottom", "right", "insideH", "insideV"))
s = s.replace('<w:tblInd w:w="0" w:type="dxa" />\n      <w:tblCellMar>',
              '<w:tblInd w:w="0" w:type="dxa" />\n      <w:tblBorders>%s</w:tblBorders>\n      <w:tblCellMar>' % borders, 1)

def pstyle(sid, ppr, rpr=""):
    return ('<w:style w:type="paragraph" w:customStyle="1" w:styleId="%s"><w:name w:val="%s" />'
            '<w:basedOn w:val="BodyText" /><w:qFormat /><w:pPr>%s</w:pPr>%s</w:style>' % (sid, sid, ppr, rpr))

tabs4 = '<w:tabs><w:tab w:val="left" w:pos="2410"/><w:tab w:val="left" w:pos="4820"/><w:tab w:val="left" w:pos="7230"/></w:tabs>'
tabs2 = '<w:tabs><w:tab w:val="left" w:pos="4820"/></w:tabs>'
extra = (pstyle("Center", '<w:jc w:val="center" /><w:spacing w:before="0" w:after="0" />')
         + pstyle("Options", tabs4 + '<w:spacing w:before="20" w:after="20" /><w:ind w:left="284" />')
         + pstyle("Options2", tabs2 + '<w:spacing w:before="20" w:after="20" /><w:ind w:left="284" />')
         + pstyle("Indent", '<w:spacing w:before="20" w:after="20" /><w:ind w:left="284" />')
         + pstyle("Right", '<w:jc w:val="right" /><w:spacing w:before="0" w:after="0" />'))
s = s.replace("</w:styles>", extra + "</w:styles>")
files["word/styles.xml"] = s.encode()

d = files["word/document.xml"].decode()
d = d.replace("<w:sectPr />", '<w:sectPr><w:pgSz w:w="11906" w:h="16838"/>'
              '<w:pgMar w:top="1021" w:right="1021" w:bottom="1021" w:left="1247" w:header="567" w:footer="567" w:gutter="0"/></w:sectPr>')
files["word/document.xml"] = d.encode()

with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
    for n, b in files.items():
        z.writestr(n, b)
shutil.rmtree(tmp)
