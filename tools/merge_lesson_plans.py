#!/usr/bin/env python3
"""
Gộp nhiều giáo án Word theo lịch báo giảng và xuất PDF.

Yêu cầu:
  pip install -r requirements.txt
  - LibreOffice (soffice) hoặc docx2pdf (Windows/Mac có Word) để chuyển PDF.
"""

from __future__ import annotations

import argparse
import csv
import json
import logging
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List, Sequence

from docx import Document
from docxcompose.composer import Composer


LOGGER = logging.getLogger("lesson-plan-merger")


@dataclass(order=True)
class LessonSpec:
    order: int
    source: Path
    title: str | None = None
    slot: str | None = None
    date: str | None = None


class ScheduleFormatError(ValueError):
    """Ngoại lệ cho lịch không đúng định dạng."""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Gộp giáo án Word theo lịch báo giảng rồi xuất ra DOCX/PDF.",
    )
    parser.add_argument(
        "--schedule",
        required=True,
        type=Path,
        help="Đường dẫn file lịch (CSV/JSON).",
    )
    parser.add_argument(
        "--lessons-root",
        type=Path,
        default=Path("."),
        help="Thư mục chứa các giáo án gốc (mặc định: thư mục hiện tại).",
    )
    parser.add_argument(
        "--output-docx",
        type=Path,
        required=True,
        help="Đường dẫn file DOCX gộp (ví dụ build/tuan01.docx).",
    )
    parser.add_argument(
        "--output-pdf",
        type=Path,
        help="Đường dẫn file PDF (mặc định cùng tên output-docx).",
    )
    parser.add_argument(
        "--skip-pdf",
        action="store_true",
        help="Chỉ tạo DOCX, bỏ qua bước convert PDF.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="In log chi tiết.",
    )
    return parser.parse_args()


def load_schedule(schedule_path: Path, lessons_root: Path) -> List[LessonSpec]:
    if not schedule_path.exists():
        raise FileNotFoundError(f"Không tìm thấy file lịch: {schedule_path}")

    ext = schedule_path.suffix.lower()
    if ext == ".csv":
        lessons = _load_csv_schedule(schedule_path, lessons_root)
    elif ext == ".json":
        lessons = _load_json_schedule(schedule_path, lessons_root)
    else:
        raise ScheduleFormatError("Hiện chỉ hỗ trợ CSV hoặc JSON cho file lịch.")

    if not lessons:
        raise ScheduleFormatError("Danh sách tiết trống.")

    lessons.sort()
    return lessons


def _load_csv_schedule(schedule_path: Path, lessons_root: Path) -> List[LessonSpec]:
    lessons: List[LessonSpec] = []
    with schedule_path.open(encoding="utf-8-sig") as csv_file:
        reader = csv.DictReader(csv_file)
        required_field = "docx_path"
        if not reader.fieldnames or required_field not in reader.fieldnames:
            raise ScheduleFormatError(
                f"CSV phải có cột '{required_field}'. "
                "Có thể thêm 'order', 'title', 'slot', 'date' tuỳ chọn."
            )
        for idx, row in enumerate(reader, start=1):
            docx_rel = row.get(required_field, "").strip()
            if not docx_rel:
                continue
            order_value = row.get("order") or row.get("stt") or row.get("slot") or str(idx)
            try:
                order = int(order_value)
            except ValueError as exc:
                raise ScheduleFormatError(
                    f"Không thể chuyển '{order_value}' sang số thứ tự (dòng {idx})."
                ) from exc
            source_path = (lessons_root / docx_rel).expanduser().resolve()
            if not source_path.exists():
                raise FileNotFoundError(f"Thiếu giáo án: {source_path}")
            lessons.append(
                LessonSpec(
                    order=order,
                    source=source_path,
                    title=row.get("title") or row.get("name"),
                    slot=row.get("slot"),
                    date=row.get("date"),
                )
            )
    return lessons


def _load_json_schedule(schedule_path: Path, lessons_root: Path) -> List[LessonSpec]:
    lessons: List[LessonSpec] = []
    data = json.loads(schedule_path.read_text(encoding="utf-8"))
    if isinstance(data, list):
        raw_lessons: Sequence[dict] = data
    elif isinstance(data, dict):
        raw_lessons = data.get("lessons", [])
    else:
        raise ScheduleFormatError("JSON phải là mảng hoặc có key 'lessons'.")
    if not isinstance(raw_lessons, Sequence):
        raise ScheduleFormatError("JSON phải có mảng 'lessons'.")
    for idx, item in enumerate(raw_lessons, start=1):
        docx_rel = (item.get("docx_path") or item.get("path") or "").strip()
        if not docx_rel:
            continue
        order_value = item.get("order") or item.get("slot") or idx
        if isinstance(order_value, str):
            try:
                order = int(order_value)
            except ValueError as exc:
                raise ScheduleFormatError(
                    f"order '{order_value}' không phải số (phần tử {idx})."
                ) from exc
        else:
            order = int(order_value)
        source_path = (lessons_root / docx_rel).expanduser().resolve()
        if not source_path.exists():
            raise FileNotFoundError(f"Thiếu giáo án: {source_path}")
        lessons.append(
            LessonSpec(
                order=order,
                source=source_path,
                title=item.get("title"),
                slot=item.get("slot"),
                date=item.get("date"),
            )
        )
    return lessons


def merge_docx(lesson_files: Sequence[Path], output_path: Path) -> None:
    LOGGER.info("Bắt đầu gộp %d giáo án...", len(lesson_files))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    base_doc = Document(str(lesson_files[0]))
    composer = Composer(base_doc)
    for lesson in lesson_files[1:]:
        composer.append(Document(str(lesson)))
    composer.save(str(output_path))
    LOGGER.info("Đã tạo DOCX gộp tại %s", output_path)


def convert_docx_to_pdf(docx_path: Path, pdf_path: Path) -> None:
    soffice = shutil.which("soffice") or shutil.which("libreoffice")
    if not soffice:
        raise RuntimeError(
            "Không tìm thấy LibreOffice (soffice). "
            "Vui lòng cài đặt để chuyển DOCX sang PDF."
        )
    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        soffice,
        "--headless",
        "--convert-to",
        "pdf",
        "--outdir",
        str(pdf_path.parent),
        str(docx_path),
    ]
    LOGGER.info("Đang chuyển DOCX → PDF bằng LibreOffice...")
    subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    generated_pdf = pdf_path.parent / f"{docx_path.stem}.pdf"
    if generated_pdf != pdf_path:
        generated_pdf.replace(pdf_path)
    LOGGER.info("Đã tạo PDF tại %s", pdf_path)


def main() -> None:
    args = parse_args()
    args.schedule = args.schedule.expanduser()
    if not args.schedule.is_absolute():
        args.schedule = args.schedule.resolve()
    args.lessons_root = args.lessons_root.expanduser().resolve()
    args.output_docx = args.output_docx.expanduser()
    if not args.output_docx.is_absolute():
        args.output_docx = args.output_docx.resolve()
    if args.output_pdf:
        args.output_pdf = args.output_pdf.expanduser()
        if not args.output_pdf.is_absolute():
            args.output_pdf = args.output_pdf.resolve()
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s %(message)s",
    )

    try:
        lessons = load_schedule(args.schedule, args.lessons_root)
        lesson_paths = [lesson.source for lesson in lessons]
        merge_docx(lesson_paths, args.output_docx)
        export_pdf = not args.skip_pdf
        pdf_target = args.output_pdf or args.output_docx.with_suffix(".pdf")
        if export_pdf:
            convert_docx_to_pdf(args.output_docx, pdf_target)
        else:
            LOGGER.info("Bỏ qua bước xuất PDF theo tùy chọn skip-pdf.")
    except Exception as exc:  # pylint: disable=broad-except
        LOGGER.error("%s", exc)
        if LOGGER.isEnabledFor(logging.DEBUG):
            raise
        sys.exit(1)


if __name__ == "__main__":
    main()
