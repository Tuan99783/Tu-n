# Bộ 5 đề kiểm tra giữa học kì I – Toán 7 (KNTT), năm học 2026 – 2027

- `Bo_5_de_GKI_Toan7_KNTT_co_dap_an.docx`: cả 5 đề kèm cấu trúc đề và hướng dẫn chấm.
- `Bo_5_de_GKI_Toan7_KNTT_co_dap_an.pdf`: bản PDF gộp cả 5 đề và hướng dẫn chấm (21 trang).
- `Bo_5_de_GKI_Toan7_KNTT_chi_co_de.docx` / `.pdf`: chỉ có đề của 5 đề (không có đáp án), mỗi đề bắt đầu ở trang mới.
- `De_1_…docx` … `De_5_…docx`: từng đề riêng (đề + hướng dẫn chấm).

Cấu trúc: trắc nghiệm 3 điểm (4 câu nhiều lựa chọn, 1 câu đúng/sai 4 ý, 4 câu trả lời ngắn; 0,25 điểm/câu, ý) và tự luận 7 điểm. Thời gian làm bài 90 phút.
Mọi công thức đều là Equation của Word, có thể chỉnh sửa trực tiếp.

Phạm vi: Chương I (Bài 1 – 4), Bài 5; Chương III (Bài 8 – 11), Bài 12, Bài 13 (trường hợp c.c.c).

Sinh lại file: `python3 src/build.py .` (cần pandoc và matplotlib). Nội dung đề nằm trong `src/content.py`.

## Mã LaTeX (thư mục `latex/`)

- `Bo_5_de_GKI_Toan7_chi_co_de.tex`: 5 đề, không có đáp án.
- `Bo_5_de_GKI_Toan7_co_dap_an.tex`: cấu trúc đề + 5 đề kèm hướng dẫn chấm.
- `De_1_GKI_Toan7.tex` … `De_5_GKI_Toan7.tex`: từng đề kèm hướng dẫn chấm.

Mỗi file độc lập, biên dịch bằng **pdfLaTeX** (gói `vietnam` của vntex; hình vẽ bằng TikZ, không cần file ảnh), dùng được trên Overleaf.
Sinh lại: `python3 src/build_latex.py latex`.
