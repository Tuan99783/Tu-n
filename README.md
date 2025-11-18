# Gộp giáo án Word sang PDF mà không vỡ công thức

Script Python trong repo này giúp gộp nhiều file giáo án `.docx` (được soạn bằng Word + MathType) thành một giáo án tổng hợp theo lịch báo giảng hàng tuần, sau đó xuất thẳng ra PDF. Quá trình xử lý giữ nguyên toàn bộ đối tượng OLE nên công thức MathType không bị biến dạng.

## 1. Chuẩn bị môi trường

```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Trên Linux cần cài thêm LibreOffice (`sudo apt install libreoffice`) để chuyển DOCX → PDF. Nếu chạy Windows/macOS đã có Microsoft Word, có thể dùng `docx2pdf`, tuy nhiên script mặc định ưu tiên LibreOffice.

## 2. Chuẩn bị dữ liệu

1. Lưu các giáo án lẻ `.docx` trong một thư mục, ví dụ `data/lessons/`.
2. Tạo file lịch báo giảng từng tuần bằng CSV hoặc JSON.

### 2.1. Định dạng CSV

| Cột        | Bắt buộc | Ý nghĩa                                              |
|------------|----------|------------------------------------------------------|
| `docx_path`| ✓        | Đường dẫn tương đối tới file giáo án                  |
| `order`    |          | Thứ tự tiết (mặc định theo dòng nếu trống)           |
| `slot`     |          | Mã tiết, ví dụ `Tiết 1`                              |
| `date`     |          | Ngày dạy (định dạng ISO hoặc tự do)                  |
| `title`    |          | Tên bài/ghi chú để tiện kiểm tra                     |

Ví dụ: `examples/week01_schedule.csv`.

### 2.2. Định dạng JSON

```json
{
  "week": "2024-W36",
  "lessons": [
    {"order": 1, "title": "Ôn tập số hữu tỉ", "docx_path": "lessons/tiet01.docx"},
    {"order": 2, "title": "Phép cộng số hữu tỉ", "docx_path": "lessons/tiet02.docx"}
  ]
}
```

## 3. Chạy script gộp

```
python tools/merge_lesson_plans.py \
  --schedule examples/week01_schedule.csv \
  --lessons-root /path/to/data \
  --output-docx build/tuan01.docx
```

Tuỳ chọn:
- `--output-pdf build/tuan01.pdf`: đặt tên file PDF (mặc định cùng tên DOCX).
- `--skip-pdf`: chỉ tạo DOCX, bỏ qua convert PDF.
- `--verbose`: bật log chi tiết (debug thiếu file, lỗi LibreOffice, v.v.).

## 4. Vì sao công thức MathType không bị lỗi?

- Script dùng `docxcompose` để nối trực tiếp các phần thân DOCX nên giữ nguyên đối tượng OLE mà MathType sử dụng.
- Bước convert PDF dựa trên LibreOffice headless – công cụ này đọc đúng các object MathType nếu font đã được nhúng.
- Nếu PDF thiếu font đặc biệt, cài font đó vào hệ điều hành rồi chạy lại lệnh convert.

## 5. Mẹo vận hành

- Có thể tạo nhiều file lịch (theo tuần) và chạy script trong CI/CD hoặc cron để luôn có bản PDF mới nhất.
- Nếu cần trang bìa/ghi chú tuần, đặt một file template ở đầu danh sách trong lịch.
- Để tránh lỗi đường dẫn, nên tổ chức thư mục:

```
data/
  lessons/
    tiet01_on_tap.docx
    tiet02_cong.docx
examples/week01_schedule.csv
build/
```