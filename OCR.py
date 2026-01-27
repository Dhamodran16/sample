# # OCR.py
# """
# Advanced PDF Reader — persistent downloads + exact line-by-line JSON output.

# Enhancement: tables are exported:
# - JSON: each page includes "tables": [ { "rows": [ [cell1, cell2, ...], ... ] }, ... ]
# - TXT: table rows are inserted as tab-separated lines between markers:
#     --- TABLE START ---
#     cell1<TAB>cell2<TAB>...
#     --- TABLE END ---
# """

# from typing import Any, Optional, Callable, List, Dict, Tuple, cast
# import streamlit as st
# from pathlib import Path
# import tempfile, os, io, subprocess, json
# from datetime import datetime
# import difflib

# # Optional libs (defensive)
# try:
#     import numpy as np  # type: ignore
# except Exception:
#     np = None  # type: ignore

# try:
#     import cv2  # type: ignore
# except Exception:
#     cv2 = None  # type: ignore

# try:
#     from PIL import Image as PILImage  # type: ignore
# except Exception:
#     PILImage = None  # type: ignore

# try:
#     import fitz  # PyMuPDF
# except Exception:
#     fitz = None

# try:
#     import pdfplumber
# except Exception:
#     pdfplumber = None

# try:
#     from pdfminer.high_level import extract_text as pdfminer_extract_text  # type: ignore
# except Exception:
#     pdfminer_extract_text = None

# st.set_page_config(page_title="Advanced PDF Reader — Persistent Downloads", layout="wide")

# # ---- session_state defaults ----
# _defaults = {
#     "processed": False,
#     "uploaded_bytes": None,          # bytes of uploaded PDF (persisted)
#     "uploaded_name": None,           # filename of uploaded PDF
#     "extracted_json_bytes": None,    # structured JSON bytes
#     "extracted_txt_bytes": None,     # TXT bytes
#     "verify_report_bytes": None,
#     "_structured_preview": None,
#     "last_out_dir": None,
#     "_easyocr_state": None,
# }
# for k, v in _defaults.items():
#     if k not in st.session_state:
#         st.session_state[k] = v

# # ---- small utility helpers ----
# def safe_str_nonempty(x: Optional[object]) -> bool:
#     if x is None:
#         return False
#     if isinstance(x, str):
#         return bool(x.strip())
#     if isinstance(x, (bytes, bytearray)):
#         try:
#             return bool(x.decode("utf-8", errors="ignore").strip())
#         except Exception:
#             return False
#     return False

# def safe_get_text_from_ocr_field(v: Optional[object]) -> str:
#     if v is None:
#         return ""
#     if isinstance(v, str):
#         return v.strip()
#     if isinstance(v, (bytes, bytearray)):
#         try:
#             return v.decode("utf-8", errors="ignore").strip()
#         except Exception:
#             return ""
#     try:
#         return str(v).strip()
#     except Exception:
#         return ""

# def safe_path(p: Optional[object]) -> Optional[Path]:
#     if p is None:
#         return None
#     try:
#         return Path(str(p))
#     except Exception:
#         return None

# def coerce_bytes_for_download(d: Optional[object]) -> bytes:
#     if d is None:
#         return b""
#     if isinstance(d, (bytes, bytearray)):
#         return bytes(d)
#     if isinstance(d, str):
#         return d.encode("utf-8")
#     try:
#         if hasattr(d, "read"):
#             b = getattr(d, "read")()
#             if isinstance(b, (bytes, bytearray)):
#                 return bytes(b)
#             return str(b).encode("utf-8")
#     except Exception:
#         pass
#     try:
#         return json.dumps(d, ensure_ascii=False).encode("utf-8")
#     except Exception:
#         return b""

# # ---- basic image helpers (used by OCR fallback) ----
# def pil_to_cv2(pil_img: Optional[Any]):
#     if pil_img is None or np is None:
#         return None
#     try:
#         arr = np.asarray(pil_img)
#     except Exception:
#         return None
#     if getattr(arr, "ndim", 0) == 2:
#         return arr
#     if getattr(arr, "ndim", 0) == 3 and arr.shape[2] == 3:
#         try:
#             return cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)
#         except Exception:
#             return arr
#     if getattr(arr, "ndim", 0) == 3 and arr.shape[2] == 4:
#         try:
#             return cv2.cvtColor(arr, cv2.COLOR_RGBA2BGR)
#         except Exception:
#             return arr
#     return arr

# def cv2_to_pil(img):
#     if PILImage is None:
#         return None
#     try:
#         if getattr(img, "ndim", 0) == 2:
#             return PILImage.fromarray(img)
#         return PILImage.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
#     except Exception:
#         try:
#             return PILImage.fromarray(img)
#         except Exception:
#             return PILImage.new("RGB", (1,1), "white")

# def preprocess_for_ocr(pil_img, upscale_factor: int = 2, do_deskew: bool = True):
#     if pil_img is None:
#         return None
#     try:
#         img = pil_img.convert("RGB")
#     except Exception:
#         return pil_img
#     if np is None or cv2 is None:
#         return img
#     cv_img = pil_to_cv2(img)
#     if cv_img is None:
#         return img
#     try:
#         gray = cv_img if getattr(cv_img, "ndim", 0) == 2 else cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
#     except Exception:
#         gray = cv_img
#     if do_deskew:
#         try:
#             blur = cv2.GaussianBlur(gray, (5,5), 0)
#             thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
#             coords = np.column_stack(np.where(thresh > 0))
#             if coords.shape[0] >= 10:
#                 angle = cv2.minAreaRect(coords)[-1]
#                 if angle < -45:
#                     angle = -(90 + angle)
#                 else:
#                     angle = -angle
#                 (h, w) = gray.shape[:2]
#                 M = cv2.getRotationMatrix2D((w//2,h//2), angle, 1.0)
#                 gray = cv2.warpAffine(gray, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
#         except Exception:
#             pass
#     try:
#         th = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 10)
#     except Exception:
#         th = gray
#     try:
#         h, w = th.shape
#         up = cv2.resize(th, (max(1, w * upscale_factor), max(1, h * upscale_factor)), interpolation=cv2.INTER_CUBIC)
#     except Exception:
#         up = th
#     pil_out = cv2_to_pil(up)
#     return pil_out or img

# # ---- text extraction helpers ----
# def run_pdftotext(pdf_path: str, page_no: Optional[int] = None, layout: bool = True) -> Optional[str]:
#     cmd = ["pdftotext"]
#     if layout:
#         cmd.append("-layout")
#     cmd += ["-enc", "UTF-8"]
#     if page_no is not None:
#         cmd += ["-f", str(page_no), "-l", str(page_no)]
#     cmd += [pdf_path, "-"]
#     try:
#         p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False, timeout=30)
#         out = p.stdout.decode("utf-8", errors="replace")
#         if safe_str_nonempty(out):
#             return out
#     except Exception:
#         pass
#     return None

# def fitz_extract_text_words(pdf_path: str, page_no: int):
#     if fitz is None:
#         return None, []
#     try:
#         doc = fitz.open(pdf_path)
#         page = doc.load_page(page_no-1)
#         text_val = page.get_text("text")
#         raw = page.get_text("words") or []
#         words = []
#         for t in raw:
#             if len(t) >= 5:
#                 txt_val = t[4]
#                 if safe_str_nonempty(txt_val):
#                     x0,y0,x1,y1 = t[0],t[1],t[2],t[3]
#                     words.append({"text": str(txt_val), "x0": float(x0), "x1": float(x1), "top": float(y0), "bottom": float(y1)})
#         doc.close()
#         text_out = str(text_val).strip() if safe_str_nonempty(text_val) else None
#         return text_out, words
#     except Exception:
#         return None, []

# def pdfplumber_extract(page):
#     if page is None:
#         return None, []
#     text_out = None
#     words_out = []
#     try:
#         raw_text = page.extract_text()
#         if safe_str_nonempty(raw_text):
#             text_out = str(raw_text)
#     except Exception:
#         text_out = None
#     try:
#         raw_words = page.extract_words(use_text_flow=True) or []
#     except Exception:
#         raw_words = []
#     normalized = []
#     try:
#         if isinstance(raw_words, list):
#             for w in raw_words:
#                 if isinstance(w, dict):
#                     txt = w.get("text") or w.get("t") or w.get("str") or ""
#                     if safe_str_nonempty(txt):
#                         x0 = float(w.get("x0", 0.0))
#                         x1 = float(w.get("x1", 0.0))
#                         top = float(w.get("top", 0.0))
#                         bottom = float(w.get("bottom", 0.0))
#                         normalized.append({"text": str(txt), "x0": x0, "x1": x1, "top": top, "bottom": bottom})
#                 elif isinstance(w, (list,tuple)) and len(w) >= 5:
#                     txt_val = w[4]
#                     if safe_str_nonempty(txt_val):
#                         x0, top, x1, bottom = float(w[0]), float(w[1]), float(w[2]), float(w[3])
#                         normalized.append({"text": str(txt_val), "x0": x0, "x1": x1, "top": top, "bottom": bottom})
#         elif isinstance(raw_words, dict):
#             txt = raw_words.get("text") or raw_words.get("t") or ""
#             if safe_str_nonempty(txt):
#                 x0 = float(raw_words.get("x0", 0.0))
#                 x1 = float(raw_words.get("x1", 0.0))
#                 top = float(raw_words.get("top", 0.0))
#                 bottom = float(raw_words.get("bottom", 0.0))
#                 normalized.append({"text": str(txt), "x0": x0, "x1": x1, "top": top, "bottom": bottom})
#     except Exception:
#         normalized = []
#     words_out = normalized
#     return text_out, words_out

# def pdfminer_extract(pdf_path: str, page_no: Optional[int] = None) -> Optional[str]:
#     if pdfminer_extract_text is None:
#         return None
#     try:
#         if page_no is None:
#             txt = pdfminer_extract_text(pdf_path)
#         else:
#             txt = pdfminer_extract_text(pdf_path, page_numbers=[page_no-1])
#         if safe_str_nonempty(txt):
#             return str(txt)
#     except Exception:
#         pass
#     return None

# # ---- per-page aggressive extraction (text layers first, OCR fallback) ----
# def extract_page_aggressive(pdf_path: str, page_num: int, dpi: int = 300, ocr_mode: str = "auto", debug_outdir: Optional[Path] = None) -> Dict[str,Any]:
#     result = {"text": None, "words": [], "source": None, "sample_image": None}
#     # pdftotext
#     t = run_pdftotext(pdf_path, page_no=page_num, layout=True)
#     if safe_str_nonempty(t):
#         result.update({"text": t, "source": "pdftotext"})
#         return result
#     # pymupdf
#     t, words = fitz_extract_text_words(pdf_path, page_num)
#     if words or safe_str_nonempty(t):
#         result.update({"text": t, "words": words, "source": "pymupdf"})
#         return result
#     # pdfplumber
#     if pdfplumber is not None:
#         try:
#             with pdfplumber.open(pdf_path) as doc:
#                 page = doc.pages[page_num-1]
#                 t_p, w_p = pdfplumber_extract(page)
#                 if w_p:
#                     result.update({"words": w_p, "source": "pdfplumber_words"})
#                     return result
#                 if safe_str_nonempty(t_p):
#                     result.update({"text": t_p, "source": "pdfplumber_text"})
#                     return result
#         except Exception:
#             pass
#     # pdfminer
#     t = pdfminer_extract(pdf_path, page_no=page_num)
#     if safe_str_nonempty(t):
#         result.update({"text": t, "source": "pdfminer"})
#         return result
#     # OCR fallback (EasyOCR -> pytesseract)
#     if ocr_mode in ("always", "auto"):
#         pil = None
#         # try pdfplumber image
#         if pdfplumber is not None:
#             try:
#                 with pdfplumber.open(pdf_path) as doc:
#                     page = doc.pages[page_num-1]
#                     pil = page.to_image(resolution=dpi).original
#             except Exception:
#                 pil = None
#         # fallback via fitz
#         if pil is None and fitz is not None:
#             try:
#                 doc = fitz.open(pdf_path)
#                 pg = doc.load_page(page_num-1)
#                 mat = fitz.Matrix(dpi/72.0, dpi/72.0)
#                 pix = pg.get_pixmap(matrix=mat)
#                 img_bytes = pix.tobytes("png")
#                 if PILImage is not None:
#                     pil = PILImage.open(io.BytesIO(img_bytes)).convert("RGB")
#                 doc.close()
#             except Exception:
#                 pil = None
#         if pil is not None:
#             processed = preprocess_for_ocr(pil, upscale_factor=2, do_deskew=True)
#             # EasyOCR prefer
#             try:
#                 import importlib
#                 easyocr = importlib.import_module("easyocr")
#                 torch = importlib.import_module("torch")
#                 gpu_avail = False
#                 try:
#                     gpu_avail = torch.cuda.is_available()
#                 except Exception:
#                     gpu_avail = False
#                 reader = easyocr.Reader(["en"], gpu=gpu_avail)
#                 if reader is not None and np is not None:
#                     arr = np.asarray(processed.convert("RGB")) if processed is not None else None
#                     if arr is not None:
#                         raw = reader.readtext(arr, detail=1)
#                         words_ocr = []
#                         parts = []
#                         for bbox, text, conf in raw:
#                             t_s = safe_get_text_from_ocr_field(text)
#                             if not t_s:
#                                 continue
#                             parts.append(t_s)
#                             xs = [p[0] for p in bbox]; ys = [p[1] for p in bbox]
#                             words_ocr.append({"text": t_s, "x0": float(min(xs)), "x1": float(max(xs)), "top": float(min(ys)), "bottom": float(max(ys)), "conf": float(conf) if conf is not None else None})
#                         ocr_text = " ".join(parts) if parts else None
#                         result.update({"text": ocr_text, "words": words_ocr, "source": "easyocr_gpu" if gpu_avail else "easyocr_cpu"})
#                         # save sample image if requested
#                         if debug_outdir is not None and processed is not None and hasattr(processed, "save"):
#                             try:
#                                 d = safe_path(debug_outdir)
#                                 if d is not None:
#                                     d.mkdir(parents=True, exist_ok=True)
#                                     f = d / f"page_{page_num}_ocr.png"
#                                     processed.save(f)
#                                     result["sample_image"] = str(f)
#                             except Exception:
#                                 pass
#                         return result
#             except Exception:
#                 pass
#             # pytesseract fallback
#             try:
#                 import pytesseract
#                 cfg = r"--oem 3 --psm 3"
#                 raw_text = pytesseract.image_to_string(processed, config=cfg)
#                 ocr_text = safe_get_text_from_ocr_field(raw_text)
#                 try:
#                     data = pytesseract.image_to_data(processed, output_type=pytesseract.Output.DICT)
#                 except Exception:
#                     data = {"text": [], "left": [], "top": [], "width": [], "height": [], "conf": []}
#                 words_ocr = []
#                 text_list = data.get("text", []) if isinstance(data.get("text", []), (list, tuple)) else []
#                 lefts = data.get("left", []) if isinstance(data.get("left", []), (list, tuple)) else []
#                 tops = data.get("top", []) if isinstance(data.get("top", []), (list, tuple)) else []
#                 widths = data.get("width", []) if isinstance(data.get("width", []), (list, tuple)) else []
#                 heights = data.get("height", []) if isinstance(data.get("height", []), (list, tuple)) else []
#                 confs = data.get("conf", []) if isinstance(data.get("conf", []), (list, tuple)) else []
#                 n = len(text_list)
#                 for i in range(n):
#                     txt = safe_get_text_from_ocr_field(text_list[i])
#                     if not txt:
#                         continue
#                     left = lefts[i] if i < len(lefts) else 0
#                     top = tops[i] if i < len(tops) else 0
#                     w = widths[i] if i < len(widths) else 0
#                     h = heights[i] if i < len(heights) else 0
#                     conf_raw = confs[i] if i < len(confs) else None
#                     try:
#                         conf = float(conf_raw) if conf_raw not in (None, "", "-1") else None
#                     except Exception:
#                         conf = None
#                     words_ocr.append({"text": txt, "x0": float(left), "x1": float(left + w), "top": float(top), "bottom": float(top + h), "conf": conf})
#                 result.update({"text": ocr_text if safe_str_nonempty(ocr_text) else None, "words": words_ocr, "source": "tesseract"})
#                 if debug_outdir is not None and processed is not None and hasattr(processed, "save"):
#                     try:
#                         d = safe_path(debug_outdir)
#                         if d is not None:
#                             d.mkdir(parents=True, exist_ok=True)
#                             f = d / f"page_{page_num}_ocr.png"
#                             processed.save(f)
#                             result["sample_image"] = str(f)
#                     except Exception:
#                         pass
#                 return result
#             except Exception:
#                 pass
#     return result

# # ---- assemble document extraction ----
# def extract_document(pdf_bytes: bytes, ocr_mode: str = "auto", dpi: int = 300, debug_outdir: Optional[Path] = None, progress_cb: Optional[Callable[[int,int,Dict[str,Any]], None]] = None) -> Dict[str,Any]:
#     with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
#         tmp.write(pdf_bytes); tmp.flush(); pdf_path = tmp.name
#     try:
#         metadata = {"title": None, "author": None, "producer": None, "pages": 0}
#         total = 0
#         # try PyPDF2 metadata/pages
#         try:
#             from PyPDF2 import PdfReader
#             with open(pdf_path, "rb") as fh:
#                 r = PdfReader(fh)
#                 md = getattr(r, "metadata", {}) or {}
#                 total = len(getattr(r, "pages", []))
#                 metadata = {"title": md.get("/Title"), "author": md.get("/Author"), "producer": md.get("/Producer"), "pages": int(total)}
#         except Exception:
#             total = 0
#         # fallback via pdfplumber to count pages
#         if total == 0 and pdfplumber is not None:
#             try:
#                 with pdfplumber.open(pdf_path) as doc:
#                     total = len(doc.pages)
#                     metadata["pages"] = total
#             except Exception:
#                 total = 0
#         structured = {"file": "uploaded", "metadata": metadata, "pages": []}
#         if total <= 0:
#             return structured
#         # iterate pages
#         for i in range(1, total+1):
#             info = extract_page_aggressive(pdf_path, i, dpi=dpi, ocr_mode=ocr_mode, debug_outdir=debug_outdir)
#             page_entry = {"page_number": i, "width_pt": None, "height_pt": None}
#             if pdfplumber is not None:
#                 try:
#                     with pdfplumber.open(pdf_path) as doc:
#                         p = doc.pages[i-1]
#                         page_entry["width_pt"] = float(p.width); page_entry["height_pt"] = float(p.height)
#                 except Exception:
#                     page_entry["width_pt"] = None; page_entry["height_pt"] = None
#             page_entry["extraction_source"] = info.get("source")
#             page_entry["sample_image"] = info.get("sample_image")
#             words = info.get("words", []) or []
#             text = info.get("text")
#             # build line-by-line blocks (prefer words if present)
#             text_blocks = []
#             if words:
#                 words_sorted = sorted(words, key=lambda w: (float(w.get("top", 0)), float(w.get("x0", 0))))
#                 lines = []
#                 if words_sorted:
#                     cur = [words_sorted[0]]
#                     for w in words_sorted[1:]:
#                         prev = cur[-1]
#                         if abs(float(w.get("top", 0)) - float(prev.get("top", 0))) <= 3:
#                             cur.append(w)
#                         else:
#                             lines.append(cur)
#                             cur = [w]
#                     lines.append(cur)
#                 paras = []
#                 if lines:
#                     curp = [lines[0]]
#                     for a,b in zip(lines, lines[1:]):
#                         gap = float(b[0].get("top", 0)) - float(a[-1].get("bottom", 0))
#                         if gap <= 8:
#                             curp.append(b)
#                         else:
#                             paras.append(curp); curp = [b]
#                     paras.append(curp)
#                 for pblock in paras:
#                     para_lines = []
#                     for ln in pblock:
#                         txt = " ".join(str(w.get("text","")).strip() for w in ln if safe_str_nonempty(w.get("text")))
#                         try:
#                             bbox = [min(float(w.get("x0",0)) for w in ln), min(float(w.get("top",0)) for w in ln), max(float(w.get("x1",0)) for w in ln), max(float(w.get("bottom",0)) for w in ln)]
#                         except Exception:
#                             bbox = [0,0,0,0]
#                         para_lines.append({"text": txt, "bbox": bbox, "words": ln})
#                     text_blocks.append({"bbox": None, "paragraphs": [{"lines": para_lines, "bbox": None}]})
#             elif safe_str_nonempty(text):
#                 para_lines = [{"text": l.rstrip(), "bbox": [0,0,0,0], "words": [{"text": w} for w in l.split()]} for l in str(text).splitlines() if safe_str_nonempty(l)]
#                 if para_lines:
#                     text_blocks.append({"bbox": None, "paragraphs": [{"lines": para_lines, "bbox": None}]})
#             page_entry["text_blocks"] = text_blocks
#             # tables/images if pdfplumber
#             page_entry["tables"] = []
#             page_entry["images"] = []
#             if pdfplumber is not None:
#                 try:
#                     with pdfplumber.open(pdf_path) as doc:
#                         p = doc.pages[i-1]
#                         raw_tables = p.extract_tables()
#                         page_entry["tables"] = [{"rows": t} for t in raw_tables] if raw_tables else []
#                         imgs = []
#                         for im in p.images:
#                             imgs.append({"bbox":[im.get("x0"), im.get("y0"), im.get("x1"), im.get("y1")], "name": None})
#                         page_entry["images"] = imgs
#                 except Exception:
#                     page_entry["tables"] = []; page_entry["images"] = []
#             # debug text length
#             if safe_str_nonempty(text):
#                 text_len = len(str(text))
#             else:
#                 text_len = sum(len(ln.get("text","")) for blk in text_blocks for para in blk["paragraphs"] for ln in para["lines"]) if text_blocks else 0
#             page_entry["_debug_text_len"] = int(text_len)
#             page_entry["_debug_source"] = info.get("source")
#             structured["pages"].append(page_entry)
#             if callable(progress_cb):
#                 try:
#                     progress_cb(i, int(total), page_entry)
#                 except Exception:
#                     pass
#         return structured
#     finally:
#         try: os.unlink(pdf_path)
#         except Exception: pass

# # ---- verification helpers (line-by-line) ----
# def normalize_line(s: Optional[str]) -> str:
#     if not safe_str_nonempty(s):
#         return ""
#     return " ".join(str(s).split()).strip()

# def get_ground_truth_lines(pdf_path: str, page_num: int) -> List[str]:
#     if pdfplumber is not None:
#         try:
#             with pdfplumber.open(pdf_path) as doc:
#                 if 0 <= page_num-1 < len(doc.pages):
#                     pg = doc.pages[page_num-1]
#                     t = pg.extract_text()
#                     if safe_str_nonempty(t):
#                         return [normalize_line(l) for l in str(t).splitlines() if normalize_line(l)]
#         except Exception:
#             pass
#     if fitz is not None:
#         try:
#             doc = fitz.open(pdf_path)
#             pg = doc.load_page(page_num-1)
#             t = pg.get_text("text")
#             doc.close()
#             if safe_str_nonempty(t):
#                 return [normalize_line(l) for l in str(t).splitlines() if normalize_line(l)]
#         except Exception:
#             pass
#     t = run_pdftotext(pdf_path, page_no=page_num, layout=True)
#     if safe_str_nonempty(t):
#         return [normalize_line(l) for l in str(t).splitlines() if normalize_line(l)]
#     return []

# def extract_lines_from_page_struct(page_struct: Dict[str,Any]) -> List[str]:
#     lines = []
#     blocks = page_struct.get("text_blocks", [])
#     if isinstance(blocks, list) and blocks:
#         for blk in blocks:
#             paras = blk.get("paragraphs", [])
#             for para in paras:
#                 for ln in para.get("lines", []):
#                     txt = ln.get("text","")
#                     if safe_str_nonempty(txt):
#                         normalized = normalize_line(txt)
#                         if normalized:
#                             lines.append(normalized)
#         return lines
#     txt = page_struct.get("text")
#     if safe_str_nonempty(txt):
#         return [normalize_line(l) for l in str(txt).splitlines() if normalize_line(l)]
#     return []

# def verify_page(page_struct: Dict[str,Any], ground_truth_lines: List[str], fuzzy_thresh: float = 0.90) -> Dict[str,Any]:
#     extracted_lines = extract_lines_from_page_struct(page_struct)
#     gt = ground_truth_lines or []
#     matched = 0
#     mismatches = []
#     used = set()
#     for e in extracted_lines:
#         best_ratio = 0.0
#         best_idx = None
#         for idx,g in enumerate(gt):
#             if idx in used:
#                 continue
#             ratio = difflib.SequenceMatcher(None, e, g).ratio()
#             if ratio > best_ratio:
#                 best_ratio = ratio; best_idx = idx
#         if best_ratio >= fuzzy_thresh and best_idx is not None:
#             matched += 1; used.add(best_idx)
#         else:
#             mismatches.append({"extracted": e, "best_gt": gt[best_idx] if best_idx is not None and best_idx < len(gt) else None, "ratio": round(best_ratio,3)})
#     total = max(1, len(gt))
#     match_percent = round((matched/total) * 100.0, 1)
#     level = "Good" if match_percent >= 90 else ("Avg" if match_percent >= 60 else "Poor")
#     return {"matched": matched, "gt_total": len(gt), "extracted_total": len(extracted_lines), "match_percent": match_percent, "level": level, "mismatches": mismatches}

# # ---- Streamlit UI ----
# st.title("Advanced PDF Reader — Persistent Downloads & Exact JSON (tables supported)")

# col1, col2 = st.columns([1,2])
# with col1:
#     uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])
#     ocr_mode = st.selectbox("OCR Mode", ["auto", "always", "never"], index=0)
#     dpi = st.slider("Raster DPI (for OCR)", 100, 600, 300)
#     save_debug_images = st.checkbox("Save debug OCR images (server)", value=False)
#     debug = st.checkbox("Show extraction debug info", value=False)
#     verify = st.checkbox("Verify extraction line-by-line against PDF text layer", value=True)
#     fuzzy_thresh_pct = st.slider("Fuzzy match threshold (%)", 50, 100, 90)
#     process_button = st.button("Process")
#     clear_button = st.button("Clear outputs")

# with col2:
#     status = st.empty()
#     prog = st.progress(0)
#     out_area = st.empty()
#     logs = st.empty()

# def _safe_rerun():
#     rerun = getattr(st, "experimental_rerun", None)
#     if callable(rerun):
#         try: rerun()
#         except Exception: pass

# if clear_button:
#     for k in list(_defaults.keys()) + ["_easyocr_state"]:
#         if k in st.session_state:
#             del st.session_state[k]
#     for k, v in _defaults.items():
#         if k not in st.session_state:
#             st.session_state[k] = v
#     _safe_rerun()

# # If user uploaded a file and clicked Process, read bytes and store them persistently
# if uploaded_file is not None and process_button:
#     # read safely and persist bytes + filename
#     data = b""
#     try:
#         if hasattr(uploaded_file, "read"):
#             data = uploaded_file.read()
#             if not isinstance(data, (bytes, bytearray)):
#                 try:
#                     data = bytes(data)
#                 except Exception:
#                     data = str(data).encode("utf-8", errors="ignore")
#         else:
#             data = uploaded_file.getvalue() if hasattr(uploaded_file, "getvalue") else b""
#     except Exception:
#         try: data = uploaded_file.getvalue()
#         except Exception: data = b""
#     st.session_state["uploaded_bytes"] = data
#     st.session_state["uploaded_name"] = getattr(uploaded_file, "name", "uploaded.pdf")
#     # optional debug output dir
#     out_dir = None
#     if save_debug_images:
#         try:
#             base = Path(st.session_state["uploaded_name"]).stem
#             out_dir = Path("pdf_reader_debug") / f"{base}_{datetime.utcnow().strftime('%Y%m%dT%H%M%S')}"
#             out_dir.mkdir(parents=True, exist_ok=True)
#         except Exception:
#             out_dir = None
#     # progress callback
#     def progress_cb(pi, total, page_struct):
#         try: prog.progress(int((pi/total)*100) if total else 100)
#         except Exception: pass
#         try: status.markdown(f"Processing page {pi}/{total} — source: {page_struct.get('_debug_source')} — chars: {page_struct.get('_debug_text_len')}")
#         except Exception: pass
#         try: logs.info(f"page {pi} source={page_struct.get('_debug_source')} chars={page_struct.get('_debug_text_len')}")
#         except Exception: pass
#     status.info("Starting extraction — text layers then OCR fallback (if enabled).")
#     try:
#         structured = extract_document(st.session_state["uploaded_bytes"], ocr_mode=ocr_mode, dpi=dpi, debug_outdir=out_dir, progress_cb=progress_cb)
#     except Exception as e:
#         status.error(f"Extraction failed: {e}")
#         st.stop()
#     prog.progress(100)
#     status.success("Extraction finished")
#     # create line-by-line JSON representation (clean & easy to read), include tables
#     pages_for_json = []
#     txt_lines_all = []
#     for p in structured.get("pages", []):
#         lines: List[str] = []
#         # produce lines from text_blocks if present
#         if p.get("text_blocks"):
#             for blk in p.get("text_blocks", []):
#                 for para in blk.get("paragraphs", []):
#                     for ln in para.get("lines", []):
#                         t = ln.get("text","")
#                         if safe_str_nonempty(t):
#                             lines.append(str(t))
#         # include tables: JSON keeps them as arrays; lines include tab-separated rows with markers
#         tables_struct: List[Dict[str,Any]] = []
#         if p.get("tables"):
#             for tbl in p.get("tables", []):
#                 rows = tbl.get("rows", []) if isinstance(tbl, dict) else (tbl if isinstance(tbl, list) else [])
#                 # normalize each cell to string
#                 normalized_rows = []
#                 for r in rows:
#                     if not isinstance(r, (list, tuple)):
#                         # sometimes pdfplumber returns None or unexpected; coerce
#                         if r is None:
#                             normalized_rows.append([])
#                             continue
#                         try:
#                             # try to coerce dict-like row
#                             normalized_rows.append([str(c) for c in list(r)])
#                         except Exception:
#                             normalized_rows.append([str(r)])
#                     else:
#                         normalized_rows.append([("" if c is None else str(c)).strip() for c in r])
#                 tables_struct.append({"rows": normalized_rows})
#                 # add to lines with markers and tab separation
#                 if normalized_rows:
#                     lines.append("--- TABLE START ---")
#                     for r in normalized_rows:
#                         # join with tab so columns remain aligned in txt viewer
#                         lines.append("\t".join(r))
#                     lines.append("--- TABLE END ---")
#         pages_for_json.append({"page_number": p.get("page_number"), "lines": lines, "source": p.get("_debug_source"), "tables": tables_struct})
#         txt_lines_all.append({"page_number": p.get("page_number"), "lines": lines})
#     # prepare final outputs
#     clean_json = {"file": st.session_state.get("uploaded_name"), "generated": datetime.utcnow().isoformat(), "pages": pages_for_json}
#     json_bytes = json.dumps(clean_json, indent=2, ensure_ascii=False).encode("utf-8")
#     # TXT: preserve line-by-line with page separators
#     txt_buf = io.StringIO()
#     for pg in txt_lines_all:
#         txt_buf.write(f"\n\n--- PAGE {pg['page_number']} ---\n\n")
#         for ln in pg["lines"]:
#             txt_buf.write(ln + "\n")
#         if not pg["lines"]:
#             txt_buf.write("[no lines extracted for this page]\n")
#     txt_bytes = txt_buf.getvalue().encode("utf-8")
#     # verification (optional)
#     verify_bytes = None
#     if verify:
#         verify_report = {"file": st.session_state.get("uploaded_name"), "generated": datetime.utcnow().isoformat(), "pages": []}
#         # need a tmp file for pdf reading ground truth
#         with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmpf:
#             tmpf.write(st.session_state["uploaded_bytes"]); tmpf.flush(); fp = tmpf.name
#         try:
#             for p in structured.get("pages", []):
#                 pg_no = int(p.get("page_number", 0))
#                 gt = get_ground_truth_lines(fp, pg_no)
#                 v = verify_page(p, gt, fuzzy_thresh=(fuzzy_thresh_pct/100.0))
#                 v["page_number"] = pg_no
#                 v["mismatch_sample"] = v["mismatches"][:10]
#                 verify_report["pages"].append(v)
#             percents = [pg.get("match_percent") for pg in verify_report["pages"] if isinstance(pg.get("match_percent"), (int,float))]
#             overall = round(sum(percents)/len(percents),1) if percents else 0.0
#             verify_report["overall_match_percent"] = overall
#             verify_report["overall_level"] = "Good" if overall >= 90 else ("Avg" if overall >= 60 else "Poor")
#             verify_bytes = json.dumps(verify_report, indent=2, ensure_ascii=False).encode("utf-8")
#         finally:
#             try: os.unlink(fp)
#             except Exception: pass
#     # persist outputs so download buttons remain independent of uploader object
#     st.session_state["extracted_json_bytes"] = json_bytes
#     st.session_state["extracted_txt_bytes"] = txt_bytes
#     st.session_state["verify_report_bytes"] = verify_bytes
#     st.session_state["_structured_preview"] = structured
#     st.session_state["processed"] = True
#     st.session_state["last_out_dir"] = str(out_dir) if out_dir else None
#     st.session_state["uploaded_name"] = st.session_state.get("uploaded_name", "uploaded.pdf")

# # If there's already processed data in session_state, use it and show downloads
# with out_area.container():
#     preview = st.session_state.get("_structured_preview")
#     if preview:
#         st.subheader("Extraction Summary")
#         st.write(preview.get("metadata", {}))
#         rows = []
#         for p in preview.get("pages", []):
#             rows.append({"page": p.get("page_number"), "source": p.get("_debug_source"), "chars": p.get("_debug_text_len"), "sample_image": p.get("sample_image")})
#         st.table(rows)
#         if debug:
#             st.subheader("Per-page debug (first 50 pages)")
#             for p in preview.get("pages", [])[:50]:
#                 st.markdown(f"Page {p.get('page_number')}: source={p.get('_debug_source')} chars={p.get('_debug_text_len')}")
#                 if p.get("sample_image"):
#                     try:
#                         st.image(p.get("sample_image"), width=350)
#                     except Exception:
#                         pass
#         if verify and st.session_state.get("verify_report_bytes"):
#             try:
#                 verify_report = json.loads(st.session_state.get("verify_report_bytes", b"").decode("utf-8"))
#             except Exception:
#                 verify_report = {"pages": []}
#             st.subheader("Verification Results")
#             vt = []
#             for pg in verify_report.get("pages", []):
#                 vt.append({"page": pg.get("page_number"), "match_percent": pg.get("match_percent"), "level": pg.get("level"), "gt_lines": pg.get("gt_total"), "extracted_lines": pg.get("extracted_total")})
#             st.table(vt)
#             st.markdown(f"**Overall match:** {verify_report.get('overall_match_percent')}% — {verify_report.get('overall_level')}")
#             st.subheader("Mismatch samples (first pages)")
#             for pg in verify_report.get("pages", [])[:5]:
#                 st.markdown(f"**Page {pg.get('page_number')}** — match {pg.get('match_percent')}% — level {pg.get('level')}")
#                 for mm in pg.get("mismatch_sample", [])[:10]:
#                     st.markdown(f"- extracted: `{mm.get('extracted')}`")
#                     st.markdown(f"  best_gt: `{mm.get('best_gt')}` (ratio={mm.get('ratio')})")

# # Download buttons placed in fixed columns; they read bytes from session_state.
# c1, c2, c3 = st.columns([1,1,1])
# with c1:
#     jb = st.session_state.get("extracted_json_bytes")
#     if jb is not None:
#         st.download_button(label="Download Extracted JSON (line-by-line + tables)", data=coerce_bytes_for_download(jb), file_name=f"{Path(st.session_state.get('uploaded_name') or 'extracted').stem}.json", mime="application/json", key="download_json")
# with c2:
#     tb = st.session_state.get("extracted_txt_bytes")
#     if tb is not None:
#         st.download_button(label="Download Extracted TXT (same lines + tables)", data=coerce_bytes_for_download(tb), file_name=f"{Path(st.session_state.get('uploaded_name') or 'extracted').stem}.txt", mime="text/plain", key="download_txt")
# with c3:
#     vb = st.session_state.get("verify_report_bytes")
#     if verify and vb is not None:
#         st.download_button(label="Download Verification Report (JSON)", data=coerce_bytes_for_download(vb), file_name=f"{Path(st.session_state.get('uploaded_name') or 'extracted').stem}_verify.json", mime="application/json", key="download_verify")

# if st.session_state.get("last_out_dir"):
#     try:
#         st.write(f"Debug artifacts saved at: `{st.session_state.get('last_out_dir')}`")
#     except Exception:
#         pass

# if not st.session_state.get("_structured_preview"):
#     st.info("Upload a PDF and click Process to extract text and generate TXT/JSON. Downloads will remain available after extraction.")

# st.markdown("""
# Notes:
# - JSON format produced: { file, generated, pages: [ {page_number, lines: [ ... ], source, tables: [ { rows: [ [c1, c2, ...], ... ] } ] } ] }
#   — Each `lines` entry is a single line extracted, preserving line-order on page. Table rows are included as tab-separated lines and also provided under `tables`.
# - TXT output equals the JSON lines, with page separators and table markers:
#     --- TABLE START ---
#     cell1<TAB>cell2<TAB>...
#     --- TABLE END ---
# - Clicking any download button will rerun Streamlit, but outputs are persisted in `st.session_state`,
#   so multiple downloads (txt, json, verify) can be done sequentially without losing data.
# - To enable GPU OCR, install CUDA-enabled PyTorch and EasyOCR; the app will use EasyOCR if available.
# """)
# OCR.py
"""
Advanced PDF Reader — RAG-ready JSON + chunk generation.

Outputs:
- Ground-truth JSON: exact lines, tables (rows as arrays), images, metadata.
- Chunks JSON: list of chunk records (chunk_id...) suitable for embedding.
- TXT: human readable with table markers and tab-separated cells.
- Verification report (optional).
"""
from typing import Any, Optional, Callable, List, Dict, Tuple, cast
import streamlit as st
from pathlib import Path
import tempfile, os, io, subprocess, json, uuid
from datetime import datetime
import difflib

# Optional libs (defensive)
try:
    import numpy as np  # type: ignore
except Exception:
    np = None  # type: ignore

try:
    import cv2  # type: ignore
except Exception:
    cv2 = None  # type: ignore

try:
    from PIL import Image as PILImage  # type: ignore
except Exception:
    PILImage = None  # type: ignore

try:
    import fitz  # PyMuPDF
except Exception:
    fitz = None

try:
    import pdfplumber
except Exception:
    pdfplumber = None

try:
    from pdfminer.high_level import extract_text as pdfminer_extract_text  # type: ignore
except Exception:
    pdfminer_extract_text = None

st.set_page_config(page_title="Advanced PDF Reader — RAG JSON", layout="wide")

# ---- session_state defaults ----
_defaults = {
    "processed": False,
    "uploaded_bytes": None,          # bytes of uploaded PDF (persisted)
    "uploaded_name": None,           # filename of uploaded PDF
    "extracted_json_bytes": None,    # structured JSON bytes (legacy)
    "extracted_txt_bytes": None,     # TXT bytes
    "verify_report_bytes": None,
    "_structured_preview": None,
    "last_out_dir": None,
    "_easyocr_state": None,
    # New RAG outputs:
    "rag_ground_truth_bytes": None,
    "rag_chunks_bytes": None,
    "rag_chunks_list": None,         # list of dicts in memory (optional)
}
for k, v in _defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ---- helpers ----
def _uid(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex}"

def safe_str_nonempty(x: Optional[object]) -> bool:
    if x is None:
        return False
    if isinstance(x, str):
        return bool(x.strip())
    if isinstance(x, (bytes, bytearray)):
        try:
            return bool(x.decode("utf-8", errors="ignore").strip())
        except Exception:
            return False
    return False

def safe_get_text_from_ocr_field(v: Optional[object]) -> str:
    if v is None:
        return ""
    if isinstance(v, str):
        return v.strip()
    if isinstance(v, (bytes, bytearray)):
        try:
            return v.decode("utf-8", errors="ignore").strip()
        except Exception:
            return ""
    try:
        return str(v).strip()
    except Exception:
        return ""

def safe_path(p: Optional[object]) -> Optional[Path]:
    if p is None:
        return None
    try:
        return Path(str(p))
    except Exception:
        return None

def coerce_bytes_for_download(d: Optional[object]) -> bytes:
    if d is None:
        return b""
    if isinstance(d, (bytes, bytearray)):
        return bytes(d)
    if isinstance(d, str):
        return d.encode("utf-8")
    try:
        if hasattr(d, "read"):
            b = getattr(d, "read")()
            if isinstance(b, (bytes, bytearray)):
                return bytes(b)
            return str(b).encode("utf-8")
    except Exception:
        pass
    try:
        return json.dumps(d, ensure_ascii=False).encode("utf-8")
    except Exception:
        return b""

# ---- image helpers for OCR fallback ----
def pil_to_cv2(pil_img: Optional[Any]):
    if pil_img is None or np is None:
        return None
    try:
        arr = np.asarray(pil_img)
    except Exception:
        return None
    if getattr(arr, "ndim", 0) == 2:
        return arr
    if getattr(arr, "ndim", 0) == 3 and arr.shape[2] == 3:
        try:
            return cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)
        except Exception:
            return arr
    if getattr(arr, "ndim", 0) == 3 and arr.shape[2] == 4:
        try:
            return cv2.cvtColor(arr, cv2.COLOR_RGBA2BGR)
        except Exception:
            return arr
    return arr

def cv2_to_pil(img):
    if PILImage is None:
        return None
    try:
        if getattr(img, "ndim", 0) == 2:
            return PILImage.fromarray(img)
        return PILImage.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    except Exception:
        try:
            return PILImage.fromarray(img)
        except Exception:
            return PILImage.new("RGB", (1,1), "white")

def preprocess_for_ocr(pil_img, upscale_factor: int = 2, do_deskew: bool = True):
    if pil_img is None:
        return None
    try:
        img = pil_img.convert("RGB")
    except Exception:
        return pil_img
    if np is None or cv2 is None:
        return img
    cv_img = pil_to_cv2(img)
    if cv_img is None:
        return img
    try:
        gray = cv_img if getattr(cv_img, "ndim", 0) == 2 else cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
    except Exception:
        gray = cv_img
    if do_deskew:
        try:
            blur = cv2.GaussianBlur(gray, (5,5), 0)
            thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
            coords = np.column_stack(np.where(thresh > 0))
            if coords.shape[0] >= 10:
                angle = cv2.minAreaRect(coords)[-1]
                if angle < -45:
                    angle = -(90 + angle)
                else:
                    angle = -angle
                (h, w) = gray.shape[:2]
                M = cv2.getRotationMatrix2D((w//2,h//2), angle, 1.0)
                gray = cv2.warpAffine(gray, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
        except Exception:
            pass
    try:
        th = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 10)
    except Exception:
        th = gray
    try:
        h, w = th.shape
        up = cv2.resize(th, (max(1, w * upscale_factor), max(1, h * upscale_factor)), interpolation=cv2.INTER_CUBIC)
    except Exception:
        up = th
    pil_out = cv2_to_pil(up)
    return pil_out or img

# ---- text extraction helpers (unchanged) ----
def run_pdftotext(pdf_path: str, page_no: Optional[int] = None, layout: bool = True) -> Optional[str]:
    cmd = ["pdftotext"]
    if layout:
        cmd.append("-layout")
    cmd += ["-enc", "UTF-8"]
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

def fitz_extract_text_words(pdf_path: str, page_no: int):
    if fitz is None:
        return None, []
    try:
        doc = fitz.open(pdf_path)
        page = doc.load_page(page_no-1)
        text_val = page.get_text("text")
        raw = page.get_text("words") or []
        words = []
        for t in raw:
            if len(t) >= 5:
                txt_val = t[4]
                if safe_str_nonempty(txt_val):
                    x0,y0,x1,y1 = t[0],t[1],t[2],t[3]
                    words.append({"text": str(txt_val), "x0": float(x0), "x1": float(x1), "top": float(y0), "bottom": float(y1)})
        doc.close()
        text_out = str(text_val).strip() if safe_str_nonempty(text_val) else None
        return text_out, words
    except Exception:
        return None, []

def pdfplumber_extract(page):
    if page is None:
        return None, []
    text_out = None
    words_out = []
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
    normalized = []
    try:
        if isinstance(raw_words, list):
            for w in raw_words:
                if isinstance(w, dict):
                    txt = w.get("text") or w.get("t") or w.get("str") or ""
                    if safe_str_nonempty(txt):
                        x0 = float(w.get("x0", 0.0))
                        x1 = float(w.get("x1", 0.0))
                        top = float(w.get("top", 0.0))
                        bottom = float(w.get("bottom", 0.0))
                        normalized.append({"text": str(txt), "x0": x0, "x1": x1, "top": top, "bottom": bottom})
                elif isinstance(w, (list,tuple)) and len(w) >= 5:
                    txt_val = w[4]
                    if safe_str_nonempty(txt_val):
                        x0, top, x1, bottom = float(w[0]), float(w[1]), float(w[2]), float(w[3])
                        normalized.append({"text": str(txt_val), "x0": x0, "x1": x1, "top": top, "bottom": bottom})
        elif isinstance(raw_words, dict):
            txt = raw_words.get("text") or raw_words.get("t") or ""
            if safe_str_nonempty(txt):
                x0 = float(raw_words.get("x0", 0.0))
                x1 = float(raw_words.get("x1", 0.0))
                top = float(raw_words.get("top", 0.0))
                bottom = float(raw_words.get("bottom", 0.0))
                normalized.append({"text": str(txt), "x0": x0, "x1": x1, "top": top, "bottom": bottom})
    except Exception:
        normalized = []
    words_out = normalized
    return text_out, words_out

def pdfminer_extract(pdf_path: str, page_no: Optional[int] = None) -> Optional[str]:
    if pdfminer_extract_text is None:
        return None
    try:
        if page_no is None:
            txt = pdfminer_extract_text(pdf_path)
        else:
            txt = pdfminer_extract_text(pdf_path, page_numbers=[page_no-1])
        if safe_str_nonempty(txt):
            return str(txt)
    except Exception:
        pass
    return None

# ---- per-page extraction (unchanged) ----
def extract_page_aggressive(pdf_path: str, page_num: int, dpi: int = 300, ocr_mode: str = "auto", debug_outdir: Optional[Path] = None) -> Dict[str,Any]:
    result = {"text": None, "words": [], "source": None, "sample_image": None}
    # pdftotext
    t = run_pdftotext(pdf_path, page_no=page_num, layout=True)
    if safe_str_nonempty(t):
        result.update({"text": t, "source": "pdftotext"})
        return result
    # pymupdf
    t, words = fitz_extract_text_words(pdf_path, page_num)
    if words or safe_str_nonempty(t):
        result.update({"text": t, "words": words, "source": "pymupdf"})
        return result
    # pdfplumber
    if pdfplumber is not None:
        try:
            with pdfplumber.open(pdf_path) as doc:
                page = doc.pages[page_num-1]
                t_p, w_p = pdfplumber_extract(page)
                if w_p:
                    result.update({"words": w_p, "source": "pdfplumber_words"})
                    return result
                if safe_str_nonempty(t_p):
                    result.update({"text": t_p, "source": "pdfplumber_text"})
                    return result
        except Exception:
            pass
    # pdfminer
    t = pdfminer_extract(pdf_path, page_no=page_num)
    if safe_str_nonempty(t):
        result.update({"text": t, "source": "pdfminer"})
        return result
    # OCR fallback (EasyOCR -> pytesseract)
    if ocr_mode in ("always", "auto"):
        pil = None
        # pdfplumber image
        if pdfplumber is not None:
            try:
                with pdfplumber.open(pdf_path) as doc:
                    page = doc.pages[page_num-1]
                    pil = page.to_image(resolution=dpi).original
            except Exception:
                pil = None
        # fallback via fitz
        if pil is None and fitz is not None:
            try:
                doc = fitz.open(pdf_path)
                pg = doc.load_page(page_num-1)
                mat = fitz.Matrix(dpi/72.0, dpi/72.0)
                pix = pg.get_pixmap(matrix=mat)
                img_bytes = pix.tobytes("png")
                if PILImage is not None:
                    pil = PILImage.open(io.BytesIO(img_bytes)).convert("RGB")
                doc.close()
            except Exception:
                pil = None
        if pil is not None:
            processed = preprocess_for_ocr(pil, upscale_factor=2, do_deskew=True)
            # EasyOCR prefer
            try:
                import importlib
                easyocr = importlib.import_module("easyocr")
                torch = importlib.import_module("torch")
                gpu_avail = False
                try:
                    gpu_avail = torch.cuda.is_available()
                except Exception:
                    gpu_avail = False
                reader = easyocr.Reader(["en"], gpu=gpu_avail)
                if reader is not None and np is not None:
                    arr = np.asarray(processed.convert("RGB")) if processed is not None else None
                    if arr is not None:
                        raw = reader.readtext(arr, detail=1)
                        words_ocr = []
                        parts = []
                        for bbox, text, conf in raw:
                            t_s = safe_get_text_from_ocr_field(text)
                            if not t_s:
                                continue
                            parts.append(t_s)
                            xs = [p[0] for p in bbox]; ys = [p[1] for p in bbox]
                            words_ocr.append({"text": t_s, "x0": float(min(xs)), "x1": float(max(xs)), "top": float(min(ys)), "bottom": float(max(ys)), "conf": float(conf) if conf is not None else None})
                        ocr_text = " ".join(parts) if parts else None
                        result.update({"text": ocr_text, "words": words_ocr, "source": "easyocr_gpu" if gpu_avail else "easyocr_cpu"})
                        # save sample image if requested
                        if debug_outdir is not None and processed is not None and hasattr(processed, "save"):
                            try:
                                d = safe_path(debug_outdir)
                                if d is not None:
                                    d.mkdir(parents=True, exist_ok=True)
                                    f = d / f"page_{page_num}_ocr.png"
                                    processed.save(f)
                                    result["sample_image"] = str(f)
                            except Exception:
                                pass
                        return result
            except Exception:
                pass
            # pytesseract fallback
            try:
                import pytesseract
                cfg = r"--oem 3 --psm 3"
                raw_text = pytesseract.image_to_string(processed, config=cfg)
                ocr_text = safe_get_text_from_ocr_field(raw_text)
                try:
                    data = pytesseract.image_to_data(processed, output_type=pytesseract.Output.DICT)
                except Exception:
                    data = {"text": [], "left": [], "top": [], "width": [], "height": [], "conf": []}
                words_ocr = []
                text_list = data.get("text", []) if isinstance(data.get("text", []), (list, tuple)) else []
                lefts = data.get("left", []) if isinstance(data.get("left", []), (list, tuple)) else []
                tops = data.get("top", []) if isinstance(data.get("top", []), (list, tuple)) else []
                widths = data.get("width", []) if isinstance(data.get("width", []), (list, tuple)) else []
                heights = data.get("height", []) if isinstance(data.get("height", []), (list, tuple)) else []
                confs = data.get("conf", []) if isinstance(data.get("conf", []), (list, tuple)) else []
                n = len(text_list)
                for i in range(n):
                    txt = safe_get_text_from_ocr_field(text_list[i])
                    if not txt:
                        continue
                    left = lefts[i] if i < len(lefts) else 0
                    top = tops[i] if i < len(tops) else 0
                    w = widths[i] if i < len(widths) else 0
                    h = heights[i] if i < len(heights) else 0
                    conf_raw = confs[i] if i < len(confs) else None
                    try:
                        conf = float(conf_raw) if conf_raw not in (None, "", "-1") else None
                    except Exception:
                        conf = None
                    words_ocr.append({"text": txt, "x0": float(left), "x1": float(left + w), "top": float(top), "bottom": float(top + h), "conf": conf})
                result.update({"text": ocr_text if safe_str_nonempty(ocr_text) else None, "words": words_ocr, "source": "tesseract"})
                if debug_outdir is not None and processed is not None and hasattr(processed, "save"):
                    try:
                        d = safe_path(debug_outdir)
                        if d is not None:
                            d.mkdir(parents=True, exist_ok=True)
                            f = d / f"page_{page_num}_ocr.png"
                            processed.save(f)
                            result["sample_image"] = str(f)
                    except Exception:
                        pass
                return result
            except Exception:
                pass
    return result

# ---- assemble document extraction (unchanged) ----
def extract_document(pdf_bytes: bytes, ocr_mode: str = "auto", dpi: int = 300, debug_outdir: Optional[Path] = None, progress_cb: Optional[Callable[[int,int,Dict[str,Any]], None]] = None) -> Dict[str,Any]:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(pdf_bytes); tmp.flush(); pdf_path = tmp.name
    try:
        metadata = {"title": None, "author": None, "producer": None, "pages": 0}
        total = 0
        # try PyPDF2 metadata/pages
        try:
            from PyPDF2 import PdfReader
            with open(pdf_path, "rb") as fh:
                r = PdfReader(fh)
                md = getattr(r, "metadata", {}) or {}
                total = len(getattr(r, "pages", []))
                metadata = {"title": md.get("/Title"), "author": md.get("/Author"), "producer": md.get("/Producer"), "pages": int(total)}
        except Exception:
            total = 0
        # fallback via pdfplumber to count pages
        if total == 0 and pdfplumber is not None:
            try:
                with pdfplumber.open(pdf_path) as doc:
                    total = len(doc.pages)
                    metadata["pages"] = total
            except Exception:
                total = 0
        structured = {"file": "uploaded", "metadata": metadata, "pages": []}
        if total <= 0:
            return structured
        # iterate pages
        for i in range(1, total+1):
            info = extract_page_aggressive(pdf_path, i, dpi=dpi, ocr_mode=ocr_mode, debug_outdir=debug_outdir)
            page_entry = {"page_number": i, "width_pt": None, "height_pt": None}
            if pdfplumber is not None:
                try:
                    with pdfplumber.open(pdf_path) as doc:
                        p = doc.pages[i-1]
                        page_entry["width_pt"] = float(p.width); page_entry["height_pt"] = float(p.height)
                except Exception:
                    page_entry["width_pt"] = None; page_entry["height_pt"] = None
            page_entry["extraction_source"] = info.get("source")
            page_entry["sample_image"] = info.get("sample_image")
            words = info.get("words", []) or []
            text = info.get("text")
            # build line-by-line blocks (prefer words if present)
            text_blocks = []
            if words:
                words_sorted = sorted(words, key=lambda w: (float(w.get("top", 0)), float(w.get("x0", 0))))
                lines = []
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
                paras = []
                if lines:
                    curp = [lines[0]]
                    for a,b in zip(lines, lines[1:]):
                        gap = float(b[0].get("top", 0)) - float(a[-1].get("bottom", 0))
                        if gap <= 8:
                            curp.append(b)
                        else:
                            paras.append(curp); curp = [b]
                    paras.append(curp)
                for pblock in paras:
                    para_lines = []
                    for ln in pblock:
                        txt = " ".join(str(w.get("text","")).strip() for w in ln if safe_str_nonempty(w.get("text")))
                        try:
                            bbox = [min(float(w.get("x0",0)) for w in ln), min(float(w.get("top",0)) for w in ln), max(float(w.get("x1",0)) for w in ln), max(float(w.get("bottom",0)) for w in ln)]
                        except Exception:
                            bbox = [0,0,0,0]
                        para_lines.append({"text": txt, "bbox": bbox, "words": ln})
                    text_blocks.append({"bbox": None, "paragraphs": [{"lines": para_lines, "bbox": None}]})
            elif safe_str_nonempty(text):
                para_lines = [{"text": l.rstrip(), "bbox": [0,0,0,0], "words": [{"text": w} for w in l.split()]} for l in str(text).splitlines() if safe_str_nonempty(l)]
                if para_lines:
                    text_blocks.append({"bbox": None, "paragraphs": [{"lines": para_lines, "bbox": None}]})
            page_entry["text_blocks"] = text_blocks
            # tables/images if pdfplumber
            page_entry["tables"] = []
            page_entry["images"] = []
            if pdfplumber is not None:
                try:
                    with pdfplumber.open(pdf_path) as doc:
                        p = doc.pages[i-1]
                        raw_tables = p.extract_tables()
                        page_entry["tables"] = [{"rows": t} for t in raw_tables] if raw_tables else []
                        imgs = []
                        for im in p.images:
                            imgs.append({"bbox":[im.get("x0"), im.get("y0"), im.get("x1"), im.get("y1")], "name": None})
                        page_entry["images"] = imgs
                except Exception:
                    page_entry["tables"] = []; page_entry["images"] = []
            # debug text length
            if safe_str_nonempty(text):
                text_len = len(str(text))
            else:
                text_len = sum(len(ln.get("text","")) for blk in text_blocks for para in blk["paragraphs"] for ln in para["lines"]) if text_blocks else 0
            page_entry["_debug_text_len"] = int(text_len)
            page_entry["_debug_source"] = info.get("source")
            structured["pages"].append(page_entry)
            if callable(progress_cb):
                try:
                    progress_cb(i, int(total), page_entry)
                except Exception:
                    pass
        return structured
    finally:
        try: os.unlink(pdf_path)
        except Exception: pass

# ---- RAG builder: ground-truth + chunk generation ----
def _safe_str(x: Any) -> str:
    if x is None:
        return ""
    if isinstance(x, str):
        return x
    try:
        return str(x)
    except Exception:
        return ""

def build_rag_json_and_chunks(structured: Dict[str,Any], file_name: Optional[str] = None, include_cell_chunks: bool = True) -> Tuple[Dict[str,Any], List[Dict[str,Any]]]:
    """
    Build ground-truth JSON (lossless) and chunk list for embedding.
    Each chunk has a stable chunk_id and references page/table/row/col where applicable.
    """
    doc_id = _uid("doc")
    gt = {
        "doc_id": doc_id,
        "file_name": file_name or (structured.get("metadata", {}).get("title") or "uploaded"),
        "generated": datetime.utcnow().isoformat() + "Z",
        "pages": []
    }
    chunks: List[Dict[str,Any]] = []

    for p in structured.get("pages", []):
        pg_no = int(p.get("page_number", 0)) if p.get("page_number") is not None else 0
        # lines
        lines: List[str] = []
        if p.get("text_blocks"):
            for blk in p.get("text_blocks", []):
                for para in blk.get("paragraphs", []):
                    for ln in para.get("lines", []):
                        t = _safe_str(ln.get("text", "")).rstrip("\n")
                        if t != "":
                            lines.append(t)
        else:
            # fallback to text if present
            raw_text = p.get("text")
            if raw_text is not None and _safe_str(raw_text).strip() != "":
                for l in _safe_str(raw_text).splitlines():
                    if l.strip() != "":
                        lines.append(l.rstrip("\n"))

        # tables
        tables_out = []
        for t in p.get("tables", []) or []:
            raw_rows = t.get("rows") if isinstance(t, dict) else t
            normalized_rows: List[List[str]] = []
            if isinstance(raw_rows, list):
                for r in raw_rows:
                    if isinstance(r, (list, tuple)):
                        normalized_rows.append([("" if c is None else _safe_str(c)).strip() for c in r])
                    else:
                        normalized_rows.append([_safe_str(r)])
            table_id = t.get("table_id") if isinstance(t, dict) and t.get("table_id") else _uid("table")
            tables_out.append({"table_id": table_id, "bbox": t.get("bbox") if isinstance(t, dict) else None, "rows": normalized_rows, "raw_text": _safe_str(t.get("raw_text") if isinstance(t, dict) else "")})

        gt_page = {"page_number": pg_no, "lines": lines, "tables": tables_out, "images": p.get("images", []), "extraction_source": p.get("extraction_source") or p.get("_debug_source") or None}
        gt["pages"].append(gt_page)

        # create line chunks
        for li, line_text in enumerate(lines):
            cid = _uid("chunk")
            chunks.append({
                "chunk_id": cid,
                "doc_id": doc_id,
                "type": "line",
                "page": pg_no,
                "line_index": li,
                "table_id": None,
                "row_index": None,
                "col_index": None,
                "text": line_text,
                "metadata": {"source": gt_page["extraction_source"]}
            })

        # create table chunks (row-level + optional cell-level)
        for tbl in tables_out:
            tbl_id = tbl["table_id"]
            for r_idx, row in enumerate(tbl["rows"]):
                row_text = " | ".join([_safe_str(x) for x in row])
                cid = _uid("chunk")
                chunks.append({
                    "chunk_id": cid,
                    "doc_id": doc_id,
                    "type": "table_row",
                    "page": pg_no,
                    "table_id": tbl_id,
                    "row_index": r_idx,
                    "col_index": None,
                    "text": row_text,
                    "metadata": {"cols": len(row)}
                })
                if include_cell_chunks:
                    for c_idx, cell in enumerate(row):
                        cidc = _uid("chunk")
                        chunks.append({
                            "chunk_id": cidc,
                            "doc_id": doc_id,
                            "type": "table_cell",
                            "page": pg_no,
                            "table_id": tbl_id,
                            "row_index": r_idx,
                            "col_index": c_idx,
                            "text": _safe_str(cell),
                            "metadata": {}
                        })
    return gt, chunks

def dump_rag_files(ground_truth: Dict[str,Any], chunks: List[Dict[str,Any]]):
    gt_bytes = json.dumps(ground_truth, ensure_ascii=False, indent=2).encode("utf-8")
    chunks_bytes = json.dumps(chunks, ensure_ascii=False, indent=2).encode("utf-8")
    return gt_bytes, chunks_bytes

# ---- verification helpers (unchanged) ----
def normalize_line(s: Optional[str]) -> str:
    if not safe_str_nonempty(s):
        return ""
    return " ".join(str(s).split()).strip()

def get_ground_truth_lines(pdf_path: str, page_num: int) -> List[str]:
    if pdfplumber is not None:
        try:
            with pdfplumber.open(pdf_path) as doc:
                if 0 <= page_num-1 < len(doc.pages):
                    pg = doc.pages[page_num-1]
                    t = pg.extract_text()
                    if safe_str_nonempty(t):
                        return [normalize_line(l) for l in str(t).splitlines() if normalize_line(l)]
        except Exception:
            pass
    if fitz is not None:
        try:
            doc = fitz.open(pdf_path)
            pg = doc.load_page(page_num-1)
            t = pg.get_text("text")
            doc.close()
            if safe_str_nonempty(t):
                return [normalize_line(l) for l in str(t).splitlines() if normalize_line(l)]
        except Exception:
            pass
    t = run_pdftotext(pdf_path, page_no=page_num, layout=True)
    if safe_str_nonempty(t):
        return [normalize_line(l) for l in str(t).splitlines() if normalize_line(l)]
    return []

def extract_lines_from_page_struct(page_struct: Dict[str,Any]) -> List[str]:
    lines = []
    blocks = page_struct.get("text_blocks", [])
    if isinstance(blocks, list) and blocks:
        for blk in blocks:
            paras = blk.get("paragraphs", [])
            for para in paras:
                for ln in para.get("lines", []):
                    txt = ln.get("text","")
                    if safe_str_nonempty(txt):
                        normalized = normalize_line(txt)
                        if normalized:
                            lines.append(normalized)
        return lines
    txt = page_struct.get("text")
    if safe_str_nonempty(txt):
        return [normalize_line(l) for l in str(txt).splitlines() if normalize_line(l)]
    return []

def verify_page(page_struct: Dict[str,Any], ground_truth_lines: List[str], fuzzy_thresh: float = 0.90) -> Dict[str,Any]:
    extracted_lines = extract_lines_from_page_struct(page_struct)
    gt = ground_truth_lines or []
    matched = 0
    mismatches = []
    used = set()
    for e in extracted_lines:
        best_ratio = 0.0
        best_idx = None
        for idx,g in enumerate(gt):
            if idx in used:
                continue
            ratio = difflib.SequenceMatcher(None, e, g).ratio()
            if ratio > best_ratio:
                best_ratio = ratio; best_idx = idx
        if best_ratio >= fuzzy_thresh and best_idx is not None:
            matched += 1; used.add(best_idx)
        else:
            mismatches.append({"extracted": e, "best_gt": gt[best_idx] if best_idx is not None and best_idx < len(gt) else None, "ratio": round(best_ratio,3)})
    total = max(1, len(gt))
    match_percent = round((matched/total) * 100.0, 1)
    level = "Good" if match_percent >= 90 else ("Avg" if match_percent >= 60 else "Poor")
    return {"matched": matched, "gt_total": len(gt), "extracted_total": len(extracted_lines), "match_percent": match_percent, "level": level, "mismatches": mismatches}

# ---- Streamlit UI (unchanged layout, integrated RAG generation) ----
st.title("Advanced PDF Reader — RAG-ready JSON + Chunks")

col1, col2 = st.columns([1,2])
with col1:
    uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])
    ocr_mode = st.selectbox("OCR Mode", ["auto", "always", "never"], index=0)
    dpi = st.slider("Raster DPI (for OCR)", 100, 600, 300)
    save_debug_images = st.checkbox("Save debug OCR images (server)", value=False)
    debug = st.checkbox("Show extraction debug info", value=False)
    verify = st.checkbox("Verify extraction line-by-line against PDF text layer", value=True)
    fuzzy_thresh_pct = st.slider("Fuzzy match threshold (%)", 50, 100, 90)
    process_button = st.button("Process")
    clear_button = st.button("Clear outputs")

with col2:
    status = st.empty()
    prog = st.progress(0)
    out_area = st.empty()
    logs = st.empty()

def _safe_rerun():
    rerun = getattr(st, "experimental_rerun", None)
    if callable(rerun):
        try: rerun()
        except Exception: pass

if clear_button:
    for k in list(_defaults.keys()) + ["_easyocr_state"]:
        if k in st.session_state:
            del st.session_state[k]
    for k, v in _defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v
    _safe_rerun()

# If user uploaded a file and clicked Process, read bytes and store them persistently
if uploaded_file is not None and process_button:
    # read safely and persist bytes + filename
    data = b""
    try:
        if hasattr(uploaded_file, "read"):
            data = uploaded_file.read()
            if not isinstance(data, (bytes, bytearray)):
                try:
                    data = bytes(data)
                except Exception:
                    data = str(data).encode("utf-8", errors="ignore")
        else:
            data = uploaded_file.getvalue() if hasattr(uploaded_file, "getvalue") else b""
    except Exception:
        try: data = uploaded_file.getvalue()
        except Exception: data = b""
    st.session_state["uploaded_bytes"] = data
    st.session_state["uploaded_name"] = getattr(uploaded_file, "name", "uploaded.pdf")
    # optional debug output dir
    out_dir = None
    if save_debug_images:
        try:
            base = Path(st.session_state["uploaded_name"]).stem
            out_dir = Path("pdf_reader_debug") / f"{base}_{datetime.utcnow().strftime('%Y%m%dT%H%M%S')}"
            out_dir.mkdir(parents=True, exist_ok=True)
        except Exception:
            out_dir = None
    # progress callback
    def progress_cb(pi, total, page_struct):
        try: prog.progress(int((pi/total)*100) if total else 100)
        except Exception: pass
        try: status.markdown(f"Processing page {pi}/{total} — source: {page_struct.get('_debug_source')} — chars: {page_struct.get('_debug_text_len')}")
        except Exception: pass
        try: logs.info(f"page {pi} source={page_struct.get('_debug_source')} chars={page_struct.get('_debug_text_len')}")
        except Exception: pass
    status.info("Starting extraction — text layers then OCR fallback (if enabled).")
    try:
        structured = extract_document(st.session_state["uploaded_bytes"], ocr_mode=ocr_mode, dpi=dpi, debug_outdir=out_dir, progress_cb=progress_cb)
    except Exception as e:
        status.error(f"Extraction failed: {e}")
        st.stop()
    prog.progress(100)
    status.success("Extraction finished")

    # build RAG ground-truth JSON and chunks
    gt_json, chunks_list = build_rag_json_and_chunks(structured, file_name=st.session_state.get("uploaded_name"), include_cell_chunks=True)
    gt_bytes, chunks_bytes = dump_rag_files(gt_json, chunks_list)

    # create TXT that preserves lines and tables (tab-separated)
    txt_buf = io.StringIO()
    for pg in gt_json["pages"]:
        txt_buf.write(f"\n\n--- PAGE {pg['page_number']} ---\n\n")
        # direct lines
        for ln in pg.get("lines", []):
            txt_buf.write(ln + "\n")
        # tables (if any) with markers
        for tbl in pg.get("tables", []):
            rows = tbl.get("rows", [])
            if rows:
                txt_buf.write("--- TABLE START ---\n")
                for r in rows:
                    txt_buf.write("\t".join(r) + "\n")
                txt_buf.write("--- TABLE END ---\n")
        if not pg.get("lines") and not pg.get("tables"):
            txt_buf.write("[no lines or tables extracted for this page]\n")
    txt_bytes = txt_buf.getvalue().encode("utf-8")

    # verification (optional)
    verify_bytes = None
    if verify:
        verify_report = {"file": st.session_state.get("uploaded_name"), "generated": datetime.utcnow().isoformat(), "pages": []}
        # need a tmp file for pdf reading ground truth
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmpf:
            tmpf.write(st.session_state["uploaded_bytes"]); tmpf.flush(); fp = tmpf.name
        try:
            for p in structured.get("pages", []):
                pg_no = int(p.get("page_number", 0))
                gt = get_ground_truth_lines(fp, pg_no)
                v = verify_page(p, gt, fuzzy_thresh=(fuzzy_thresh_pct/100.0))
                v["page_number"] = pg_no
                v["mismatch_sample"] = v["mismatches"][:10]
                verify_report["pages"].append(v)
            percents = [pg.get("match_percent") for pg in verify_report["pages"] if isinstance(pg.get("match_percent"), (int,float))]
            overall = round(sum(percents)/len(percents),1) if percents else 0.0
            verify_report["overall_match_percent"] = overall
            verify_report["overall_level"] = "Good" if overall >= 90 else ("Avg" if overall >= 60 else "Poor")
            verify_bytes = json.dumps(verify_report, indent=2, ensure_ascii=False).encode("utf-8")
        finally:
            try: os.unlink(fp)
            except Exception: pass

    # persist outputs
    st.session_state["rag_ground_truth_bytes"] = gt_bytes
    st.session_state["rag_chunks_bytes"] = chunks_bytes
    st.session_state["rag_chunks_list"] = chunks_list
    st.session_state["extracted_txt_bytes"] = txt_bytes
    st.session_state["verify_report_bytes"] = verify_bytes
    st.session_state["_structured_preview"] = structured
    st.session_state["processed"] = True
    st.session_state["last_out_dir"] = str(out_dir) if out_dir else None
    st.session_state["uploaded_name"] = st.session_state.get("uploaded_name", "uploaded.pdf")

# Show preview and downloads
with out_area.container():
    preview = st.session_state.get("_structured_preview")
    if preview:
        st.subheader("Extraction Summary")
        st.write(preview.get("metadata", {}))
        rows = []
        for p in preview.get("pages", []):
            rows.append({"page": p.get("page_number"), "source": p.get("_debug_source"), "chars": p.get("_debug_text_len"), "sample_image": p.get("sample_image")})
        st.table(rows)
        if debug:
            st.subheader("Per-page debug (first 50 pages)")
            for p in preview.get("pages", [])[:50]:
                st.markdown(f"Page {p.get('page_number')}: source={p.get('_debug_source')} chars={p.get('_debug_text_len')}")
                if p.get("sample_image"):
                    try:
                        st.image(p.get("sample_image"), width=350)
                    except Exception:
                        pass
        if verify and st.session_state.get("verify_report_bytes"):
            try:
                verify_report = json.loads(st.session_state.get("verify_report_bytes", b"").decode("utf-8"))
            except Exception:
                verify_report = {"pages": []}
            st.subheader("Verification Results")
            vt = []
            for pg in verify_report.get("pages", []):
                vt.append({"page": pg.get("page_number"), "match_percent": pg.get("match_percent"), "level": pg.get("level"), "gt_lines": pg.get("gt_total"), "extracted_lines": pg.get("extracted_total")})
            st.table(vt)
            st.markdown(f"**Overall match:** {verify_report.get('overall_match_percent')}% — {verify_report.get('overall_level')}")
            st.subheader("Mismatch samples (first pages)")
            for pg in verify_report.get("pages", [])[:5]:
                st.markdown(f"**Page {pg.get('page_number')}** — match {pg.get('match_percent')}% — level {pg.get('level')}")
                for mm in pg.get("mismatch_sample", [])[:10]:
                    st.markdown(f"- extracted: `{mm.get('extracted')}`")
                    st.markdown(f"  best_gt: `{mm.get('best_gt')}` (ratio={mm.get('ratio')})")

# Download buttons (fixed columns)
c1, c2, c3, c4 = st.columns([1,1,1,1])
with c1:
    jb = st.session_state.get("rag_ground_truth_bytes")
    if jb is not None:
        st.download_button(
            label="Download Ground-truth JSON (lossless)",
            data=coerce_bytes_for_download(jb),
            file_name=f"{Path(st.session_state.get('uploaded_name') or 'extracted').stem}_ground_truth.json",
            mime="application/json",
            key="download_rag_gt"
        )
with c2:
    cb = st.session_state.get("rag_chunks_bytes")
    if cb is not None:
        st.download_button(
            label="Download Chunks JSON (for embedding)",
            data=coerce_bytes_for_download(cb),
            file_name=f"{Path(st.session_state.get('uploaded_name') or 'extracted').stem}_chunks.json",
            mime="application/json",
            key="download_rag_chunks"
        )
with c3:
    tb = st.session_state.get("extracted_txt_bytes")
    if tb is not None:
        st.download_button(
            label="Download TXT (lines + tables)",
            data=coerce_bytes_for_download(tb),
            file_name=f"{Path(st.session_state.get('uploaded_name') or 'extracted').stem}.txt",
            mime="text/plain",
            key="download_txt"
        )
with c4:
    vb = st.session_state.get("verify_report_bytes")
    if verify and vb is not None:
        st.download_button(
            label="Download Verification Report (JSON)",
            data=coerce_bytes_for_download(vb),
            file_name=f"{Path(st.session_state.get('uploaded_name') or 'extracted').stem}_verify.json",
            mime="application/json",
            key="download_verify"
        )

if st.session_state.get("last_out_dir"):
    try:
        st.write(f"Debug artifacts saved at: `{st.session_state.get('last_out_dir')}`")
    except Exception:
        pass

if not st.session_state.get("_structured_preview"):
    st.info("Upload a PDF and click Process to extract text and generate RAG JSON + Chunks. Downloads persist in session_state.")

st.markdown("""
Notes:
- Ground-truth JSON schema:
  {
    doc_id, file_name, generated,
    pages: [ { page_number, lines: [ ... ], tables: [ { table_id, bbox, rows: [ [c1, c2,...], ... ], raw_text } ], images, extraction_source }, ... ]
  }
- Chunks JSON: list of { chunk_id, doc_id, type: line|table_row|table_cell, page, table_id?, row_index?, col_index?, text, metadata }.
- Embedding workflow: embed chunk['text'] (not the whole doc), store (vector, chunk_id) in vector DB. On retrieval, use chunk_id to fetch exact text & table rows in ground-truth JSON (no hallucination).
- TXT output preserves lines and tables (tables as tab-separated rows inside markers).
- This app persists outputs in st.session_state so downloads remain available after Streamlit reruns.
""")
