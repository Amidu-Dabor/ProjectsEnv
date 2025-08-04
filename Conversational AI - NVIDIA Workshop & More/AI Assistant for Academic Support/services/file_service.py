# services/file_service.py
import os, io, csv, pathlib
from typing import Dict, Any

import PyPDF2, docx, pandas as pd, pptx
from PIL import Image
import openai


class FileProcessor:
    """
    Utility class to read arbitrary user‑uploaded files and pull a few
    human‑friendly metadata fields.
    """

    # --------------------------------------------------------------------- #
    # public API                                                            #
    # --------------------------------------------------------------------- #
    @staticmethod
    def read_file(file) -> str:
        """
        Return the textual content (or a short description for images)
        of *file*.

        `file` may be:
          • a pathlib.Path / str                       ("/tmp/foo.pdf")
          • a Gradio dict                              ({"path": "...", ...})
          • a file‑like object with a `.name` attr     (BytesIO, SpooledFile …)
        """
        path = FileProcessor._path_from_input(file)
        if path is None:
            return "No file provided"

        ext = pathlib.Path(path).suffix.lower()

        # ---------- plain text --------------------------------------------
        if ext == ".txt":
            with open(path, "r", encoding="utf‑8", errors="ignore") as fh:
                return fh.read()

        # ---------- PDF ----------------------------------------------------
        if ext == ".pdf":
            reader = PyPDF2.PdfReader(path)
            return "\n".join(
                p.extract_text() or "" for p in reader.pages
            )

        # ---------- Word ---------------------------------------------------
        if ext in (".docx", ".doc"):
            doc = docx.Document(path)
            return "\n".join(para.text for para in doc.paragraphs)

        # ---------- Excel --------------------------------------------------
        if ext in (".xlsx", ".xls"):
            df = pd.read_excel(path, dtype=str, engine="openpyxl")
            return df.to_string()

        # ---------- CSV ----------------------------------------------------
        if ext == ".csv":
            try:
                df = pd.read_csv(path, dtype=str)
                return df.to_string()
            except Exception:
                # fallback – very large / malformed CSV
                with open(path, newline="", encoding="utf‑8", errors="ignore") as fh:
                    return fh.read()

        # ---------- PowerPoint --------------------------------------------
        if ext in (".pptx", ".ppt"):
            pres = pptx.Presentation(path)
            txt = []
            for slide in pres.slides:
                for shape in slide.shapes:
                    if hasattr(shape, "text"):
                        txt.append(shape.text)
            return "\n".join(txt)

        # ---------- images -------------------------------------------------
        if ext in (".png", ".jpg", ".jpeg", ".gif"):
            try:
                img = Image.open(path)
                buf = io.BytesIO()
                img.save(buf, format="PNG")
                resp = openai.Image.create_variation(
                    image=buf, n=1, size="256x256"
                )
                return f"[Image uploaded. Variation URL: {resp['data'][0]['url']}]"
            except Exception as e:
                return f"Error processing image: {e}"

        return f"Unsupported file type: {ext}"

    # ------------------------------------------------------------------ #
    @staticmethod
    def get_file_metadata(file) -> Dict[str, Any]:
        """
        Return a small dict with useful metadata.
        """
        path = FileProcessor._path_from_input(file)
        if path is None:
            return {"error": "No file provided"}

        p = pathlib.Path(path)
        ext = p.suffix.lower()
        size = p.stat().st_size if p.exists() else 0

        meta: Dict[str, Any] = {
            "filename": p.name,
            "extension": ext,
            "size_bytes": size,
            "size_formatted": FileProcessor._human_size(size),
        }

        # ---------- type‑specific extras ----------------------------------
        try:
            if ext == ".pdf":
                r = PyPDF2.PdfReader(path)
                meta["pages"] = len(r.pages)

            elif ext in (".docx", ".doc"):
                meta["paragraphs"] = len(docx.Document(path).paragraphs)

            elif ext in (".xlsx", ".xls"):
                df = pd.read_excel(path, engine="openpyxl")
                meta.update(rows=len(df), columns=len(df.columns))

            elif ext == ".csv":
                df = pd.read_csv(path)
                meta.update(rows=len(df), columns=len(df.columns))

            elif ext in (".pptx", ".ppt"):
                meta["slides"] = len(pptx.Presentation(path).slides)

            elif ext in (".png", ".jpg", ".jpeg", ".gif"):
                img = Image.open(path)
                meta.update(dimensions=f"{img.width}×{img.height}", mode=img.mode)
        except Exception as e:
            meta["warning"] = f"metadata extraction error: {e}"

        return meta

    # ------------------------------------------------------------------ #
    # helper utilities                                                   #
    # ------------------------------------------------------------------ #
    @staticmethod
    def _path_from_input(inp) -> str | None:
        """
        Normalise whatever Gradio sent us into a file‑system path.
        Returns *None* if the value is obviously invalid.
        """
        if inp is None or inp == "":
            return None

        # New(er) Gradio – dict with "path"
        if isinstance(inp, dict):
            return inp.get("path") or inp.get("name")

        # Old `type="filepath"` – already a str / Path
        if isinstance(inp, (str, pathlib.Path)):
            return str(inp)

        # File‑like object – hope it has `.name`
        if hasattr(inp, "name"):
            return str(inp.name)

        # Anything else → no idea how to handle
        return None

    @staticmethod
    def _human_size(num: int) -> str:
        for unit in ("B", "KB", "MB", "GB", "TB"):
            if num < 1024:
                return f"{num:.2f} {unit}"
            num /= 1024
        return f"{num:.2f} PB"
