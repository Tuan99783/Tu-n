# -*- coding: utf-8 -*-
"""Sinh file Word (.docx) cho 5 đề + hướng dẫn chấm.  Cách dùng:
    python3 build.py <thư mục xuất>
Cần: pandoc, matplotlib.  Công thức được pandoc chuyển thành Equation (OMML) của Word.
"""
import math
import re
import os
import subprocess
import sys

from content import EXAMS

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, ".."))
BUILD = os.path.join(HERE, "_build")
FIG = os.path.join(BUILD, "fig")
os.makedirs(FIG, exist_ok=True)

TAB = "`<w:r><w:tab/></w:r>`{=openxml}"
PAGEBREAK = '```{=openxml}\n<w:p><w:r><w:br w:type="page"/></w:r></w:p>\n```\n'
LETTERS = "ABCD"
YEAR = "2026 – 2027"


def no_list(text):
    """Tránh để pandoc hiểu "a) ..." ở đầu dòng là danh sách tự động đánh số."""
    return re.sub(r"^([a-d])\) ", r"\1\\) ", text)


def div(style, body):
    body = no_list(body)
    return '::: {custom-style="%s"}\n%s\n:::\n' % (style, body)


def para(text):
    return text + "\n\n"


def image(name, width_cm):
    return div("Center", "![](%s){width=%scm}" % (os.path.join(FIG, name), width_cm))


def grid_table(rows, fracs, header=True):
    """Bảng lưới pandoc; rows: list các hàng, mỗi ô là list dòng (mỗi dòng là một đoạn)."""
    cells = []
    for row in rows:
        r = []
        for c in row:
            if isinstance(c, str):
                c = [c]
            lines = []
            for i, ln in enumerate(c):
                if i:
                    lines.append("")
                lines.append(ln)
            r.append(lines)
        cells.append(r)
    need = [max(len(ln) for row in cells for ln in row[j]) + 2 for j in range(len(fracs))]
    k = max(n / f for n, f in zip(need, fracs))
    widths = [int(math.ceil(k * f)) for f in fracs]
    sep = "+" + "+".join("-" * w for w in widths) + "+"
    hsep = "+" + "+".join("=" * w for w in widths) + "+"
    out = [sep]
    for i, row in enumerate(cells):
        h = max(len(c) for c in row)
        for li in range(h):
            out.append("|" + "|".join((" " + (row[j][li] if li < len(row[j]) else "")).ljust(widths[j])
                                      for j in range(len(widths))) + "|")
        out.append(hsep if (header and i == 0) else sep)
    return "\n".join(out) + "\n\n"


def header(no):
    md = div("Center", "**TRƯỜNG THCS ………………………**")
    md += div("Center", "**ĐỀ KIỂM TRA GIỮA HỌC KÌ I – NĂM HỌC %s**" % YEAR)
    md += div("Center", "**MÔN: TOÁN 7** – Sách *Kết nối tri thức với cuộc sống*")
    md += div("Center", "*Thời gian làm bài: 90 phút (không kể thời gian giao đề)*")
    md += div("Center", "**ĐỀ SỐ %d**" % no)
    md += para("Họ và tên: ……………………………………………… Lớp: ………… Số báo danh: …………")
    return md


def exam_md(no, e):
    md = header(no)
    md += "## A. TRẮC NGHIỆM (3,0 điểm)\n\n"
    md += para("**Phần I. Câu trắc nghiệm nhiều phương án lựa chọn** *(1,0 điểm)*. "
               "Thí sinh trả lời từ câu 1 đến câu 4. Mỗi câu hỏi thí sinh chỉ chọn một phương án.")
    for i, (q, opts, per_line, _) in enumerate(e["mcq"], 1):
        md += para("**Câu %d.** %s" % (i, q))
        items = ["**%s.** %s" % (LETTERS[j], o) for j, o in enumerate(opts)]
        if per_line == 4:
            md += div("Options", TAB.join(items))
        elif per_line == 2:
            md += div("Options2", items[0] + TAB + items[1]) + div("Options2", items[2] + TAB + items[3])
        else:
            md += "".join(div("Indent", it) for it in items)
    md += para("**Phần II. Câu trắc nghiệm đúng sai** *(1,0 điểm)*. "
               "Trong mỗi ý a), b), c), d) ở câu 5, thí sinh chọn đúng hoặc sai.")
    stem, items = e["tf"]
    md += para("**Câu 5.** " + stem)
    for j, (s, _) in enumerate(items):
        md += div("Indent", "%s) %s" % ("abcd"[j], s))
    md += para("**Phần III. Câu trắc nghiệm trả lời ngắn** *(1,0 điểm)*. Thí sinh trả lời từ câu 6 đến câu 9.")
    for i, (q, _) in enumerate(e["short"], 6):
        md += para("**Câu %d.** %s" % (i, q))
    md += "## B. TỰ LUẬN (7,0 điểm)\n\n"
    for title, pts, intro, parts, per_line, fig in e["essay"]:
        md += para("**%s** *(%s)*. %s" % (title, pts, intro))
        if fig:
            md += image(fig, 6.5 if "bai4" in fig else 5.5)
        if per_line == 2:
            for k in range(0, len(parts), 2):
                md += div("Options2", TAB.join(no_list(x) for x in parts[k:k + 2]))
        else:
            md += "".join(div("Indent", p) for p in parts)
    md += div("Center", "**——— HẾT ———**")
    md += div("Center", "*Giáo viên coi kiểm tra không giải thích gì thêm.*")
    return md


def key_md(no, e):
    md = "# HƯỚNG DẪN CHẤM – ĐỀ SỐ %d\n\n" % no
    md += "## A. TRẮC NGHIỆM (3,0 điểm)\n\n"
    md += para("**Phần I.** Mỗi câu trả lời đúng được 0,25 điểm.")
    md += grid_table([["Câu"] + [str(i) for i in range(1, 5)], ["Đáp án"] + ["**%s**" % m[3] for m in e["mcq"]]],
                     [0.2, 0.2, 0.2, 0.2, 0.2])
    md += para("**Phần II.** Mỗi ý trả lời đúng được 0,25 điểm.")
    md += grid_table([["Câu 5", "**a)**", "**b)**", "**c)**", "**d)**"],
                      ["Đáp án"] + ["**%s**" % ("Đúng" if t else "Sai") for _, t in e["tf"][1]]],
                     [0.2, 0.2, 0.2, 0.2, 0.2])
    md += para("**Phần III.** Mỗi câu trả lời đúng được 0,25 điểm.")
    md += grid_table([["Câu", "6", "7", "8", "9"], ["Đáp án"] + ["**%s**" % a for _, a in e["short"]]],
                     [0.2, 0.2, 0.2, 0.2, 0.2])
    md += "## B. TỰ LUẬN (7,0 điểm)\n\n"
    rows = [["**Bài**", "**Nội dung**", "**Điểm**"]]
    pending_imgs = []
    for label, lines, pts in e["key"]:
        cell = []
        for ln in lines:
            if ln.startswith("IMG:"):
                pending_imgs.append(ln[4:])
                cell.append("*(Hình vẽ ở cuối hướng dẫn chấm)*")
            elif ln.startswith("$="):
                # Dòng biến đổi bắt đầu bằng "=": thêm khoảng trắng văn bản để LibreOffice/WPS hiển thị đúng
                cell.append(r"$\text{ }=" + ln[2:])
            else:
                cell.append(ln)
        rows.append(["**%s**" % label if label else "", cell, pts])
    md += grid_table(rows, [0.08, 0.82, 0.10])
    md += para("*Lưu ý: Học sinh làm cách khác đúng vẫn cho điểm tối đa theo thang điểm tương ứng. "
               "Bài hình không vẽ hình hoặc vẽ hình sai không chấm phần tương ứng.*")
    for img in pending_imgs:
        md += para("**Hình vẽ bài 5:**")
        md += image(img, 5.5)
    return md


def intro_md():
    md = "# BỘ 5 ĐỀ KIỂM TRA GIỮA HỌC KÌ I – TOÁN 7\n\n"
    md += div("Center", "Sách *Kết nối tri thức với cuộc sống* – Năm học %s" % YEAR)
    md += "## 1. Cấu trúc đề (theo quy định của nhà trường)\n\n"
    md += grid_table([
        ["**Phần**", "**Hình thức**", "**Số câu / ý**", "**Điểm**"],
        ["A. Trắc nghiệm (30%)", ["Phần I. Nhiều phương án lựa chọn (4 lựa chọn)"], ["4 câu (câu 1 – 4)"], ["1,0"]],
        ["", ["Phần II. Đúng – Sai"], ["1 câu, 4 ý (câu 5)"], ["1,0"]],
        ["", ["Phần III. Trả lời ngắn"], ["4 câu (câu 6 – 9)"], ["1,0"]],
        ["B. Tự luận (70%)", ["6 bài"], ["Bài 1 – Bài 6"], ["7,0"]],
        ["**Tổng**", "", ["**Thời gian: 90 phút**"], ["**10,0**"]],
    ], [0.24, 0.42, 0.22, 0.12])
    md += para("Mỗi câu (ý) trắc nghiệm đúng được 0,25 điểm.")
    md += "## 2. Phạm vi kiến thức (theo PPCT Toán 7 – KNTT)\n\n"
    md += para("**Số và Đại số:** Chương I. Số hữu tỉ (Bài 1 – Bài 4, Luyện tập chung, Bài tập cuối chương I); "
               "Chương II – Bài 5. Làm quen với số thập phân vô hạn tuần hoàn (kèm làm tròn số).")
    md += para("**Hình học:** Chương III. Góc và đường thẳng song song (Bài 8 – Bài 11, Luyện tập chung, Bài tập cuối chương III); "
               "Chương IV – Bài 12. Tổng các góc trong một tam giác; Bài 13. Hai tam giác bằng nhau. "
               "Trường hợp bằng nhau thứ nhất (c.c.c).")
    md += "## 3. Phân bố nội dung phần tự luận (giống nhau ở cả 5 đề)\n\n"
    md += grid_table([
        ["**Bài**", "**Nội dung**", "**Mức độ**", "**Điểm**"],
        ["Bài 1", ["Thực hiện phép tính với số hữu tỉ, lũy thừa (tính hợp lí)"], ["Thông hiểu"], ["1,0"]],
        ["Bài 2", ["Tìm $x$ (quy tắc chuyển vế, lũy thừa)"], ["Thông hiểu – Vận dụng"], ["1,5"]],
        ["Bài 3", ["Bài toán thực tế với số hữu tỉ"], ["Vận dụng"], ["1,0"]],
        ["Bài 4", ["Góc ở vị trí đặc biệt, tia phân giác, hai đường thẳng song song"], ["Thông hiểu – Vận dụng"], ["1,5"]],
        ["Bài 5", ["Tổng ba góc của tam giác; tam giác bằng nhau (c.c.c)"], ["Thông hiểu – Vận dụng"], ["1,5"]],
        ["Bài 6", ["Bài toán nâng cao (tính tổng, so sánh lũy thừa, tìm $x$, giá trị nguyên)"], ["Vận dụng cao"], ["0,5"]],
    ], [0.1, 0.56, 0.22, 0.12])
    return md


def pandoc(md, out_docx, ref):
    src = out_docx[:-5] + ".md"
    src = os.path.join(BUILD, os.path.basename(src))
    with open(src, "w", encoding="utf-8") as f:
        f.write(md)
    subprocess.run(["pandoc", src, "-f", "markdown+raw_attribute+fenced_divs", "-o", out_docx,
                    "--reference-doc", ref, "--columns=60"], check=True)


def main():
    ref = os.path.join(BUILD, "reference.docx")
    subprocess.run([sys.executable, os.path.join(HERE, "make_reference.py"), ref], check=True)
    subprocess.run([sys.executable, os.path.join(HERE, "figures.py"), FIG], check=True)
    os.makedirs(OUT, exist_ok=True)
    all_md = intro_md()
    exams_only = []
    for no, e in enumerate(EXAMS, 1):
        one = exam_md(no, e) + PAGEBREAK + key_md(no, e)
        pandoc(one, os.path.join(OUT, "De_%d_GKI_Toan7_KNTT.docx" % no), ref)
        all_md += PAGEBREAK + one
        exams_only.append(exam_md(no, e))
    pandoc(all_md, os.path.join(OUT, "Bo_5_de_GKI_Toan7_KNTT_co_dap_an.docx"), ref)
    pandoc(PAGEBREAK.join(exams_only), os.path.join(OUT, "Bo_5_de_GKI_Toan7_KNTT_chi_co_de.docx"), ref)
    print("Đã tạo file trong", OUT)


if __name__ == "__main__":
    main()
