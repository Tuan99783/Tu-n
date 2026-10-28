# -*- coding: utf-8 -*-
"""Sinh mã LaTeX (pdfLaTeX + vntex, hình vẽ TikZ) cho 5 đề và hướng dẫn chấm.  Cách dùng:
    python3 build_latex.py <thư mục xuất>
Hình vẽ lấy từ figures.py: một đối tượng giả lập Axes ghi lại các nét vẽ rồi xuất thành TikZ.
"""
import math
import os
import sys

import figures
from content import EXAMS

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "latex"))
YEAR = "2026 -- 2027"
LETTERS = "ABCD"

PREAMBLE = r"""\documentclass[12pt,a4paper]{article}
\usepackage[utf8]{vietnam}
\usepackage{amsmath,amssymb}
\usepackage[a4paper,left=2cm,right=1.8cm,top=1.8cm,bottom=1.8cm]{geometry}
\usepackage{tikz}
\usepackage{array,tabularx,longtable}
\usepackage{enumitem}
\setlength{\parindent}{0pt}
\setlength{\parskip}{3pt}
\linespread{1.15}
\pagestyle{plain}

% Phương án trắc nghiệm: 4 phương án trên 1 dòng / 2 dòng / mỗi phương án 1 dòng
\newcommand{\bonpa}[4]{\par\noindent\begin{tabularx}{\linewidth}{@{\hspace{0.6cm}}XXXX@{}}
\textbf{A.} #1 & \textbf{B.} #2 & \textbf{C.} #3 & \textbf{D.} #4\end{tabularx}\par}
\newcommand{\haipa}[4]{\par\noindent\begin{tabularx}{\linewidth}{@{\hspace{0.6cm}}XX@{}}
\textbf{A.} #1 & \textbf{B.} #2\\ \textbf{C.} #3 & \textbf{D.} #4\end{tabularx}\par}
\newcommand{\motpa}[4]{\par\hspace*{0.6cm}\textbf{A.} #1\par\hspace*{0.6cm}\textbf{B.} #2\par
\hspace*{0.6cm}\textbf{C.} #3\par\hspace*{0.6cm}\textbf{D.} #4\par}
\newcommand{\cau}[1]{\par\medskip\textbf{Câu #1.}~}
\newcommand{\bai}[2]{\par\medskip\textbf{Bài #1} \textit{(#2)}.~}
\newcommand{\y}[1]{\par\hspace*{0.6cm}#1}
\newcommand{\phan}[1]{\par\bigskip{\large\textbf{#1}}\par\smallskip}
\setlength{\extrarowheight}{2pt}
"""


# ---------------------------------------------------------------- TikZ
class TikzAxes:
    """Thay thế matplotlib Axes: ghi lại các lệnh vẽ của figures.py dưới dạng TikZ."""

    def __init__(self):
        self.cmds = []

    def set_aspect(self, *a, **k):
        pass

    def axis(self, *a, **k):
        pass

    def plot(self, xs, ys=None, fmt=None, lw=1.2, **kw):
        if fmt == "o":  # ax.plot(x, y, "o"): chấm điểm
            self.cmds.append(r"\fill (%.3f,%.3f) circle (1.3pt);" % (xs, ys))
            return
        width = "0.7pt" if lw >= 1.1 else "0.5pt"
        path = " -- ".join("(%.3f,%.3f)" % (x, y) for x, y in zip(xs, ys))
        self.cmds.append(r"\draw[line width=%s] %s;" % (width, path))

    def add_patch(self, arc):
        (cx, cy), r = arc.center, arc.width / 2
        t1, t2 = arc.theta1, arc.theta2
        sx, sy = cx + r * math.cos(math.radians(t1)), cy + r * math.sin(math.radians(t1))
        self.cmds.append(r"\draw[line width=0.5pt] (%.3f,%.3f) arc[start angle=%g,end angle=%g,radius=%.3f];"
                         % (sx, sy, t1, t2, r))

    def text(self, x, y, s, fontsize=12, ha="left", va="center", **kw):
        if s.startswith("$"):
            label = s
        elif s.isalpha():
            label = "$%s$" % s
        else:
            label = s
        if fontsize < 12:
            label = r"{\small %s}" % label
        anchor = {"left": "west", "right": "east"}.get(ha, "center")
        if va == "bottom":
            anchor = "south" if anchor == "center" else "south " + anchor
        self.cmds.append(r"\node[anchor=%s,inner sep=1pt] at (%.3f,%.3f) {%s};" % (anchor, x, y, label))


def build_tikz():
    """Chạy các hàm vẽ trong figures.py với TikzAxes, trả về {tên hình: mã TikZ}."""
    out = {}
    for f in figures.ALL:
        rec = {}

        def new(w=4.2, h=2.6, rec=rec):
            ax = TikzAxes()
            rec["ax"], rec["w"] = ax, w
            return None, ax

        def save(fig, name, rec=rec):
            rec["name"] = name

        figures.new, figures.save = new, save
        f()
        scale = 1.15 if "bai4" in rec["name"] else 0.95
        body = "\n  ".join(rec["ax"].cmds)
        out[rec["name"]] = ("\\begin{center}\n\\begin{tikzpicture}[scale=%s,line cap=round,line join=round]\n  %s\n"
                            "\\end{tikzpicture}\n\\end{center}\n" % (scale, body))
    return out


TIKZ = build_tikz()


# ---------------------------------------------------------------- văn bản
def tex(s):
    """Chuyển chuỗi nội dung (văn bản + $...$) sang LaTeX: \\frac -> \\dfrac, ký tự đặc biệt."""
    s = s.replace("\\frac", "\\dfrac").replace("−", "$-$").replace("%", "\\%")
    return s


def header(no):
    return r"""\noindent
\begin{minipage}[t]{0.38\linewidth}\centering
TRƯỜNG THCS \dotfill\\[2pt]
\textbf{ĐỀ SỐ %d}
\end{minipage}\hfill
\begin{minipage}[t]{0.6\linewidth}\centering
\textbf{ĐỀ KIỂM TRA GIỮA HỌC KÌ I}\\
\textbf{NĂM HỌC %s}\\
\textbf{MÔN: TOÁN 7} -- Sách \textit{Kết nối tri thức với cuộc sống}\\
\textit{Thời gian làm bài: 90 phút (không kể thời gian giao đề)}
\end{minipage}

\medskip
Họ và tên: \dotfill\ Lớp: \makebox[2cm]{\dotfill}\ Số báo danh: \makebox[2.5cm]{\dotfill}
""" % (no, YEAR)


def exam_tex(no, e):
    t = "%% ===================== ĐỀ SỐ %d =====================\n" % no
    t += header(no)
    t += "\\phan{A. TRẮC NGHIỆM (3,0 điểm)}\n"
    t += ("\\textbf{Phần I. Câu trắc nghiệm nhiều phương án lựa chọn} \\textit{(1,0 điểm)}. "
          "Thí sinh trả lời từ câu 1 đến câu 4. Mỗi câu hỏi thí sinh chỉ chọn một phương án.\n")
    for i, (q, opts, per_line, _) in enumerate(e["mcq"], 1):
        macro = {4: "bonpa", 2: "haipa", 1: "motpa"}[per_line]
        t += "\\cau{%d} %s\n\\%s%s\n" % (i, tex(q), macro, "".join("{%s}" % tex(o) for o in opts))
    t += ("\n\\medskip\\textbf{Phần II. Câu trắc nghiệm đúng sai} \\textit{(1,0 điểm)}. "
          "Trong mỗi ý a), b), c), d) ở câu 5, thí sinh chọn đúng hoặc sai.\n")
    stem, items = e["tf"]
    t += "\\cau{5} %s\n" % tex(stem)
    for j, (s, _) in enumerate(items):
        t += "\\y{%s) %s}\n" % ("abcd"[j], tex(s))
    t += ("\n\\medskip\\textbf{Phần III. Câu trắc nghiệm trả lời ngắn} \\textit{(1,0 điểm)}. "
          "Thí sinh trả lời từ câu 6 đến câu 9.\n")
    for i, (q, _) in enumerate(e["short"], 6):
        t += "\\cau{%d} %s\n" % (i, tex(q))
    t += "\\phan{B. TỰ LUẬN (7,0 điểm)}\n"
    for title, pts, intro, parts, per_line, fig in e["essay"]:
        t += "\\bai{%s}{%s} %s\n" % (title.replace("Bài ", ""), pts, tex(intro))
        if fig:
            t += TIKZ[fig]
        if per_line == 2:
            for k in range(0, len(parts), 2):
                cells = [tex(p) for p in parts[k:k + 2]]
                t += ("\\par\\noindent\\begin{tabularx}{\\linewidth}{@{\\hspace{0.6cm}}XX@{}}%s\\end{tabularx}\n"
                      % " & ".join(cells))
        else:
            t += "".join("\\y{%s}\n" % tex(p) for p in parts)
    t += "\n\\bigskip\\begin{center}\\textbf{--------- HẾT ---------}\\\\\n\\textit{Giáo viên coi kiểm tra không giải thích gì thêm.}\\end{center}\n"
    return t


def key_tex(no, e):
    t = "\\begin{center}{\\large\\textbf{HƯỚNG DẪN CHẤM -- ĐỀ SỐ %d}}\\end{center}\n" % no
    t += "\\phan{A. TRẮC NGHIỆM (3,0 điểm)}\n"

    def row_table(head, vals):
        return ("\\begin{tabular}{|l|*{4}{>{\\centering\\arraybackslash}p{2cm}|}}\\hline\n"
                "%s \\\\ \\hline\nĐáp án & %s \\\\ \\hline\n\\end{tabular}\n\n"
                % (" & ".join(head), " & ".join("\\textbf{%s}" % v for v in vals)))

    t += "\\textbf{Phần I.} Mỗi câu trả lời đúng được 0,25 điểm.\n\n"
    t += row_table(["Câu", "1", "2", "3", "4"], [m[3] for m in e["mcq"]])
    t += "\\textbf{Phần II.} Mỗi ý trả lời đúng được 0,25 điểm.\n\n"
    t += row_table(["Câu 5", "a)", "b)", "c)", "d)"], ["Đúng" if v else "Sai" for _, v in e["tf"][1]])
    t += "\\textbf{Phần III.} Mỗi câu trả lời đúng được 0,25 điểm.\n\n"
    t += row_table(["Câu", "6", "7", "8", "9"], [tex(a) for _, a in e["short"]])
    t += "\\phan{B. TỰ LUẬN (7,0 điểm)}\n"
    t += ("\\begin{longtable}{|>{\\bfseries}c|p{0.76\\linewidth}|>{\\centering\\arraybackslash}p{1.3cm}|}\\hline\n"
          "Bài & \\multicolumn{1}{c|}{\\textbf{Nội dung}} & \\textbf{Điểm} \\\\ \\hline\\endhead\n")
    figs = []
    for label, lines, pts in e["key"]:
        cell = []
        for ln in lines:
            if ln.startswith("IMG:"):
                figs.append(ln[4:].strip())
                cell.append("\\textit{(Hình vẽ ở cuối hướng dẫn chấm)}")
            else:
                cell.append(tex(ln))
        body = " \\newline ".join(cell)
        if "\\dfrac" in body:  # chừa chỗ để phân số không chạm đường kẻ bảng
            body = "\\rule{0pt}{4ex}%s\\rule[-2.4ex]{0pt}{0pt}" % body
        t += "%s & %s & %s \\\\ \\hline\n" % (label, body, pts)
    t += "\\end{longtable}\n"
    t += ("\\textit{Lưu ý: Học sinh làm cách khác đúng vẫn cho điểm tối đa theo thang điểm tương ứng. "
          "Bài hình không vẽ hình hoặc vẽ hình sai không chấm phần tương ứng.}\n")
    for f in figs:
        t += "\n\\textbf{Hình vẽ bài 5:}\n" + TIKZ[f]
    return t


def intro_tex():
    return r"""\begin{center}
{\Large\textbf{BỘ 5 ĐỀ KIỂM TRA GIỮA HỌC KÌ I -- TOÁN 7}}\\[2pt]
Sách \textit{Kết nối tri thức với cuộc sống} -- Năm học %s
\end{center}
\phan{1. Cấu trúc đề}
\begin{tabular}{|p{3.2cm}|p{6.2cm}|p{3.6cm}|c|}\hline
\textbf{Phần} & \textbf{Hình thức} & \textbf{Số câu / ý} & \textbf{Điểm}\\\hline
A. Trắc nghiệm (30\%%) & Phần I. Nhiều phương án lựa chọn & 4 câu (câu 1 -- 4) & 1,0\\\cline{2-4}
 & Phần II. Đúng -- Sai & 1 câu, 4 ý (câu 5) & 1,0\\\cline{2-4}
 & Phần III. Trả lời ngắn & 4 câu (câu 6 -- 9) & 1,0\\\hline
B. Tự luận (70\%%) & 6 bài & Bài 1 -- Bài 6 & 7,0\\\hline
\textbf{Tổng} & & \textbf{Thời gian: 90 phút} & \textbf{10,0}\\\hline
\end{tabular}

Mỗi câu (ý) trắc nghiệm đúng được 0,25 điểm.
\phan{2. Phạm vi kiến thức (theo PPCT Toán 7 -- KNTT)}
\textbf{Số và Đại số:} Chương I. Số hữu tỉ (Bài 1 -- Bài 4); Chương II -- Bài 5. Làm quen với số thập phân vô hạn tuần hoàn.

\textbf{Hình học:} Chương III. Góc và đường thẳng song song (Bài 8 -- Bài 11); Chương IV -- Bài 12. Tổng các góc trong một tam giác; Bài 13. Hai tam giác bằng nhau. Trường hợp bằng nhau thứ nhất (c.c.c).
\phan{3. Phân bố nội dung phần tự luận}
\begin{tabular}{|c|p{9cm}|p{3.4cm}|c|}\hline
\textbf{Bài} & \textbf{Nội dung} & \textbf{Mức độ} & \textbf{Điểm}\\\hline
1 & Thực hiện phép tính với số hữu tỉ, lũy thừa & Thông hiểu & 1,0\\\hline
2 & Tìm $x$ (quy tắc chuyển vế, lũy thừa) & Thông hiểu -- Vận dụng & 1,5\\\hline
3 & Bài toán thực tế với số hữu tỉ & Vận dụng & 1,0\\\hline
4 & Góc ở vị trí đặc biệt, tia phân giác, hai đường thẳng song song & Thông hiểu -- Vận dụng & 1,5\\\hline
5 & Tổng ba góc của tam giác; tam giác bằng nhau (c.c.c) & Thông hiểu -- Vận dụng & 1,5\\\hline
6 & Bài toán nâng cao & Vận dụng cao & 0,5\\\hline
\end{tabular}
""" % YEAR


def document(body):
    return PREAMBLE + "\n\\begin{document}\n" + body + "\n\\end{document}\n"


def main():
    os.makedirs(OUT, exist_ok=True)
    files = {}
    exams = [exam_tex(no, e) for no, e in enumerate(EXAMS, 1)]
    keys = [key_tex(no, e) for no, e in enumerate(EXAMS, 1)]
    files["Bo_5_de_GKI_Toan7_chi_co_de.tex"] = document("\n\\newpage\n".join(exams))
    files["Bo_5_de_GKI_Toan7_co_dap_an.tex"] = document(
        intro_tex() + "".join("\n\\newpage\n" + ex + "\n\\newpage\n" + k for ex, k in zip(exams, keys)))
    for no, (ex, k) in enumerate(zip(exams, keys), 1):
        files["De_%d_GKI_Toan7.tex" % no] = document(ex + "\n\\newpage\n" + k)
    for name, content in files.items():
        with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
            f.write(content)
    print("Đã tạo %d file .tex trong %s" % (len(files), OUT))


if __name__ == "__main__":
    main()
