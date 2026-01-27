# streamlit_pdf_reader_final_fixed2.py
"""
Advanced PDF Reader — Final fixed version (Pylance-clean)
Minor return-type coercions added so static type checkers cannot infer mixed return unions.

Aggressive multi-engine extraction with robust type-safe checks.
"""

from typing import Any, Dict, List, Optional, Tuple, Callable
import streamlit as st
from pathlib import Path
import tempfile, os, io, subprocess, json
from datetime import datetime

# imaging / OCR / PDF libs
import numpy as np
from PIL import Image
import pytesseract
import pdfplumber
import fitz  # PyMuPDF
from pdfminer.high_level import extract_text as pdfminer_extract_text
from PyPDF2 import PdfReader
import cv2

st.set_page_config(layout="wide", page_title="Advanced PDF Reader (Fixed)")

# -------------------------
# Type-safe helpers
# -------------------------
def safe_str_nonempty(x: Any) -> bool:
    """Return True if x is a non-empty string after strip. Handles None/bytes/others safely."""
    if x is None:
        return False
    if isinstance(x, str):
        return bool(x.strip())
    if isinstance(x, bytes):
        try:
            return bool(x.decode("utf-8", errors="ignore").strip())
        except Exception:
            return False
    return False

def safe_get_text_from_ocr_field(val: Any) -> str:
    """Normalize OCR/text-like values to a stripped string. Never raises."""
    if val is None:
        return ""
    if isinstance(val, str):
        return val.strip()
    if isinstance(val, bytes):
        try:
            return val.decode("utf-8", errors="ignore").strip()
        except Exception:
            return ""
    try:
        return str(val).strip()
    except Exception:
        return ""

def safe_len(obj: Any) -> int:
    """Return len(obj) if it supports __len__, else 0."""
    try:
        return len(obj)  # type: ignore[arg-type]
    except Exception:
        return 0

# -------------------------
# OpenCV / image helpers (type-safe) - normalize fixed (dst not None)
# -------------------------
def pil_to_cv2(pil_img: Optional[Image.Image]) -> np.ndarray:
    """Convert PIL image to OpenCV BGR numpy array. Return tiny black array on error."""
    if pil_img is None:
        return np.zeros((1, 1), dtype=np.uint8)
    arr = np.asarray(pil_img)
    if arr.ndim == 2:
        return arr
    if arr.ndim == 3 and arr.shape[2] == 3:
        return cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)
    if arr.ndim == 3 and arr.shape[2] == 4:
        return cv2.cvtColor(arr, cv2.COLOR_RGBA2BGR)
    try:
        return arr.astype(np.uint8)
    except Exception:
        return np.zeros((1,1), dtype=np.uint8)

def cv2_to_pil(img: Optional[np.ndarray]) -> Image.Image:
    """Convert OpenCV BGR/gray to PIL RGB. Return white 1x1 on error."""
    if img is None:
        return Image.new("RGB", (1,1), "white")
    if img.ndim == 2:
        try:
            return Image.fromarray(img)
        except Exception:
            return Image.new("RGB", (1,1), "white")
    try:
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        return Image.fromarray(img_rgb)
    except Exception:
        return Image.new("RGB", (1,1), "white")

def safe_cv_normalize(src: Any) -> np.ndarray:
    """
    Normalize image to uint8 safely; always returns numpy.ndarray.
    IMPORTANT: create dst explicitly (np.empty_like) and pass it to cv2.normalize
    to satisfy type checker (no dst=None).
    """
    if src is None:
        return np.zeros((1,1), dtype=np.uint8)
    if not hasattr(src, "dtype"):
        try:
            src = np.array(src, dtype=np.uint8)
        except Exception:
            return np.zeros((1,1), dtype=np.uint8)
    try:
        dst = np.empty_like(src)
        cv2.normalize(src, dst, 0, 255, cv2.NORM_MINMAX)
        if dst.dtype != np.uint8:
            dst = np.clip(dst, 0, 255).astype(np.uint8)
        return dst
    except Exception:
        try:
            return np.clip(np.asarray(src), 0, 255).astype(np.uint8)
        except Exception:
            return np.zeros((1,1), dtype=np.uint8)

def deskew_image(gray: np.ndarray) -> np.ndarray:
    """Attempt to deskew grayscale image. Return original on failure."""
    if gray is None or gray.size == 0:
        return gray
    try:
        blur = cv2.GaussianBlur(gray, (5,5), 0)
        thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
        coords = np.column_stack(np.where(thresh > 0))
        if coords.shape[0] < 10:
            return gray
        angle = cv2.minAreaRect(coords)[-1]
        if angle < -45:
            angle = -(90 + angle)
        else:
            angle = -angle
        (h, w) = gray.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(gray, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
        return rotated
    except Exception:
        return gray

def preprocess_for_ocr(pil_img: Optional[Image.Image], upscale_factor: int = 2, do_deskew: bool = True) -> Image.Image:
    """Preprocess PIL image for OCR; always returns a PIL Image."""
    if pil_img is None:
        return Image.new("RGB", (1,1), "white")
    img = pil_img.convert("RGB")
    cv_img = pil_to_cv2(img)
    # grayscale
    try:
        gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY) if cv_img.ndim == 3 else cv_img
    except Exception:
        gray = cv_img
    # deskew if requested
    if do_deskew:
        try:
            gray = deskew_image(gray)
        except Exception:
            pass
    # normalize safely (uses dst explicitly)
    gray = safe_cv_normalize(gray)
    # denoise
    try:
        gray = cv2.bilateralFilter(gray, d=9, sigmaColor=75, sigmaSpace=75)
    except Exception:
        pass
    # adaptive threshold
    try:
        th = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                   cv2.THRESH_BINARY, 31, 10)
    except Exception:
        th = gray
    # upscale
    try:
        h, w = th.shape
        up = cv2.resize(th, (max(1, w * upscale_factor), max(1, h * upscale_factor)), interpolation=cv2.INTER_CUBIC)
    except Exception:
        up = th
    return cv2_to_pil(up)

# -------------------------
# Multi-engine extractors (type-safe returns)
# -------------------------
def run_pdftotext(pdf_path: str, page_no: Optional[int] = None, encoding: str = "UTF-8") -> Optional[str]:
    """Return extracted text via pdftotext CLI or None."""
    cmd = ["pdftotext", "-enc", encoding]
    if page_no is not None:
        cmd += ["-f", str(page_no), "-l", str(page_no)]
    cmd += [pdf_path, "-"]
    try:
        p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False, timeout=30)
        out = p.stdout.decode("utf-8", errors="replace")
        if safe_str_nonempty(out):
            return out
    except Exception:
        pass
    return None

def fitz_extract_text_words(pdf_path: str, page_no: int) -> Tuple[Optional[str], List[Dict[str, Any]]]:
    """Return (text, words) using PyMuPDF. Words list may be empty."""
    try:
        doc = fitz.open(pdf_path)
        page = doc.load_page(page_no - 1)
        text_val = page.get_text("text")
        raw = page.get_text("words")
        words: List[Dict[str, Any]] = []
        for t in raw:
            # raw tuple: (x0,y0,x1,y1,text,block_no,line_no,word_no)
            if len(t) >= 5:
                txt_val = t[4]
                if safe_str_nonempty(txt_val):
                    x0, y0, x1, y1 = t[0], t[1], t[2], t[3]
                    words.append({"text": str(txt_val), "x0": float(x0), "x1": float(x1), "top": float(y0), "bottom": float(y1)})
        doc.close()
        text_out: Optional[str] = str(text_val).strip() if safe_str_nonempty(text_val) else None
        return text_out, words
    except Exception:
        return None, []

def pdfplumber_extract(page) -> Tuple[Optional[str], List[Dict[str, Any]]]:
    """
    Return (text, words) extracted by pdfplumber; ensure consistent return types:
    - text is Optional[str]
    - words is List[Dict[str, Any]]
    """
    text_out: Optional[str] = None
    words_out: List[Dict[str, Any]] = []
    try:
        raw_text = page.extract_text()
        if safe_str_nonempty(raw_text):
            text_out = str(raw_text)
    except Exception:
        text_out = None

    try:
        raw_words = page.extract_words(use_text_flow=True) or []
    except Exception:
        raw_words = []

    # Normalize raw_words into a list of dicts with 'text' key
    try:
        normalized: List[Dict[str, Any]] = []
        if isinstance(raw_words, list):
            for w in raw_words:
                if isinstance(w, dict):
                    txt = w.get("text") or w.get("t") or w.get("str") or ""
                    if safe_str_nonempty(txt):
                        # keep numeric coords if present, else default 0.0
                        x0 = float(w.get("x0", 0.0)) if w.get("x0", None) is not None else 0.0
                        x1 = float(w.get("x1", 0.0)) if w.get("x1", None) is not None else 0.0
                        top = float(w.get("top", 0.0)) if w.get("top", None) is not None else 0.0
                        bottom = float(w.get("bottom", 0.0)) if w.get("bottom", None) is not None else 0.0
                        normalized.append({"text": str(txt), "x0": x0, "x1": x1, "top": top, "bottom": bottom})
                elif isinstance(w, (list, tuple)) and len(w) >= 5:
                    # sometimes pdfplumber may return tuples — defensive
                    txt_val = w[4]
                    if safe_str_nonempty(txt_val):
                        x0, top, x1, bottom = float(w[0]), float(w[1]), float(w[2]), float(w[3])
                        normalized.append({"text": str(txt_val), "x0": x0, "x1": x1, "top": top, "bottom": bottom})
        elif isinstance(raw_words, dict):
            # single dict -> wrap
            txt = raw_words.get("text") or raw_words.get("t") or ""
            if safe_str_nonempty(txt):
                x0 = float(raw_words.get("x0", 0.0))
                x1 = float(raw_words.get("x1", 0.0))
                top = float(raw_words.get("top", 0.0))
                bottom = float(raw_words.get("bottom", 0.0))
                normalized.append({"text": str(txt), "x0": x0, "x1": x1, "top": top, "bottom": bottom})
        words_out = normalized
    except Exception:
        words_out = []

    # If we have words, prefer them; otherwise text_out may be used by caller
    if words_out:
        # ensure text_out is None to match earlier semantics (words wins)
        return None, words_out
    return text_out, []

def pdfminer_extract(pdf_path: str, page_no: Optional[int] = None) -> Optional[str]:
    """Use pdfminer.six to extract text (per page if page_no provided)."""
    try:
        if page_no is None:
            txt = pdfminer_extract_text(pdf_path)
        else:
            txt = pdfminer_extract_text(pdf_path, page_numbers=[page_no - 1])
        if safe_str_nonempty(txt):
            return str(txt)
    except Exception:
        pass
    return None

# -------------------------
# Aggressive per-page extractor (returns normalized dict)
# -------------------------
def extract_page_aggressive(pdf_tmp_path: str, page_num: int, dpi: int = 300, ocr_mode: str = "auto", debug_outdir: Optional[Path] = None) -> Dict[str, Any]:
    """
    Try: pdftotext -> PyMuPDF -> pdfminer -> pdfplumber -> OCR(with preprocessing).
    Returns dict with keys: text, words, source, sample_image (optional).
    """
    result: Dict[str, Any] = {"text": None, "words": [], "source": None, "sample_image": None}

    # 1) pdftotext CLI
    t = run_pdftotext(pdf_tmp_path, page_no=page_num)
    if safe_str_nonempty(t):
        result.update({"text": t, "source": "pdftotext"})
        return result

    # 2) PyMuPDF
    t, words = fitz_extract_text_words(pdf_tmp_path, page_num)
    if words or safe_str_nonempty(t):
        result.update({"text": t, "words": words, "source": "pymupdf"})
        return result

    # 3) pdfminer.six
    t = pdfminer_extract(pdf_tmp_path, page_no=page_num)
    if safe_str_nonempty(t):
        result.update({"text": t, "source": "pdfminer"})
        return result

    # 4) pdfplumber
    try:
        with pdfplumber.open(pdf_tmp_path) as doc:
            page = doc.pages[page_num - 1]
            t_p, w_p = pdfplumber_extract(page)
            if w_p:
                result.update({"words": w_p, "source": "pdfplumber_words"})
                return result
            if safe_str_nonempty(t_p):
                result.update({"text": t_p, "source": "pdfplumber_text"})
                return result
    except Exception:
        pass

    # 5) OCR fallback with preprocessing
    if ocr_mode in ("always", "auto"):
        try:
            with pdfplumber.open(pdf_tmp_path) as doc:
                page = doc.pages[page_num - 1]
                pil = page.to_image(resolution=dpi).original
        except Exception:
            pil = None
        if pil is not None:
            processed = preprocess_for_ocr(pil, upscale_factor=2, do_deskew=True)
            tconf = r"--oem 3 --psm 3"
            try:
                ocr_text_raw = pytesseract.image_to_string(processed, config=tconf)
            except Exception:
                ocr_text_raw = ""
            ocr_text = safe_get_text_from_ocr_field(ocr_text_raw)
            try:
                ocr_data = pytesseract.image_to_data(processed, output_type=pytesseract.Output.DICT)
            except Exception:
                ocr_data = {"text": [], "left": [], "top": [], "width": [], "height": [], "conf": []}
            words_ocr: List[Dict[str, Any]] = []
            text_list = ocr_data.get("text", []) if isinstance(ocr_data.get("text", []), (list, tuple)) else []
            lefts = ocr_data.get("left", []) if isinstance(ocr_data.get("left", []), (list, tuple)) else []
            tops = ocr_data.get("top", []) if isinstance(ocr_data.get("top", []), (list, tuple)) else []
            widths = ocr_data.get("width", []) if isinstance(ocr_data.get("width", []), (list, tuple)) else []
            heights = ocr_data.get("height", []) if isinstance(ocr_data.get("height", []), (list, tuple)) else []
            confs = ocr_data.get("conf", []) if isinstance(ocr_data.get("conf", []), (list, tuple)) else []
            n = safe_len(text_list)
            for i in range(n):
                txt = safe_get_text_from_ocr_field(text_list[i])
                if not txt:
                    continue
                left = lefts[i] if i < safe_len(lefts) else 0
                top = tops[i] if i < safe_len(tops) else 0
                w = widths[i] if i < safe_len(widths) else 0
                h = heights[i] if i < safe_len(heights) else 0
                conf_raw = confs[i] if i < safe_len(confs) else None
                try:
                    conf = float(conf_raw) if conf_raw not in (None, "", "-1") else None
                except Exception:
                    conf = None
                # convert px->pt accounting for upscale_factor=2
                scale = 72.0 / dpi / 2.0
                words_ocr.append({"text": txt, "x0": left * scale, "x1": (left + w) * scale, "top": top * scale, "bottom": (top + h) * scale, "conf": conf})
            result.update({"text": ocr_text if safe_str_nonempty(ocr_text) else None, "words": words_ocr, "source": "ocr_tesseract"})
            if debug_outdir is not None:
                try:
                    samp = Path(debug_outdir) / f"page_{page_num}_ocr.png"
                    processed.save(samp)
                    result["sample_image"] = str(samp)
                except Exception:
                    pass
            return result

    # nothing found
    return result

# -------------------------
# Top-level document extraction
# -------------------------
def extract_document(pdf_bytes: bytes, ocr_mode: str = "auto", dpi: int = 300, debug_outdir: Optional[Path] = None, progress_cb: Optional[Callable[[int,int,Dict[str,Any]], None]] = None) -> Dict[str, Any]:
    """Extract entire PDF into structured JSON (pages list)."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(pdf_bytes)
        tmp.flush()
        pdf_path = tmp.name
    try:
        with open(pdf_path, "rb") as fh:
            reader = PdfReader(fh)
            md = reader.metadata or {}
            total = safe_len(getattr(reader, "pages", []))
            metadata = {"title": md.get("/Title"), "author": md.get("/Author"), "producer": md.get("/Producer"), "pages": int(total)}
        structured: Dict[str, Any] = {"file": "uploaded", "metadata": metadata, "pages": []}
        for i in range(1, total + 1):
            info = extract_page_aggressive(pdf_path, i, dpi=dpi, ocr_mode=ocr_mode, debug_outdir=debug_outdir)
            page_entry: Dict[str, Any] = {"page_number": i, "width_pt": None, "height_pt": None}
            # page size via pdfplumber if possible
            try:
                with pdfplumber.open(pdf_path) as doc:
                    p = doc.pages[i - 1]
                    page_entry["width_pt"] = float(p.width)
                    page_entry["height_pt"] = float(p.height)
            except Exception:
                page_entry["width_pt"] = None
                page_entry["height_pt"] = None
            page_entry["extraction_source"] = info.get("source")
            page_entry["sample_image"] = info.get("sample_image")
            words = info.get("words", []) or []
            text = info.get("text")
            text_blocks: List[Dict[str, Any]] = []
            if words:
                words_sorted = sorted(words, key=lambda w: (float(w.get("top", 0)), float(w.get("x0", 0))))
                lines: List[List[Dict[str, Any]]] = []
                if words_sorted:
                    cur = [words_sorted[0]]
                    for w in words_sorted[1:]:
                        prev = cur[-1]
                        if abs(float(w.get("top", 0)) - float(prev.get("top", 0))) <= 3:
                            cur.append(w)
                        else:
                            lines.append(cur)
                            cur = [w]
                    lines.append(cur)
                paras: List[List[List[Dict[str, Any]]]] = []
                if lines:
                    curp = [lines[0]]
                    for a, b in zip(lines, lines[1:]):
                        gap = float(b[0].get("top", 0)) - float(a[-1].get("bottom", 0))
                        if gap <= 8:
                            curp.append(b)
                        else:
                            paras.append(curp)
                            curp = [b]
                    paras.append(curp)
                for p in paras:
                    para_lines = []
                    for ln in p:
                        txt = " ".join(str(w.get("text", "")).strip() for w in ln if safe_str_nonempty(w.get("text")))
                        bbox = [min(float(w.get("x0", 0)) for w in ln), min(float(w.get("top", 0)) for w in ln), max(float(w.get("x1", 0)) for w in ln), max(float(w.get("bottom", 0)) for w in ln)]
                        para_lines.append({"text": txt, "bbox": bbox, "words": ln})
                    text_blocks.append({"bbox": None, "paragraphs": [{"lines": para_lines, "bbox": None}]})
            elif safe_str_nonempty(text):
                para_lines = [{"text": l.strip(), "bbox": [0,0,0,0], "words": [{"text": w} for w in l.split()]} for l in str(text).splitlines() if safe_str_nonempty(l)]
                if para_lines:
                    text_blocks.append({"bbox": None, "paragraphs": [{"lines": para_lines, "bbox": None}]})
            page_entry["text_blocks"] = text_blocks
            # pdfplumber tables & images
            try:
                with pdfplumber.open(pdf_path) as doc:
                    p = doc.pages[i - 1]
                    raw_tables = p.extract_tables()
                    page_entry["tables"] = [{"rows": t} for t in raw_tables] if raw_tables else []
                    imgs = []
                    for idx, img in enumerate(p.images):
                        imgs.append({"bbox":[img.get("x0"), img.get("y0"), img.get("x1"), img.get("y1")], "name": None})
                    page_entry["images"] = imgs
            except Exception:
                page_entry["tables"] = []
                page_entry["images"] = []
            # debug counts
            if safe_str_nonempty(text):
                text_len = len(str(text))
            else:
                text_len = sum(len(ln.get("text","")) for blk in text_blocks for para in blk["paragraphs"] for ln in para["lines"]) if text_blocks else 0
            page_entry["_debug_text_len"] = int(text_len)
            page_entry["_debug_source"] = info.get("source")
            structured["pages"].append(page_entry)
            if callable(progress_cb):
                progress_cb(i, int(total), page_entry)
        return structured
    finally:
        try:
            os.unlink(pdf_path)
        except Exception:
            pass

# -------------------------
# Streamlit UI
# -------------------------
st.title("Advanced PDF Reader — Final (Pylance-clean, normalize & return-type fixes)")

col1, col2 = st.columns([1,2])
with col1:
    uploaded = st.file_uploader("Upload PDF", type=["pdf"])
    ocr_mode = st.selectbox("OCR Mode", options=["auto","always","never"], index=0)
    dpi = st.slider("Raster DPI (for OCR)", 150, 600, 300)
    save_debug_images = st.checkbox("Save debug OCR images (server)", value=True)
    debug = st.checkbox("Show extraction debug info", value=True)
    run = st.button("Process")

with col2:
    status = st.empty()
    prog = st.progress(0)
    logs = st.empty()
    out_area = st.empty()

json_bytes: Optional[bytes] = None
txt_bytes: Optional[bytes] = None

if uploaded and run:
    uploaded_file = uploaded  # non-optional alias
    base = Path(uploaded_file.name).stem
    out_dir: Optional[Path] = None
    if save_debug_images:
        out_dir = Path("pdf_reader_debug") / (base + "_" + datetime.utcnow().strftime("%Y%m%dT%H%M%S"))
        out_dir.mkdir(parents=True, exist_ok=True)
    data = uploaded_file.read()

    def progress_cb(page_i: int, total: int, page_struct: Dict[str, Any]) -> None:
        pct = int((page_i/total)*100) if total else 100
        prog.progress(pct)
        status.markdown(f"Processing page {page_i}/{total} — source: {page_struct.get('_debug_source')} — chars: {page_struct.get('_debug_text_len')}")
        logs.info(f"page {page_i} source={page_struct.get('_debug_source')} chars={page_struct.get('_debug_text_len')}")

    status.info("Starting extraction — this will attempt multiple methods (may take time)")
    try:
        structured = extract_document(data, ocr_mode=ocr_mode, dpi=dpi, debug_outdir=out_dir, progress_cb=progress_cb)
    except Exception as e:
        status.error(f"Extraction failed: {e}")
        st.stop()

    prog.progress(100)
    status.success("Extraction finished")

    json_str = json.dumps(structured, indent=2, ensure_ascii=False)
    json_bytes = json_str.encode("utf-8")
    txt_buf = io.StringIO()
    for p in structured["pages"]:
        txt_buf.write(f"\n\n--- PAGE {p['page_number']} (source={p.get('_debug_source')}) ---\n\n")
        if p.get("text_blocks"):
            for blk in p["text_blocks"]:
                for para in blk["paragraphs"]:
                    for ln in para["lines"]:
                        txt_buf.write(ln.get("text","") + "\n")
                    txt_buf.write("\n")
        else:
            txt_buf.write(f"[no text extracted; source={p.get('_debug_source')}] chars={p.get('_debug_text_len')}\n")
    txt_bytes = txt_buf.getvalue().encode("utf-8")

    with out_area.container():
        st.subheader("Summary")
        st.write(structured["metadata"])
        rows = [{"page": p["page_number"], "source": p.get("_debug_source"), "chars": p.get("_debug_text_len"), "sample_image": p.get("sample_image")} for p in structured["pages"]]
        st.table(rows)
        if debug:
            for p in structured["pages"][:min(20, len(structured["pages"]))]:
                st.markdown(f"Page {p['page_number']}: source={p.get('_debug_source')} chars={p.get('_debug_text_len')}")
                if p.get("sample_image"):
                    try:
                        st.image(p.get("sample_image"), width=600)
                    except Exception:
                        pass

    if json_bytes:
        st.download_button("Download JSON", data=json_bytes, file_name=base + ".json", mime="application/json")
    if txt_bytes:
        st.download_button("Download TXT", data=txt_bytes, file_name=base + ".txt", mime="text/plain")
    if out_dir:
        st.write(f"Debug artifacts saved at: `{out_dir}`")

st.markdown("""
Notes:
- This file is written to avoid Pylance return-type & normalize overload warnings:
  - pdfplumber_extract now normalizes variable shapes and always returns Tuple[Optional[str], List[Dict]].
  - cv2.normalize is called with an explicit dst array.
- If pages still extract zero text (chars=0), upload a failing PDF page and I will run this exact extractor locally and return the debug PNG + diagnostics.
""")
