# -*- coding: utf-8 -*-
"""
MKV Cutcut GUI v1.1  —  by MrTOgRaS
MIT License
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import subprocess
import os
import re
import threading
import json
import webbrowser
import ctypes
import sys
from datetime import datetime

# ─── AYARLAR (CONFIG) İÇİN FONKSİYONLAR ────────────────────────────────────────
CONFIG_FILE = "mkvcutcut_settings.json"

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def save_config(data):
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
    except Exception:
        pass

# ─── EXE İÇİN KAYNAK YOLU VE FONT YÜKLEYİCİ ────────────────────────────────────
def resource_path(relative_path):
    """ PyInstaller ile paketlendiğinde dosyanın geçici klasördeki yolunu bulur """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def load_custom_font(font_path):
    """ Windows'a fontu geçici olarak program kapanana kadar yükler """
    if os.name == 'nt' and os.path.exists(font_path):
        FR_PRIVATE = 0x10
        ctypes.windll.gdi32.AddFontResourceExW(font_path, FR_PRIVATE, 0)

# ─── FONT AYARI ────────────────────────────────────────────────────────────────
def pick_font():
    import tkinter.font as tkf
    root_tmp = tk.Tk()
    root_tmp.withdraw()
    families = tkf.families()
    root_tmp.destroy()
    for f in ("Roboto", "Segoe UI", "Calibri", "Arial"):
        if f in families:
            return f
    return "TkDefaultFont"

FMAIN = None
FMONO = "Courier New"

# ─── DİL PAKETİ ────────────────────────────────────────────────────────────────
LANGS = {
    "English": {
        "app_title":       "🎬 MKV Cutcut GUI",
        "developer_info":  "Developer: MrTOgRaS  ·  mkvmerge Powered  ·  v1.1",
        "sec_paths":       "PROGRAM & FILE SETTINGS",
        "lbl_exe":         "mkvmerge.exe :",
        "lbl_mkv":         "MKV File     :",
        "lbl_outdir":      "Output Folder:",
        "lbl_outname":     "Output Name  :",
        "hint_outname":    " (empty = auto)",
        "info_hint":       "Select an MKV file or click 'Get Info' to load video details.",
        "sec_mode":        "CUT MODE",
        "rb_time":         "By Time",
        "rb_frame":        "By Frame",
        "ts_hint":         "Format: HH:MM:SS.mmm   e.g.  00:30:00.000",
        "lbl_start":       "Start :",
        "lbl_end":         "End :",
        "dur_prefix":      "Duration",
        "dur_warn":        "WARNING: End time is before start!",
        "lbl_sf":          "Start Frame :",
        "lbl_ef":          "End Frame :",
        "frame_note":      "mkvmerge snaps to the nearest keyframe.",
        "sec_sample":      "QUICK SAMPLE",
        "lbl_dur":         "Sample Duration :",
        "lbl_minutes":     "minutes",
        "lbl_start_at":    "Start At :",
        "rb_auto":         "Auto (Middle of video)",
        "rb_custom":       "Custom Time",
        "lbl_custom":      "Custom Start :",
        "lbl_tsfmt":       "(HH:MM:SS.mmm)",
        "btn_sample":      "GET SAMPLE",
        "sec_actions":     "ACTIONS",
        "btn_info":        "Get Video Info",
        "btn_cut":         "CUT FILE",
        "btn_clear":       "Clear Log",
        "btn_about":       "About",
        "sec_log":         "LOG OUTPUT",
        "st_ready":        "Ready",
        "st_info":         "Loading video info...",
        "st_running":      "Processing...",
        "st_done":         "Done!",
        "st_error":        "Error!",
        "dlg_done_t":      "Done",
        "dlg_done_b":      "File saved:\n\n{}",
        "dlg_smp_t":       "Sample Ready",
        "dlg_smp_b":       "Sample saved:\n\n{}",
        "dlg_err_t":       "Error",
        "dlg_err_cut":     "Cut failed. See log.",
        "dlg_err_smp":     "Sample failed. See log.",
        "e_noexe":         "Select mkvmerge.exe!",
        "e_noexe2":        "mkvmerge.exe not found!",
        "e_nomkv":         "Select an MKV file!",
        "e_nomkv2":        "MKV file not found!",
        "e_noout":         "Select output folder!",
        "e_tsfmt":         "Wrong time format.\nCorrect: HH:MM:SS.mmm\nExample: 00:30:00.000",
        "e_tsord":         "Start time must be before end time!",
        "e_frint":         "Frame numbers must be integers!",
        "e_frord":         "Start frame must be less than end frame!",
        "e_durinv":        "Enter a valid minute value!",
        "e_custts":        "Custom start format wrong!\nExample: 00:10:00.000",
        "log_welcome":     "MKV Cutcut GUI v1.1 started. Welcome!",
        "log_s1":          "Step 1: Select mkvmerge.exe",
        "log_s2":          "Step 2: Select your MKV file",
        "log_s3":          "Step 3: Set mode and times, then press CUT",
        "log_cleared":     "Log cleared.",
        "log_noviddur":    "WARNING: Video duration unknown -> starting from 00:10:00",
        "log_cut":         "Cut: {} -> {}",
        "log_fcut":        "Frame Cut: {} -> {}",
        "log_sample":      "Sample: {} -> {} ({} min)",
        "log_output":      "Output: {}",
        "log_done":        "Process completed successfully!",
        "log_fail":        "Failed! Exit code: {}",
    },
    "Türkçe": {
        "app_title":       "🎬 MKV Cutcut GUI",
        "developer_info":  "Geliştirici: MrTOgRaS  ·  mkvmerge Destekli  ·  v1.1",
        "sec_paths":       "PROGRAM & DOSYA AYARLARI",
        "lbl_exe":         "mkvmerge.exe :",
        "lbl_mkv":         "MKV Dosyasi  :",
        "lbl_outdir":      "Çıktı Klasörü:",
        "lbl_outname":     "Çıktı Adı    :",
        "hint_outname":    " (bos = otomatik)",
        "info_hint":       "Video bilgisi için MKV dosyası seçin veya Bilgi Al butonuna tıklayın.",
        "sec_mode":        "KESIM MODU",
        "rb_time":         "Zamana Göre",
        "rb_frame":        "Kareye Göre",
        "ts_hint":         "Format: SS:DD:SN.mmm   Örnek: 00:30:00.000",
        "lbl_start":       "Baslangıç :",
        "lbl_end":         "Bitiş :",
        "dur_prefix":      "Süre",
        "dur_warn":        "UYARI: Bitiş zamanı baslangıçtan önce!",
        "lbl_sf":          "Baslangıç Karesi :",
        "lbl_ef":          "Bitiş Karesi :",
        "frame_note":      "mkvmerge en yakın keyframe'i kullanır.",
        "sec_sample":      "HIZLI ÖRNEK AL",
        "lbl_dur":         "Örnek Süresi :",
        "lbl_minutes":     "dakika",
        "lbl_start_at":    "Baslangıç :",
        "rb_auto":         "Otomatik (Videonun Ortası)",
        "rb_custom":       "Özel Zaman",
        "lbl_custom":      "Özel Baslangıç :",
        "lbl_tsfmt":       "(SS:DD:SN.mmm)",
        "btn_sample":      "ÖRNEK AL",
        "sec_actions":     "İŞLEMLER",
        "btn_info":        "Video Bilgisi Al",
        "btn_cut":         "DOSYAYI KES",
        "btn_clear":       "Logu Temizle",
        "btn_about":       "Hakkında",
        "sec_log":         "LOG ÇIKTISI",
        "st_ready":        "Hazır",
        "st_info":         "Video bilgisi alınıyor...",
        "st_running":      "İşlem devam ediyor...",
        "st_done":         "Tamamlandı!",
        "st_error":        "Hata!",
        "dlg_done_t":      "Tamamlandı",
        "dlg_done_b":      "Dosya kaydedildi:\n\n{}",
        "dlg_smp_t":       "Örnek Hazır",
        "dlg_smp_b":       "Örnek dosya kaydedildi:\n\n{}",
        "dlg_err_t":       "Hata",
        "dlg_err_cut":     "Kesim başarısız. Log'u kontrol edin.",
        "dlg_err_smp":     "Örnek oluşturulamadı. Log'u kontrol edin.",
        "e_noexe":         "mkvmerge.exe yolunu seçin!",
        "e_noexe2":        "mkvmerge.exe bulunamadı!",
        "e_nomkv":         "MKV dosyası seçin!",
        "e_nomkv2":        "MKV dosyası bulunamadı!",
        "e_noout":         "Çıktı klasörü seçin!",
        "e_tsfmt":         "Zaman formatı yanlış.\nDoğru: SS:DD:SN.mmm\nÖrnek: 00:30:00.000",
        "e_tsord":         "Baslangıç zamanı bitişten önce olmalı!",
        "e_frint":         "Kare numaraları tam sayı olmalı!",
        "e_frord":         "Baslangıç karesi bitiş karesinden küçük olmalı!",
        "e_durinv":        "Geçerli bir dakika değeri girin!",
        "e_custts":        "Özel baslangic zamanı formatı yanlış!\nÖrnek: 00:10:00.000",
        "log_welcome":     "MKV Cutcut GUI v1.1 başlatıldı. Hoş geldiniz!",
        "log_s1":          "Adim 1: mkvmerge.exe seçin.",
        "log_s2":          "Adim 2: MKV dosyanızı seçin.",
        "log_s3":          "Adim 3: Mod ve zamanları ayarlayın, sonra KES'e basın.",
        "log_cleared":     "Log temizlendi.",
        "log_noviddur":    "UYARI: Video süresi bilinmiyor -> 00:10:00 dan başlanıyor",
        "log_cut":         "Kesim: {} -> {}",
        "log_fcut":        "Kare Kesim: {} -> {}",
        "log_sample":      "Örnek: {} -> {} ({} dk)",
        "log_output":      "Çıktı: {}",
        "log_done":        "İşlem başarıyla tamamlandı!",
        "log_fail":        "Başarısız! Çıkış kodu: {}",
    },
    "Deutsch": {
        "app_title":       "🎬 MKV Cutcut GUI",
        "developer_info":  "Entwickler: MrTOgRaS  ·  mkvmerge Powered  ·  v1.1",
        "sec_paths":       "PROGRAMM & DATEI-EINSTELLUNGEN",
        "lbl_exe":         "mkvmerge.exe :",
        "lbl_mkv":         "MKV-Datei    :",
        "lbl_outdir":      "Ausgabeordner:",
        "lbl_outname":     "Ausgabename  :",
        "hint_outname":    " (leer = automatisch)",
        "info_hint":       "MKV-Datei waehlen oder 'Videoinfo' klicken.",
        "sec_mode":        "SCHNITTMODUS",
        "rb_time":         "Nach Zeit",
        "rb_frame":        "Nach Frame",
        "ts_hint":         "Format: HH:MM:SS.mmm   z.B.  00:30:00.000",
        "lbl_start":       "Startzeit :",
        "lbl_end":         "Endzeit :",
        "dur_prefix":      "Dauer",
        "dur_warn":        "WARNUNG: Endzeit liegt vor Startzeit!",
        "lbl_sf":          "Startframe :",
        "lbl_ef":          "Endframe :",
        "frame_note":      "mkvmerge springt zum naechsten Keyframe.",
        "sec_sample":      "SCHNELLVORSCHAU",
        "lbl_dur":         "Beispieldauer :",
        "lbl_minutes":     "Minuten",
        "lbl_start_at":    "Startpunkt :",
        "rb_auto":         "Automatisch (Mitte)",
        "rb_custom":       "Benutzerdefiniert",
        "lbl_custom":      "Eigener Start :",
        "lbl_tsfmt":       "(HH:MM:SS.mmm)",
        "btn_sample":      "VORSCHAU HOLEN",
        "sec_actions":     "AKTIONEN",
        "btn_info":        "Videoinfo holen",
        "btn_cut":         "DATEI SCHNEIDEN",
        "btn_clear":       "Log leeren",
        "btn_about":       "Über",
        "sec_log":         "LOG-AUSGABE",
        "st_ready":        "Bereit",
        "st_info":         "Lade Videoinfo...",
        "st_running":      "Wird verarbeitet...",
        "st_done":         "Fertig!",
        "st_error":        "Fehler!",
        "dlg_done_t":      "Fertig",
        "dlg_done_b":      "Datei gespeichert:\n\n{}",
        "dlg_smp_t":       "Vorschau fertig",
        "dlg_smp_b":       "Vorschau gespeichert:\n\n{}",
        "dlg_err_t":       "Fehler",
        "dlg_err_cut":     "Schnitt fehlgeschlagen. Log pruefen.",
        "dlg_err_smp":     "Vorschau fehlgeschlagen. Log pruefen.",
        "e_noexe":         "mkvmerge.exe auswaehlen!",
        "e_noexe2":        "mkvmerge.exe nicht gefunden!",
        "e_nomkv":         "MKV-Datei auswaehlen!",
        "e_nomkv2":        "MKV-Datei nicht gefunden!",
        "e_noout":         "Ausgabeordner auswaehlen!",
        "e_tsfmt":         "Falsches Zeitformat.\nKorrekt: HH:MM:SS.mmm\nBeispiel: 00:30:00.000",
        "e_tsord":         "Startzeit muss vor Endzeit liegen!",
        "e_frint":         "Frame-Nummern muessen ganze Zahlen sein!",
        "e_frord":         "Startframe muss kleiner als Endframe sein!",
        "e_durinv":        "Gueltigen Minutenwert eingeben!",
        "e_custts":        "Eigenes Startformat falsch!\nBeispiel: 00:10:00.000",
        "log_welcome":     "MKV Cutcut GUI v1.1 gestartet. Willkommen!",
        "log_s1":          "Schritt 1: mkvmerge.exe auswaehlen.",
        "log_s2":          "Schritt 2: MKV-Datei auswaehlen.",
        "log_s3":          "Schritt 3: Modus einstellen, dann SCHNEIDEN druecken.",
        "log_cleared":     "Log geleert.",
        "log_noviddur":    "WARNUNG: Videodauer unbekannt -> Start bei 00:10:00",
        "log_cut":         "Schnitt: {} -> {}",
        "log_fcut":        "Frame-Schnitt: {} -> {}",
        "log_sample":      "Vorschau: {} -> {} ({} Min)",
        "log_output":      "Ausgabe: {}",
        "log_done":        "Vorgang erfolgreich abgeschlossen!",
        "log_fail":        "Fehlgeschlagen! Exit-Code: {}",
    },
}

LANG_ORDER = ["English", "Türkçe", "Deutsch"]


# ─── ABOUT PENCERESI ───────────────────────
def show_about(root, colors):
    BG    = colors["bg"]
    CARD  = colors["card"]
    ACC   = colors["accent"]
    ACC2  = colors["accent2"]
    TXT   = colors["text"]
    DIM   = colors["dim"]
    WARN  = colors["warn"]
    OK    = colors["success"]
    FM    = colors["font"]

    win = tk.Toplevel(root)
    win.title("About — MKV Cutcut GUI")
    win.geometry("580x680")
    win.resizable(False, False)
    win.configure(bg=BG)
    win.grab_set()

    # --- baslik ---
    hdr = tk.Frame(win, bg=BG, pady=14)
    hdr.pack(fill="x")
    tk.Label(hdr, text="🎬 MKV Cutcut GUI  v1.1",
             font=(FM, 17, "bold"), bg=BG, fg=ACC).pack()
    tk.Label(hdr, text="by MrTOgRaS",
             font=(FM, 9), bg=BG, fg=DIM).pack()

    # --- scrollable body ---
    body_outer = tk.Frame(win, bg=BG)
    body_outer.pack(fill="both", expand=True, padx=0, pady=0)

    canvas  = tk.Canvas(body_outer, bg=BG, highlightthickness=0)
    vsb     = ttk.Scrollbar(body_outer, orient="vertical", command=canvas.yview)
    body    = tk.Frame(canvas, bg=BG, padx=26, pady=16)
    
    body.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=body, anchor="nw")
    canvas.configure(yscrollcommand=vsb.set)
    canvas.pack(side="left", fill="both", expand=True)
    vsb.pack(side="right", fill="y")
    
    # Scroll Hatası Düzeltmesi
    def _scroll_about(e):
        try:
            canvas.yview_scroll(int(-1*(e.delta/120)), "units")
        except tk.TclError:
            pass
    win.bind("<MouseWheel>", _scroll_about)

    def sep(col=None):
        tk.Frame(body, bg=col or "#334155", height=1).pack(fill="x", pady=8)

    def kv(label, value, vfg=None, bold=False):
        f = tk.Frame(body, bg=BG)
        f.pack(fill="x", pady=2)
        tk.Label(f, text=label, width=16, anchor="w", bg=BG, fg=DIM,
                 font=(FM, 9, "bold")).pack(side="left")
        tk.Label(f, text=value, anchor="w", bg=BG,
                 fg=vfg or TXT,
                 font=(FM, 9, "bold" if bold else "normal")).pack(side="left")

    def section_title(txt, col=None):
        tk.Label(body, text=txt, bg=BG, fg=col or ACC,
                 font=(FM, 9, "bold"), anchor="w").pack(fill="x", pady=(6,2))

    # ── Genel bilgi
    section_title("[ PROGRAM INFO ]")
    kv("Program",    "MKV Cutcut GUI")
    kv("Version",    "1.1")
    kv("Released",   "March 2026")
    kv("Platform",   "Windows")
    kv("Language",   "ENG  /  TR  /  DE")

    sep()

    # ── Açıklama
    section_title("[ DESCRIPTION ]")
    desc_box = tk.Frame(body, bg=CARD, padx=12, pady=10)
    desc_box.pack(fill="x", pady=(2,0))
    tk.Label(desc_box,
             text=(
                 "A lightweight GUI front-end for mkvmerge.\n"
                 "Cut MKV files by time or frame range, extract\n"
                 "quick samples, and view detailed track info\n"
                 "— with ZERO re-encoding."
             ),
             bg=CARD, fg=TXT, font=(FM, 9), justify="left", anchor="w"
             ).pack(fill="x")

    sep()

    # ── Kütüphaneler
    section_title("[ LIBRARIES USED ]")
    lib_frame = tk.Frame(body, bg=CARD, padx=12, pady=10)
    lib_frame.pack(fill="x", pady=(2,0))
    libs = [
        ("tkinter",    "GUI framework  —  Python standard library"),
        ("subprocess", "mkvmerge process control  —  stdlib"),
        ("threading",  "Non-blocking execution  —  stdlib"),
        ("json",       "mkvmerge JSON output parsing  —  stdlib"),
        ("re",         "Timestamp format validation  —  stdlib"),
        ("os",         "File & path operations  —  stdlib"),
        ("webbrowser", "URL opening  —  stdlib"),
    ]
    for lib, desc in libs:
        f2 = tk.Frame(lib_frame, bg=CARD)
        f2.pack(fill="x", pady=1)
        tk.Label(f2, text=lib, width=13, anchor="w",
                 bg=CARD, fg=ACC2,
                 font=(FMONO, 9, "bold")).pack(side="left")
        tk.Label(f2, text=desc, anchor="w",
                 bg=CARD, fg=DIM,
                 font=(FM, 8)).pack(side="left")

    sep()

    # ── Yazar / Iletisim
    section_title("[ AUTHOR & CONTACT ]")
    kv("Author",  "Murat Ogras  (MrTOgRaS)", TXT, bold=True)
    kv("E-Mail",  "mrtogras@proton.me", ACC2, bold=True)

    sep()

    # ── Lisans
    section_title("[ LICENSE ]", OK)
    lic_box = tk.Frame(body, bg="#064e3b", padx=14, pady=12,
                       highlightthickness=1, highlightbackground=OK)
    lic_box.pack(fill="x", pady=(2,0))
    tk.Label(lic_box, text="MIT License",
             bg="#064e3b", fg=OK,
             font=(FM, 13, "bold"), anchor="w").pack(fill="x")
    tk.Label(lic_box,
             text=(
                 "Copyright (c) 2026  Murat Ogras (MrTOgRaS)\n\n"
                 "Permission is hereby granted, free of charge, to any person\n"
                 "obtaining a copy of this software to use, copy, modify, merge,\n"
                 "publish, distribute, sublicense, and/or sell copies, subject to:\n\n"
                 "The above copyright notice and this permission notice shall\n"
                 "be included in all copies or substantial portions of the Software."
             ),
             bg="#064e3b", fg="#a7f3d0",
             font=(FM, 8), justify="left", anchor="w").pack(fill="x", pady=(6,0))

    sep()

    # ── Regards to Bunkus (Tıklanabilir Link ile)
    regards_box = tk.Frame(body, bg="#451a03", padx=14, pady=14,
                           highlightthickness=2, highlightbackground=WARN)
    regards_box.pack(fill="x", pady=(2, 16))
    tk.Label(regards_box, text="Regards to Bunkus!",
             bg="#451a03", fg=WARN,
             font=(FM, 14, "bold italic"), anchor="w").pack(fill="x")
    tk.Label(regards_box,
             text="Moritz Bunkus  —  creator of MKVToolNix & mkvmerge",
             bg="#451a03", fg="#fde68a",
             font=(FM, 9), anchor="w").pack(fill="x", pady=(4,0))
             
    # Tıklanabilir Link Alanı
    link_lbl = tk.Label(regards_box,
             text="(MKVToolNix Download)",
             bg="#451a03", fg=ACC2, cursor="hand2",
             font=(FM, 9, "bold underline"), anchor="w")
    link_lbl.pack(fill="x", pady=(2,0))
    link_lbl.bind("<Button-1>", lambda e: webbrowser.open_new("https://mkvtoolnix.download/downloads.html#windows"))

    tk.Button(win, text="  Close  ", command=win.destroy,
              bg=ACC, fg="#0f172a", relief="flat",
              padx=20, pady=8, cursor="hand2",
              font=(FM, 9, "bold"), bd=0,
              activebackground=ACC2).pack(pady=10)


# ─── ANA UYGULAMA ──────────────────────────────────────────────────────────────
class MKVCutCut:
    def __init__(self, root):
        self.root = root
        self.root.title("🎬 MKV Cutcut GUI v1.1")
        self.root.geometry("940x740")
        self.root.minsize(900, 680)

        # İKON EKLEME
        try:
            self.root.iconbitmap(resource_path("icon.ico"))
        except Exception:
            pass

        # Renk Paleti
        self.BG = "#0f172a"
        self.CARD = "#1e293b"
        self.CARD2 = "#0b1120"
        self.ACC = "#06b6d4"
        self.ACC2 = "#38bdf8"
        self.TXT = "#f8fafc"
        self.DIM = "#94a3b8"
        self.OK = "#10b981"
        self.ERR = "#ef4444"
        self.WARN = "#f59e0b"
        self.BORDER = "#334155"

        global FMAIN
        FMAIN = pick_font()
        self.root.configure(bg=self.BG)

        # ─── AYARLARI YÜKLE ───
        self.config_data = load_config()

        # Değişkenler
        self.lang_var = tk.StringVar(value="English")
        
        # mkvmerge yolunu config dosyasından çekip başlat
        saved_mkv_exe = self.config_data.get("mkvmerge_path", "")
        self.mkv_exe = tk.StringVar(value=saved_mkv_exe)
        # Yol her değiştiğinde json dosyasına kaydetmesi için izleyici(trace) ekliyoruz
        self.mkv_exe.trace_add("write", self._save_exe_path)

        self.mkv_file = tk.StringVar()
        self.out_dir = tk.StringVar()
        self.out_name = tk.StringVar()
        
        self.cut_mode = tk.StringVar(value="time")
        self.t_start = tk.StringVar(value="00:00:00.000")
        self.t_end = tk.StringVar(value="00:05:00.000")
        self.f_start = tk.StringVar(value="0")
        self.f_end = tk.StringVar(value="7200")
        
        self.smp_dur = tk.StringVar(value="5")
        self.smp_mode = tk.StringVar(value="auto")
        self.smp_custom = tk.StringVar(value="00:10:00.000")
        self.vid_info = {}

        self._build()
        self._lang_apply()

    def _save_exe_path(self, *args):
        """ mkvmerge yolunu config dosyasina kaydeder """
        self.config_data["mkvmerge_path"] = self.mkv_exe.get()
        save_config(self.config_data)

    def T(self, k):
        return LANGS[self.lang_var.get()].get(k, k)

    def _colors(self):
        return {
            "bg": self.BG, "card": self.CARD, "accent": self.ACC,
            "accent2": self.ACC2, "text": self.TXT, "dim": self.DIM,
            "success": self.OK, "warn": self.WARN, "font": FMAIN
        }

    # MKVMerge'e gönderilecek arayüz dili
    def _mkv_lang(self):
        lang = self.lang_var.get()
        if lang == "Türkçe": return "tr"
        elif lang == "Deutsch": return "de"
        return "en"

    def _build(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TProgressbar", troughcolor=self.CARD2, background=self.ACC, borderwidth=0)

        # 1. FOOTER
        self.footer = tk.Frame(self.root, bg=self.CARD2, pady=4)
        self.footer.pack(side="bottom", fill="x")
        self.lbl_dev = tk.Label(self.footer, text="", font=(FMAIN, 8), bg=self.CARD2, fg=self.DIM)
        self.lbl_dev.pack()

        # 2. ANA FRAME
        self.sf = tk.Frame(self.root, bg=self.BG)
        self.sf.pack(side="top", fill="both", expand=True)

        # ── HEADER ──
        self.hdr = tk.Frame(self.sf, bg=self.BG, pady=5)
        self.hdr.pack(fill="x")
        
        lang_row = tk.Frame(self.hdr, bg=self.BG)
        lang_row.pack(anchor="ne", padx=20)
        for lng in LANG_ORDER:
            tk.Radiobutton(lang_row, text=lng, variable=self.lang_var, value=lng, command=self._lang_apply,
                           bg=self.BG, fg=self.DIM, selectcolor=self.BG, font=(FMAIN, 8)).pack(side="left", padx=5)

        self.lbl_title = tk.Label(self.hdr, text="", font=(FMAIN, 24, "bold"), bg=self.BG, fg=self.ACC)
        self.lbl_title.pack()

        # ── BÖLÜM 1: YOLLAR ──
        self.sec1 = self._sec(self.sf)
        self.pr_exe = self._pathrow(self.sf, self.mkv_exe, lambda: self._bfile(self.mkv_exe, [("EXE","*.exe")]))
        self.pr_mkv = self._pathrow(self.sf, self.mkv_file, lambda: self._bfile(self.mkv_file, [("MKV","*.mkv"), ("Video","*.mkv *.mp4 *.avi *.ts")]), after=self._mkv_sel)
        self.pr_out = self._pathrow(self.sf, self.out_dir, lambda: self._bdir(self.out_dir))

        nr = tk.Frame(self.sf, bg=self.BG)
        nr.pack(fill="x", padx=18, pady=2)
        
        self.lbl_oname = tk.Label(nr, text="", width=14, anchor="w", bg=self.BG, fg=self.DIM, font=(FMAIN, 9))
        self.lbl_oname.pack(side="left")
        tk.Entry(nr, textvariable=self.out_name, bg=self.CARD2, fg=self.TXT, insertbackground=self.TXT, relief="flat", highlightthickness=1, highlightbackground=self.BORDER).pack(side="left", fill="x", expand=True, ipady=4)
        
        self.lbl_ohint = tk.Label(nr, text="", bg=self.BG, fg=self.DIM, font=(FMAIN,8))
        self.lbl_ohint.pack(side="left", padx=(5,0))

        self.info_box = tk.Frame(self.sf, bg=self.CARD, pady=4, padx=12)
        self.info_box.pack(fill="x", padx=18, pady=5)
        self.info_lbl = tk.Label(self.info_box, text="", bg=self.CARD, fg=self.DIM, font=(FMAIN, 9), anchor="w", justify="left")
        self.info_lbl.pack(fill="x")

        # ── DASHBOARD MİMARİSİ ──
        self.dash_frame = tk.Frame(self.sf, bg=self.BG)
        self.dash_frame.pack(fill="x", padx=18, pady=0)

        # SOL PANEL (CUT MODE)
        self.left_pane = tk.Frame(self.dash_frame, bg=self.BG)
        self.left_pane.pack(side="left", fill="both", expand=True, padx=(0, 10))

        self.sec2 = self._sec(self.left_pane, is_child=True)
        mr = tk.Frame(self.left_pane, bg=self.BG)
        mr.pack(fill="x", pady=2)
        self.rb_time = tk.Radiobutton(mr, text="", variable=self.cut_mode, value="time", command=self._toggle_mode, bg=self.BG, fg=self.TXT, selectcolor=self.BG)
        self.rb_time.pack(side="left", padx=5)
        self.rb_frame = tk.Radiobutton(mr, text="", variable=self.cut_mode, value="frame", command=self._toggle_mode, bg=self.BG, fg=self.TXT, selectcolor=self.BG)
        self.rb_frame.pack(side="left", padx=5)

        self.cc = tk.Frame(self.left_pane, bg=self.BG)
        self.cc.pack(fill="x", pady=2)

        # Time Panel
        self.tf = tk.Frame(self.cc, bg=self.CARD, pady=8, padx=14)
        self.tf.pack(fill="x")
        self.ts_hint_lbl = tk.Label(self.tf, text="", bg=self.CARD, fg=self.DIM, font=(FMAIN, 8))
        self.ts_hint_lbl.grid(row=0, column=0, columnspan=4, sticky="w", pady=(0,4))
        
        self.lbl_s = tk.Label(self.tf, text="", bg=self.CARD, fg=self.TXT, font=(FMAIN, 10))
        self.lbl_s.grid(row=1, column=0, sticky="w")
        self.ent_s = tk.Entry(self.tf, textvariable=self.t_start, width=13, bg=self.CARD2, fg=self.ACC, font=(FMONO, 12, "bold"), relief="flat", highlightthickness=1, highlightbackground=self.BORDER)
        self.ent_s.grid(row=1, column=1, padx=(5,10), ipady=4)
        
        self.lbl_e = tk.Label(self.tf, text="", bg=self.CARD, fg=self.TXT, font=(FMAIN, 10))
        self.lbl_e.grid(row=1, column=2, sticky="w")
        self.ent_e = tk.Entry(self.tf, textvariable=self.t_end, width=13, bg=self.CARD2, fg=self.ACC, font=(FMONO, 12, "bold"), relief="flat", highlightthickness=1, highlightbackground=self.BORDER)
        self.ent_e.grid(row=1, column=3, padx=(5,0), ipady=4)
        
        self.dur_lbl = tk.Label(self.tf, text="", bg=self.CARD, fg=self.OK, font=(FMAIN, 9, "bold"))
        self.dur_lbl.grid(row=2, column=0, columnspan=4, sticky="w", pady=(6,0))
        self.t_start.trace_add("write", self._upd_dur); self.t_end.trace_add("write", self._upd_dur)

        # Frame Panel
        self.ff = tk.Frame(self.cc, bg=self.CARD, pady=8, padx=14)
        
        self.lbl_sf = tk.Label(self.ff, text="", bg=self.CARD, fg=self.TXT, font=(FMAIN, 10))
        self.lbl_sf.grid(row=0, column=0, sticky="w")
        tk.Entry(self.ff, textvariable=self.f_start, width=13, bg=self.CARD2, fg=self.WARN, font=(FMONO, 12, "bold"), relief="flat", highlightthickness=1, highlightbackground=self.BORDER).grid(row=0, column=1, padx=(5,10), ipady=4)
        
        self.lbl_ef = tk.Label(self.ff, text="", bg=self.CARD, fg=self.TXT, font=(FMAIN, 10))
        self.lbl_ef.grid(row=0, column=2, sticky="w")
        tk.Entry(self.ff, textvariable=self.f_end, width=13, bg=self.CARD2, fg=self.WARN, font=(FMONO, 12, "bold"), relief="flat", highlightthickness=1, highlightbackground=self.BORDER).grid(row=0, column=3, padx=(5,0), ipady=4)

        self.fn_lbl = tk.Label(self.ff, text="", bg=self.CARD, fg=self.WARN, font=(FMAIN, 8))
        self.fn_lbl.grid(row=1, column=0, columnspan=4, sticky="w", pady=(6,0))

        # SAĞ PANEL (QUICK SAMPLE)
        self.right_pane = tk.Frame(self.dash_frame, bg=self.BG)
        self.right_pane.pack(side="right", fill="both", expand=True, padx=(10, 0))

        self.sec_smp = self._sec(self.right_pane, is_child=True)
        sp = tk.Frame(self.right_pane, bg=self.CARD, pady=8, padx=14)
        sp.pack(fill="x", pady=2)
        
        r1 = tk.Frame(sp, bg=self.CARD); r1.pack(fill="x", pady=2)
        self.lbl_s_dur = tk.Label(r1, text="", bg=self.CARD, fg=self.TXT, font=(FMAIN, 10))
        self.lbl_s_dur.pack(side="left")
        tk.Spinbox(r1, textvariable=self.smp_dur, from_=1, to=120, width=5, bg=self.CARD2, fg=self.ACC, relief="flat", highlightthickness=1, highlightbackground=self.BORDER).pack(side="left", padx=8, ipady=3)
        self.lbl_s_min = tk.Label(r1, text="", bg=self.CARD, fg=self.DIM, font=(FMAIN, 9))
        self.lbl_s_min.pack(side="left")
        
        r2 = tk.Frame(sp, bg=self.CARD); r2.pack(fill="x", pady=4)
        self.lbl_s_sat = tk.Label(r2, text="", bg=self.CARD, fg=self.TXT, font=(FMAIN, 10))
        self.lbl_s_sat.pack(side="left")
        self.rb_s_auto = tk.Radiobutton(r2, text="", variable=self.smp_mode, value="auto", bg=self.CARD, fg=self.TXT, selectcolor=self.BG, command=self._toggle_smp)
        self.rb_s_auto.pack(side="left", padx=2)
        self.rb_s_cust = tk.Radiobutton(r2, text="", variable=self.smp_mode, value="custom", bg=self.CARD, fg=self.TXT, selectcolor=self.BG, command=self._toggle_smp)
        self.rb_s_cust.pack(side="left", padx=2)

        r3 = tk.Frame(sp, bg=self.CARD); r3.pack(fill="x", pady=2)
        self.lbl_cust = tk.Label(r3, text="", bg=self.CARD, fg=self.DIM, font=(FMAIN,9))
        self.lbl_cust.pack(side="left")
        self.smp_entry = tk.Entry(r3, textvariable=self.smp_custom, width=12, state="disabled", bg=self.CARD2, fg=self.ACC, font=(FMONO,11), relief="flat", highlightthickness=1, highlightbackground=self.BORDER, disabledbackground=self.CARD2, disabledforeground=self.DIM)
        self.smp_entry.pack(side="left", padx=8, ipady=3)
        self.lbl_tsfmt = tk.Label(r3, text="", bg=self.CARD, fg=self.DIM, font=(FMAIN,8))
        self.lbl_tsfmt.pack(side="left")

        self.btn_smp = tk.Button(sp, text="", command=self._get_sample, bg=self.WARN, fg="#0f172a", font=(FMAIN, 9, "bold"), padx=15, pady=6, bd=0)
        self.btn_smp.pack(anchor="w", pady=(8,0))

        # ── BÖLÜM 4: BUTONLAR VE İŞLEMLER ──
        self.sec3 = self._sec(self.sf)
        br = tk.Frame(self.sf, bg=self.BG)
        br.pack(fill="x", padx=18, pady=4)
        
        self.btn_inf = tk.Button(br, text="", command=self._get_info, bg=self.CARD, fg=self.ACC, font=(FMAIN, 9, "bold"), padx=15, pady=8, bd=0)
        self.btn_inf.pack(side="left", padx=4)
        self.btn_cut = tk.Button(br, text="", command=self._cut, bg=self.ACC, fg="#0f172a", font=(FMAIN, 9, "bold"), padx=15, pady=8, bd=0)
        self.btn_cut.pack(side="left", padx=4)
        self.btn_clr = tk.Button(br, text="", command=self._clear_log, bg=self.CARD, fg=self.DIM, font=(FMAIN, 9, "bold"), padx=15, pady=8, bd=0)
        self.btn_clr.pack(side="left", padx=4)
        self.btn_abt = tk.Button(br, text="", command=lambda: show_about(self.root, self._colors()), bg=self.CARD, fg=self.TXT, font=(FMAIN, 9, "bold"), padx=15, pady=8, bd=0)
        self.btn_abt.pack(side="left", padx=4)

        self.progress = ttk.Progressbar(self.sf, maximum=100, mode="indeterminate", style="TProgressbar")
        self.progress.pack(fill="x", padx=18, pady=(5,2))
        
        self.st_lbl = tk.Label(self.sf, text="", bg=self.BG, fg=self.DIM, font=(FMAIN, 9), anchor="w")
        self.st_lbl.pack(fill="x", padx=18)

        # ── BÖLÜM 5: KONSOL / LOG ──
        self.sec4 = self._sec(self.sf)
        lw = tk.Frame(self.sf, bg=self.CARD, pady=2, padx=2)
        lw.pack(fill="both", expand=True, padx=18, pady=(0, 10))
        
        self.log = tk.Text(lw, bg=self.CARD2, fg="#00e676", font=(FMONO, 9), relief="flat", wrap="word", insertbackground="white")
        lsb = ttk.Scrollbar(lw, orient="vertical", command=self.log.yview)
        self.log.configure(yscrollcommand=lsb.set)
        
        self.log.pack(side="left", fill="both", expand=True)
        lsb.pack(side="right", fill="y")

    def _sec(self, parent, is_child=False):
        f = tk.Frame(parent, bg=self.BG)
        pad_x = 0 if is_child else 18
        f.pack(fill="x", padx=pad_x, pady=(8,2))
        lbl = tk.Label(f, text="", bg=self.BG, fg=self.ACC, font=(FMAIN, 10, "bold"))
        lbl.pack(side="left")
        tk.Frame(f, bg=self.BORDER, height=1).pack(side="left", fill="x", expand=True, padx=10)
        return lbl

    def _pathrow(self, parent, var, cmd, after=None):
        r = tk.Frame(parent, bg=self.BG)
        r.pack(fill="x", padx=18, pady=2)
        l = tk.Label(r, text="", width=14, anchor="w", bg=self.BG, fg=self.DIM, font=(FMAIN, 9))
        l.pack(side="left")
        tk.Entry(r, textvariable=var, bg=self.CARD2, fg=self.TXT, relief="flat", highlightthickness=1, highlightbackground=self.BORDER).pack(side="left", fill="x", expand=True, ipady=4)
        
        def _execute():
            cmd()
            if after:
                after()
                
        tk.Button(r, text="...", command=_execute, bg=self.ACC, fg="#0f172a", font=(FMAIN, 9, "bold"), bd=0, padx=10).pack(side="left", padx=5)
        return l

    def _lang_apply(self):
        t = LANGS[self.lang_var.get()]
        
        self.lbl_title.config(text=t["app_title"])
        self.lbl_dev.config(text=t["developer_info"])
        
        self.sec1.config(text="  " + t["sec_paths"])
        self.sec2.config(text="  " + t["sec_mode"])
        self.sec3.config(text="  " + t["sec_actions"])
        self.sec4.config(text="  " + t["sec_log"])
        self.sec_smp.config(text="  " + t["sec_sample"])

        self.pr_exe.config(text=t["lbl_exe"])
        self.pr_mkv.config(text=t["lbl_mkv"])
        self.pr_out.config(text=t["lbl_outdir"])
        
        self.lbl_oname.config(text=t["lbl_outname"])
        self.lbl_ohint.config(text=t["hint_outname"])
        self.info_lbl.config(text=t["info_hint"])
        
        self.rb_time.config(text=t["rb_time"])
        self.rb_frame.config(text=t["rb_frame"])
        self.ts_hint_lbl.config(text=t["ts_hint"])
        
        self.lbl_s.config(text=t["lbl_start"])
        self.lbl_e.config(text=t["lbl_end"])
        self.lbl_sf.config(text=t["lbl_sf"])
        self.lbl_ef.config(text=t["lbl_ef"])
        self.fn_lbl.config(text=t["frame_note"])
        
        self.lbl_s_dur.config(text=t["lbl_dur"])
        self.lbl_s_min.config(text=t["lbl_minutes"])
        self.lbl_s_sat.config(text=t["lbl_start_at"])
        self.rb_s_auto.config(text=t["rb_auto"])
        self.rb_s_cust.config(text=t["rb_custom"])
        self.lbl_cust.config(text=t["lbl_custom"])
        self.lbl_tsfmt.config(text=t["lbl_tsfmt"])
        self.btn_smp.config(text=t["btn_sample"])
        
        self.btn_inf.config(text=t["btn_info"])
        self.btn_cut.config(text=t["btn_cut"])
        self.btn_clr.config(text=t["btn_clear"])
        self.btn_abt.config(text=t["btn_about"])
        
        self.st_lbl.config(text=t["st_ready"])
        
        self.log.config(state="normal")
        self.log.delete("1.0", "end")
        self._log(t["log_welcome"], "OK")
        self._log(t["log_s1"])
        self._log(t["log_s2"])
        self._log(t["log_s3"])

    def _log(self, msg, lv="INFO"):
        colors = {
            "INFO": "#06b6d4",
            "ERROR": "#ef4444",
            "WARN": "#f59e0b",
            "CMD": "#38bdf8",
            "OK": "#10b981"
        }
        ts = datetime.now().strftime("%H:%M:%S")
        self.log.config(state="normal")
        self.log.insert("end", f"[{ts}] [{lv}] {msg}\n", lv)
        self.log.tag_config(lv, foreground=colors.get(lv, "#06b6d4"))
        self.log.see("end")
        self.log.config(state="disabled")

    def _clear_log(self):
        self.log.config(state="normal")
        self.log.delete("1.0", "end")
        self.log.config(state="disabled")

    def _bfile(self, var, ftypes):
        path = filedialog.askopenfilename(filetypes=ftypes)
        if path:
            var.set(path)

    def _bdir(self, var):
        path = filedialog.askdirectory()
        if path:
            var.set(path)

    def _mkv_sel(self):
        path = self.mkv_file.get()
        if path:
            base_name = os.path.splitext(os.path.basename(path))[0]
            self.out_name.set(base_name + "_cut")
            if not self.out_dir.get():
                self.out_dir.set(os.path.dirname(path))

    def _toggle_mode(self):
        if self.cut_mode.get() == "time":
            self.ff.pack_forget()
            self.tf.pack(fill="x")
        else:
            self.tf.pack_forget()
            self.ff.pack(fill="x")
            
    def _toggle_smp(self):
        self.smp_entry.config(
            state="normal" if self.smp_mode.get() == "custom" else "disabled")

    def _pts(self, t):
        m = re.match(r"^(\d+):(\d{2}):(\d{2})(?:[.,](\d+))?$", t.strip())
        if m:
            h = int(m.group(1))
            mn = int(m.group(2))
            s = int(m.group(3))
            fr = float("0." + m.group(4)) if m.group(4) else 0.0
            return h * 3600 + mn * 60 + s + fr
        return None

    def _s2t(self, sec):
        h = int(sec // 3600)
        m = int((sec % 3600) // 60)
        s = sec % 60
        return f"{h:02d}:{m:02d}:{s:06.3f}"

    def _upd_dur(self, *args):
        try:
            s = self._pts(self.t_start.get())
            e = self._pts(self.t_end.get())
            if s is not None and e is not None:
                d = e - s
                if d > 0:
                    self.dur_lbl.config(text=f"{self.T('dur_prefix')}: {self._s2t(d)}", fg=self.OK)
                else:
                    self.dur_lbl.config(text=self.T("dur_warn"), fg=self.ERR)
        except Exception:
            pass

    def _chk(self):
        if not self.mkv_exe.get() or not os.path.isfile(self.mkv_exe.get()):
            messagebox.showerror(self.T("dlg_err_t"), self.T("e_noexe"))
            return False
        if not self.mkv_file.get() or not os.path.isfile(self.mkv_file.get()):
            messagebox.showerror(self.T("dlg_err_t"), self.T("e_nomkv"))
            return False
        if not self.out_dir.get():
            messagebox.showerror(self.T("dlg_err_t"), self.T("e_noout"))
            return False
        return True

    def _get_info(self):
        if not self._chk():
            return
            
        def run():
            self.progress.start(8)
            self.st_lbl.config(text=self.T("st_info"))
            try:
                cmd = [self.mkv_exe.get(), "--ui-language", self._mkv_lang(), "--output-charset", "utf-8", "--identify", "--identification-format", "json", self.mkv_file.get()]
                self._log(f"CMD: {' '.join(cmd)}", "CMD")
                
                result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace', creationflags=0x08000000)
                if result.returncode in (0, 1):
                    data = json.loads(result.stdout)
                    duration_ns = data.get("container", {}).get("properties", {}).get("duration", 0)
                    duration_sec = duration_ns / 1e9
                    self.vid_info["duration"] = duration_sec
                    
                    self.info_lbl.config(text=f"File: {os.path.basename(self.mkv_file.get())} | Duration: {self._s2t(duration_sec)}")
                    
                    if duration_sec > 0:
                        self.t_end.set(self._s2t(duration_sec))
                        
                    self._log(f"Video Info Loaded: {self._s2t(duration_sec)}", "OK")
                else:
                    self._log(f"Identify Error: {result.stderr}", "ERROR")
            except Exception as ex:
                self._log(f"Error: {ex}", "ERROR")
            finally:
                self.progress.stop()
                self.st_lbl.config(text=self.T("st_ready"))
                
        threading.Thread(target=run, daemon=True).start()

    def _run_subprocess(self, cmd, success_msg, error_msg, out_path):
        def run():
            self.progress.start(8)
            self._log(f"CMD: {' '.join(cmd)}", "CMD")
            self.st_lbl.config(text=self.T("st_running"))
            try:
                proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding='utf-8', errors='replace', creationflags=0x08000000)
                for line in proc.stdout:
                    self._log(line.strip())
                proc.wait()
                
                if proc.returncode in (0, 1):
                    self._log(self.T("log_done"), "OK")
                    messagebox.showinfo(self.T("dlg_done_t"), success_msg.format(out_path))
                else:
                    self._log(self.T("log_fail").format(proc.returncode), "ERROR")
                    messagebox.showerror(self.T("dlg_err_t"), error_msg)
            except Exception as ex:
                self._log(f"Process Error: {ex}", "ERROR")
                messagebox.showerror(self.T("dlg_err_t"), error_msg)
            finally:
                self.progress.stop()
                self.st_lbl.config(text=self.T("st_ready"))
                
        threading.Thread(target=run, daemon=True).start()

    def _outpath(self, suffix=""):
        base = self.out_name.get().strip() or os.path.splitext(os.path.basename(self.mkv_file.get()))[0] + "_cut"
        if suffix:
            base += f"_{suffix}"
        out = os.path.join(self.out_dir.get(), base + ".mkv")
        i = 1
        while os.path.exists(out):
            out = os.path.join(self.out_dir.get(), f"{base}_{i}.mkv")
            i += 1
        return out

    def _cut(self):
        if not self._chk():
            return
            
        if self.cut_mode.get() == "time":
            st = self.t_start.get().strip()
            en = self.t_end.get().strip()
            
            ss = self._pts(st)
            es = self._pts(en)
            
            if ss is None or es is None or ss >= es:
                messagebox.showerror(self.T("dlg_err_t"), self.T("e_tsord"))
                return
                
            out = self._outpath()
            cmd = [self.mkv_exe.get(), "--ui-language", self._mkv_lang(), "--output-charset", "utf-8", "--output", out, "--split", f"parts:{st}-{en}", self.mkv_file.get()]
            self._log(self.T("log_cut").format(st, en))
            self._run_subprocess(cmd, self.T("dlg_done_b"), self.T("dlg_err_cut"), out)
            
        else:
            try:
                sf = int(self.f_start.get())
                ef = int(self.f_end.get())
            except ValueError:
                messagebox.showerror(self.T("dlg_err_t"), self.T("e_frint"))
                return
                
            if sf >= ef:
                messagebox.showerror(self.T("dlg_err_t"), self.T("e_frord"))
                return
                
            out = self._outpath("frames")
            cmd = [self.mkv_exe.get(), "--ui-language", self._mkv_lang(), "--output-charset", "utf-8", "--output", out, "--split", f"parts-frames:{sf}-{ef}", self.mkv_file.get()]
            self._log(self.T("log_fcut").format(sf, ef))
            self._run_subprocess(cmd, self.T("dlg_done_b"), self.T("dlg_err_cut"), out)

    def _get_sample(self):
        if not self._chk():
            return
            
        try:
            dm = float(self.smp_dur.get())
            if dm <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror(self.T("dlg_err_t"), self.T("e_durinv"))
            return
            
        ds = dm * 60.0
        
        if self.smp_mode.get() == "auto":
            vd = self.vid_info.get("duration", 0)
            ss = max(0, (vd / 2) - (ds / 2)) if vd > 0 else 600.0
        else:
            ss = self._pts(self.smp_custom.get())
            if ss is None:
                messagebox.showerror(self.T("dlg_err_t"), self.T("e_custts"))
                return
                
        se = ss + ds
        st_s = self._s2t(ss)
        en_s = self._s2t(se)
        
        out = self._outpath(f"sample_{int(dm)}min")
        cmd = [self.mkv_exe.get(), "--ui-language", self._mkv_lang(), "--output-charset", "utf-8", "--output", out, "--split", f"parts:{st_s}-{en_s}", self.mkv_file.get()]
        
        self._log(self.T("log_sample").format(st_s, en_s, int(dm)))
        self._run_subprocess(cmd, self.T("dlg_smp_b"), self.T("dlg_err_smp"), out)

if __name__ == "__main__":
    load_custom_font(resource_path("Roboto-Regular.ttf"))
    load_custom_font(resource_path("Roboto-Bold.ttf"))
    
    root = tk.Tk()
    app = MKVCutCut(root)
    root.mainloop()