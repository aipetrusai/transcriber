import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
import subprocess
import sys
import os
import tempfile

# ── Config ──────────────────────────────────────────────────────────────────
MODEL = "tiny"   # tiny / base / small / medium / large-v3
LANG  = None     # None = autodetect, "es" / "en" / etc.
# ────────────────────────────────────────────────────────────────────────────

BG      = "#0e0e0e"
SURFACE = "#1a1a1a"
BORDER  = "#2a2a2a"
GREEN   = "#00c896"
MUTED   = "#555555"
TEXT    = "#e8e8e8"
TEXT2   = "#888888"

class TranscriberApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Transcriber")
        self.geometry("720x640")
        self.configure(bg=BG)
        self.resizable(True, True)
        self._build_ui()

    def _build_ui(self):
        hdr = tk.Frame(self, bg=BG)
        hdr.pack(fill="x", padx=24, pady=(24, 0))

        tk.Label(hdr, text="⬡", font=("Courier", 20), bg=BG, fg=GREEN).pack(side="left")
        tk.Label(hdr, text="  Transcriber", font=("Segoe UI", 16, "bold"),
                 bg=BG, fg=TEXT).pack(side="left")
        tk.Label(hdr, text=f"modelo: {MODEL}  ·  idioma: {LANG or 'auto'}",
                 font=("Segoe UI", 9), bg=BG, fg=MUTED).pack(side="right", pady=4)

        ttk.Separator(self).pack(fill="x", padx=24, pady=12)

        tk.Label(self, text="URLs  (una por línea — YouTube, TikTok, Instagram…)",
                 font=("Segoe UI", 10), bg=BG, fg=TEXT2).pack(anchor="w", padx=24)

        url_frame = tk.Frame(self, bg=BORDER, bd=0)
        url_frame.pack(fill="x", padx=24, pady=(6, 0))

        self.url_box = tk.Text(
            url_frame, height=5, bg=SURFACE, fg=TEXT,
            insertbackground=GREEN, relief="flat",
            font=("Consolas", 10), padx=10, pady=8,
            selectbackground="#003d2e", wrap="none"
        )
        self.url_box.pack(fill="x")
        self.url_box.bind("<Control-Return>", lambda e: self._start())

        btn_row = tk.Frame(self, bg=BG)
        btn_row.pack(fill="x", padx=24, pady=12)

        self.btn_run = tk.Button(
            btn_row, text="▶  Transcribir",
            command=self._start,
            bg=GREEN, fg="#0e0e0e", activebackground="#00a87e",
            relief="flat", font=("Segoe UI", 10, "bold"),
            padx=20, pady=8, cursor="hand2", bd=0
        )
        self.btn_run.pack(side="left")

        self.btn_clear = tk.Button(
            btn_row, text="Limpiar",
            command=self._clear,
            bg=SURFACE, fg=TEXT2, activebackground=BORDER,
            relief="flat", font=("Segoe UI", 10),
            padx=16, pady=8, cursor="hand2", bd=0
        )
        self.btn_clear.pack(side="left", padx=(8, 0))

        self.btn_copy = tk.Button(
            btn_row, text="Copiar texto",
            command=self._copy,
            bg=SURFACE, fg=TEXT2, activebackground=BORDER,
            relief="flat", font=("Segoe UI", 10),
            padx=16, pady=8, cursor="hand2", bd=0
        )
        self.btn_copy.pack(side="right")

        self.status_var = tk.StringVar(value="Listo")
        status_row = tk.Frame(self, bg=BG)
        status_row.pack(fill="x", padx=24)

        self.dot = tk.Label(status_row, text="●", font=("Segoe UI", 10),
                            bg=BG, fg=MUTED)
        self.dot.pack(side="left")
        tk.Label(status_row, textvariable=self.status_var,
                 font=("Segoe UI", 9), bg=BG, fg=TEXT2).pack(side="left", padx=4)

        tk.Label(self, text="Transcripción",
                 font=("Segoe UI", 10), bg=BG, fg=TEXT2).pack(anchor="w", padx=24, pady=(14, 4))

        out_frame = tk.Frame(self, bg=BORDER)
        out_frame.pack(fill="both", expand=True, padx=24, pady=(0, 24))

        self.output = scrolledtext.ScrolledText(
            out_frame, bg=SURFACE, fg=TEXT,
            relief="flat", font=("Segoe UI", 10),
            padx=12, pady=10, wrap="word",
            insertbackground=GREEN,
            selectbackground="#003d2e"
        )
        self.output.pack(fill="both", expand=True)
        self.output.configure(state="disabled")

    def _start(self):
        urls = [u.strip() for u in self.url_box.get("1.0", "end").splitlines() if u.strip()]
        if not urls:
            self._set_status("Pega al menos una URL", color="#ff6b6b")
            return
        self.btn_run.configure(state="disabled", text="Procesando…")
        self._set_status("Iniciando…", color=GREEN)
        threading.Thread(target=self._run, args=(urls,), daemon=True).start()

    def _run(self, urls):
        try:
            from faster_whisper import WhisperModel
        except ImportError:
            self._append("❌ faster-whisper no instalado. Ejecuta:\n\n  pip install faster-whisper\n")
            self.after(0, lambda: self.btn_run.configure(state="normal", text="▶  Transcribir"))
            self._set_status("Error — ver output", color="#ff6b6b")
            return

        self._set_status("Cargando modelo…", color=GREEN)
        model = WhisperModel(MODEL, device="cpu", compute_type="int8")

        for i, url in enumerate(urls, 1):
            self._set_status(f"[{i}/{len(urls)}] Descargando…", color=GREEN)
            self._append(f"\n{'─'*50}\n🔗  {url}\n{'─'*50}\n")

            with tempfile.TemporaryDirectory() as tmp:
                audio_path = os.path.join(tmp, "audio.mp3")

                dl = subprocess.run(
                    ["yt-dlp", "-x", "--audio-format", "mp3",
                     "--no-playlist", "-o", audio_path, url],
                    capture_output=True, text=True
                )
                if dl.returncode != 0:
                    self._append(f"❌ Error descargando:\n{dl.stderr}\n")
                    continue

                self._set_status(f"[{i}/{len(urls)}] Transcribiendo…", color=GREEN)

                segments, info = model.transcribe(
                    audio_path,
                    language=LANG,
                    beam_size=1,
                    vad_filter=True,
                )

                self._append(f"🌐 Idioma detectado: {info.language}\n\n")
                for segment in segments:
                    self._append(segment.text.strip() + " ")

                self._append("\n")

        self._set_status(f"✓ Listo — {len(urls)} vídeo(s) procesados", color=GREEN)
        self.after(0, lambda: self.btn_run.configure(state="normal", text="▶  Transcribir"))

    def _append(self, text):
        def _do():
            self.output.configure(state="normal")
            self.output.insert("end", text)
            self.output.see("end")
            self.output.configure(state="disabled")
        self.after(0, _do)

    def _set_status(self, msg, color=None):
        def _do():
            self.status_var.set(msg)
            if color:
                self.dot.configure(fg=color)
        self.after(0, _do)

    def _copy(self):
        text = self.output.get("1.0", "end").strip()
        if text:
            self.clipboard_clear()
            self.clipboard_append(text)
            self._set_status("Copiado al portapapeles ✓", color=GREEN)

    def _clear(self):
        self.url_box.delete("1.0", "end")
        self.output.configure(state="normal")
        self.output.delete("1.0", "end")
        self.output.configure(state="disabled")
        self._set_status("Listo")
        self.dot.configure(fg=MUTED)


if __name__ == "__main__":
    app = TranscriberApp()
    app.mainloop()
