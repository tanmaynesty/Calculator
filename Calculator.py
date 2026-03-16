import tkinter as tk
import tkinter.font as tkfont
import math
import datetime

BG_COLOR    = "#0d0d0d"
DISP_BG_COLOR = "#0a0a0a"
DISP_FG_COLOR = "#f5f5f0"
DISP_SEC_COLOR = "#888880"

PANEL_BG    = "#141414"
BTN_NUM     = "#1c1c1e"
BTN_OP      = "#2a2a2e"
BTN_CLEAR   = "#3a1010"
BTN_EQ      = "#b5451b"
TXT_PRIMARY = "#f5f5f0"
ACCENT      = "#e8622a"

WIN_W = 428
WIN_H_NORMAL = 709
WIN_H_HIST = 909

class RoundedFrame(tk.Canvas):
    def __init__(self, parent, bg_color, frame_color, border_color, radius=16, **kw):
        super().__init__(parent, bg=bg_color, highlightthickness=0, bd=0, **kw)
        self._bg_color = bg_color
        self._frame_color = frame_color
        self._border_color = border_color
        self._r = radius
        self.bind("<Configure>", self._draw)

    def _round_rect(self, x1, y1, x2, y2, r, **kw):
        pts = [
            x1+r, y1,  x2-r, y1,
            x2,   y1,  x2,   y1+r,
            x2,   y2-r, x2,  y2,
            x2-r, y2,  x1+r, y2,
            x1,   y2,  x1,   y2-r,
            x1,   y1+r, x1,  y1,
            x1+r, y1,
        ]
        return self.create_polygon(pts, smooth=True, **kw)

    def _draw(self, event=None):
        self.delete("border")
        w, h = self.winfo_width(), self.winfo_height()
        if w > 0 and h > 0:
            if self._border_color:
                self._round_rect(0, 0, w, h, self._r, fill=self._border_color, outline="", tags="border")
                self._round_rect(1, 1, w-1, h-1, self._r - 1, fill=self._frame_color, outline="", tags="border")
            else:
                self._round_rect(0, 0, w, h, self._r, fill=self._frame_color, outline="", tags="border")
        self.tag_lower("border")

class RoundButton(tk.Canvas):
    def __init__(self, parent, text, command, bg=BTN_NUM,
                 fg=TXT_PRIMARY, hover_bg=None, width=80, height=60,
                 text_font=None, radius=14, **kw):
        super().__init__(parent, width=width, height=height,
                         bg=PANEL_BG, highlightthickness=0, bd=0, **kw)
        self._bg       = bg
        self._hover_bg = hover_bg or self._lighten(bg, 28)
        self._press_bg = self._lighten(bg, 50)
        self._fg       = fg
        self._text     = text
        self._cmd      = command
        self._r        = radius
        self._font     = text_font or ("Helvetica", 24, "bold")

        self._draw(self._bg)
        self.bind("<Enter>",          self._on_enter)
        self.bind("<Leave>",          self._on_leave)
        self.bind("<ButtonPress-1>",  self._on_press)
        self.bind("<ButtonRelease-1>",self._on_release)

    @staticmethod
    def _lighten(hex_color, amount):
        hex_color = hex_color.lstrip("#")
        r, g, b = (int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        r = min(255, r + amount)
        g = min(255, g + amount)
        b = min(255, b + amount)
        return f"#{r:02x}{g:02x}{b:02x}"

    def _round_rect(self, x1, y1, x2, y2, r, **kw):
        pts = [
            x1+r, y1,  x2-r, y1,
            x2,   y1,  x2,   y1+r,
            x2,   y2-r, x2,  y2,
            x2-r, y2,  x1+r, y2,
            x1,   y2,  x1,   y2-r,
            x1,   y1+r, x1,  y1,
            x1+r, y1,
        ]
        return self.create_polygon(pts, smooth=True, **kw)

    def _draw(self, bg):
        self.delete("all")
        w, h = self.winfo_reqwidth(), self.winfo_reqheight()
        self._round_rect(0, 2, w, h, self._r, fill=self._lighten(bg, 18), outline="")
        self._round_rect(0, 0, w, h-2, self._r, fill=bg, outline="")
        self.create_text(w//2, (h-2)//2, text=self._text, fill=self._fg, font=self._font)

    def _on_enter(self, _):  self._draw(self._hover_bg)
    def _on_leave(self, _):  self._draw(self._bg)
    def _on_press(self, _):  self._draw(self._press_bg)
    def _on_release(self, e):
        self._draw(self._hover_bg)
        if self._cmd: self._cmd(self._text)

class Calculator(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Calculator")
        self.configure(bg=BG_COLOR)
        self.resizable(False, False)
        self.overrideredirect(True)
        self._check_fonts()
        self.minsize(WIN_W, WIN_H_NORMAL)
        self.maxsize(WIN_W, WIN_H_HIST)
        self._expr        = ""
        self._fresh       = False
        self._history     = []
        self._hist_shown  = False
        self._mem         = None
        self._build_title_bar()
        self._build_ui()
        self._bind_keys()  
        self.update_idletasks()
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f"{WIN_W}x{WIN_H_NORMAL}+{(sw-WIN_W)//2}+{(sh-WIN_H_NORMAL)//2}")
        self.after(10, self._apply_border_radius)

    def _apply_border_radius(self):
        try:
            import ctypes
            if self.tk.call('tk', 'windowingsystem') == 'win32':
                hwnd = ctypes.windll.user32.GetParent(self.winfo_id())
                rgn = ctypes.windll.gdi32.CreateRoundRectRgn(0, 0, self.winfo_width(), self.winfo_height(), 20, 20)
                ctypes.windll.user32.SetWindowRgn(hwnd, rgn, True)
        except Exception:
            pass

    def _close_window(self):
        self.destroy()

    def _start_move(self, event):
        self.x = event.x
        self.y = event.y

    def _do_move(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.winfo_x() + deltax
        y = self.winfo_y() + deltay
        self.geometry(f"+{x}+{y}")

    def _build_title_bar(self):
        self.title_bar = tk.Frame(self, bg=DISP_BG_COLOR, relief="flat", bd=0, highlightthickness=0)
        self.title_bar.pack(fill=tk.X, side=tk.TOP)
        self.title_bar.bind("<Button-1>", self._start_move)
        self.title_bar.bind("<B1-Motion>", self._do_move)
        title_label = tk.Label(self.title_bar, text="Calculator", bg=DISP_BG_COLOR, fg=DISP_SEC_COLOR, font=(self.font_family, 10, "bold"))
        title_label.pack(side=tk.LEFT, padx=16, pady=8)
        title_label.bind("<Button-1>", self._start_move)
        title_label.bind("<B1-Motion>", self._do_move)
        controls_frame = tk.Frame(self.title_bar, bg=DISP_BG_COLOR)
        controls_frame.pack(side=tk.RIGHT, padx=4)

        def make_control_btn(parent, text, cmd, hover_color, fg_col=TXT_PRIMARY):
            btn = tk.Button(parent, text=text, bg=DISP_BG_COLOR, fg=fg_col,
                            font=("Helvetica", 14), bd=0, highlightthickness=0,
                            activebackground=hover_color, activeforeground=fg_col,
                            command=cmd, width=3, cursor="hand2")
            btn.bind("<Enter>", lambda e: btn.config(bg=hover_color))
            btn.bind("<Leave>", lambda e: btn.config(bg=DISP_BG_COLOR))
            btn.pack(side=tk.LEFT, padx=2)
            return btn
            
        make_control_btn(controls_frame, "×", self._close_window, hover_color="#ff453a", fg_col="#ff6b6b")

    def _check_fonts(self):
        available_fonts = tkfont.families()
        if "Segoe UI" in available_fonts:
            self.font_family = "Segoe UI"
        elif "Helvetica Neue" in available_fonts:
            self.font_family = "Helvetica Neue"
        elif "Helvetica" in available_fonts:
            self.font_family = "Helvetica"
        else:
            self.font_family = "Arial"

        self.f_disp = (self.font_family, 48, "bold")
        self.f_sec  = (self.font_family, 16)
        self.f_btn  = (self.font_family, 24)
        self.f_fn   = (self.font_family, 18)
        self.f_hist = (self.font_family, 14)
        self.f_hist_btn = (self.font_family, 12, "bold")

    def _build_ui(self):
        disp_frame = RoundedFrame(self, bg_color=BG_COLOR, frame_color=DISP_BG_COLOR, border_color="#2a2a2a", radius=16)
        disp_frame.pack(fill=tk.X, expand=False, padx=4, pady=(0, 8))
        inner_disp = tk.Frame(disp_frame, bg=DISP_BG_COLOR, padx=16, pady=20)
        inner_disp.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        top_row = tk.Frame(inner_disp, bg=DISP_BG_COLOR)
        top_row.pack(fill=tk.X, pady=(0, 5))
        self._mem_label = tk.Label(top_row, text="", bg=DISP_BG_COLOR, fg=DISP_SEC_COLOR, font=self.f_sec, anchor=tk.W)
        self._mem_label.pack(side=tk.LEFT)
        self._expr_var = tk.StringVar(value="")
        tk.Label(top_row, textvariable=self._expr_var, bg=DISP_BG_COLOR, fg=DISP_SEC_COLOR, anchor=tk.E, font=self.f_sec).pack(side=tk.RIGHT, fill=tk.X, expand=True) 
        self._val_var = tk.StringVar(value="0")
        self._val_var_label = tk.Label(inner_disp, textvariable=self._val_var, bg=DISP_BG_COLOR, fg=DISP_FG_COLOR, anchor=tk.E, font=self.f_disp)
        self._val_var_label.pack(fill=tk.X, pady=(0, 0))
        self._val_var_label.bind("<Button-3>", self._copy_result)
        self._val_var_label.bind("<Button-2>", self._copy_result)
        self._hist_frame = tk.Frame(self, bg=DISP_BG_COLOR, padx=15, pady=0)
        hist_header = tk.Frame(self._hist_frame, bg=DISP_BG_COLOR)
        hist_header.pack(fill=tk.X, pady=(5, 5))
        tk.Label(hist_header, text="HISTORY", bg=DISP_BG_COLOR, fg=DISP_SEC_COLOR, font=self.f_hist_btn).pack(side=tk.LEFT)  
        clear_btn = RoundButton(hist_header, bg=PANEL_BG, fg="#ff6b6b", text="Clear", text_font=self.f_hist_btn, command=lambda x: self._clear_history(), width=60, height=30)
        clear_btn.pack(side=tk.RIGHT)

        self._hist_text = tk.Text(
            self._hist_frame, bg=DISP_BG_COLOR, fg=DISP_FG_COLOR,
            font=self.f_hist, height=8, bd=0,
            highlightthickness=0,
            state=tk.DISABLED, cursor="arrow"
        )
        self._hist_text.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        self._hist_text.tag_config("expr",   foreground=DISP_SEC_COLOR)
        self._hist_text.tag_config("result", foreground=DISP_FG_COLOR)
        self._hist_text.tag_config("sep",    foreground=PANEL_BG)
        self.panel = RoundedFrame(self, bg_color=BG_COLOR, frame_color=PANEL_BG, border_color="#2a2a2a", radius=16)
        self.panel.pack(pady=(0, 8))
        self.panel.grid_rowconfigure(0, minsize=8)
        self.panel.grid_rowconfigure(8, minsize=14)
        self.panel.grid_columnconfigure(0, minsize=8)
        self.panel.grid_columnconfigure(5, minsize=8)
        sp = dict(padx=3, pady=3)
        self._btn(self.panel, "HIST", 0, 0, bg=BTN_OP, fg=TXT_PRIMARY, text_font=self.f_fn, **sp)
        self._btn(self.panel, "MC",   0, 1, bg=BTN_OP, fg=TXT_PRIMARY, text_font=self.f_fn, **sp)
        self._btn(self.panel, "MR",   0, 2, bg=BTN_OP, fg=TXT_PRIMARY, text_font=self.f_fn, **sp)
        self._btn(self.panel, "MS",   0, 3, bg=BTN_OP, fg=TXT_PRIMARY, text_font=self.f_fn, **sp)

        self._btn(self.panel, "√",    1, 0, bg=BTN_OP, fg=TXT_PRIMARY, text_font=self.f_fn, **sp)
        self._btn(self.panel, "x²",   1, 1, bg=BTN_OP, fg=TXT_PRIMARY, text_font=self.f_fn, **sp)
        self._btn(self.panel, "1/x",  1, 2, bg=BTN_OP, fg=TXT_PRIMARY, text_font=self.f_fn, **sp)
        self._btn(self.panel, "DEL",  1, 3, bg=BTN_OP, fg="#ff6b6b", text_font=self.f_fn, **sp)

        self._btn(self.panel, "AC",   2, 0, bg=BTN_CLEAR, fg="#ff6b6b", text_font=self.f_fn, **sp)
        self._btn(self.panel, "+/-",  2, 1, bg=BTN_OP, fg=TXT_PRIMARY, text_font=self.f_fn, **sp)
        self._btn(self.panel, "%",    2, 2, bg=BTN_OP, fg=TXT_PRIMARY, text_font=self.f_fn, **sp)
        self._btn(self.panel, "÷",    2, 3, bg=BTN_OP, fg=ACCENT, **sp)

        self._btn(self.panel, "7",    3, 0, **sp)
        self._btn(self.panel, "8",    3, 1, **sp)
        self._btn(self.panel, "9",    3, 2, **sp)
        self._btn(self.panel, "×",    3, 3, bg=BTN_OP, fg=ACCENT, **sp)

        self._btn(self.panel, "4",    4, 0, **sp)
        self._btn(self.panel, "5",    4, 1, **sp)
        self._btn(self.panel, "6",    4, 2, **sp)
        self._btn(self.panel, "−",    4, 3, bg=BTN_OP, fg=ACCENT, **sp)

        self._btn(self.panel, "1",    5, 0, **sp)
        self._btn(self.panel, "2",    5, 1, **sp)
        self._btn(self.panel, "3",    5, 2, **sp)
        self._btn(self.panel, "+",    5, 3, bg=BTN_OP, fg=ACCENT, **sp)

        self._btn(self.panel, "0",    6, 0, colspan=2, width=196, **sp)
        self._btn(self.panel, ".",    6, 2, **sp)
        self._btn(self.panel, "=",    6, 3, bg=BTN_EQ, fg=TXT_PRIMARY, hover_bg="#d4561f", **sp)

    def _btn(self, parent, text, row, col, colspan=1, width=95, height=60, bg=BTN_NUM, fg=TXT_PRIMARY, hover_bg=None, text_font=None, **grid_kw):
        if text_font is None:
            text_font = self.f_btn
        b = RoundButton(parent, text=text, command=self._handle, bg=bg, fg=fg, hover_bg=hover_bg, width=width, height=height, text_font=text_font)
        
        pady_val = grid_kw.pop('pady', 0)
        b.grid(row=row+1, column=col+1, columnspan=colspan, pady=pady_val, **grid_kw)
        return b

    def _bind_keys(self):
        key_map = {
            "Key-0":"0","Key-1":"1","Key-2":"2","Key-3":"3","Key-4":"4",
            "Key-5":"5","Key-6":"6","Key-7":"7","Key-8":"8","Key-9":"9",
            "period":".","plus":"+","minus":"−",
            "asterisk":"×","slash":"÷",
            "Return":"=","KP_Enter":"=",
            "BackSpace":"DEL","Escape":"AC",
            "percent":"%",
        }
        for key, action in key_map.items():
            self.bind(f"<{key}>", lambda e, a=action: self._handle(a))

    def _toggle_history(self):
        if self._hist_shown:
            self._hist_frame.pack_forget()
            self._hist_shown = False
            self.geometry(f"{WIN_W}x{WIN_H_NORMAL}")
        else:
            self._hist_frame.pack(fill=tk.BOTH, expand=True, padx=8, before=self.panel)
            self._hist_shown = True
            self.geometry(f"{WIN_W}x{WIN_H_HIST}")
        self.update_idletasks()
        self.after(10, self._apply_border_radius)

    def _add_history(self, expr, result):
        self._history.append((expr, result))
        self._hist_text.config(state=tk.NORMAL)
        ts = datetime.datetime.now().strftime("%H:%M:%S")
        self._hist_text.insert("end", f"  {expr}\n", "expr")
        self._hist_text.insert("end", f"  = {result}   [{ts}]\n", "result")
        self._hist_text.insert("end", "  " + "─"*30 + "\n", "sep")
        self._hist_text.see("end")
        self._hist_text.config(state=tk.DISABLED)

    def _clear_history(self):
        self._history.clear()
        self._hist_text.config(state=tk.NORMAL)
        self._hist_text.delete("1.0", tk.END)
        self._hist_text.config(state=tk.DISABLED)

    def _copy_result(self, event=None):
        val = self._val_var.get()
        self.clipboard_clear()
        self.clipboard_append(val)
        original_color = self._val_var_label.cget("fg")
        self._val_var_label.config(fg="#34C759")
        self.after(300, lambda: self._val_var_label.config(fg=original_color))

    def _update_mem_label(self):
        if self._mem is not None:
            self._mem_label.config(text=f"M: {self._mem}")
        else:
            self._mem_label.config(text="")

    def _evaluate_expr(self, expr_str):
        if not expr_str:
            return 0
        expr = (expr_str.replace("×", "*")
                        .replace("÷", "/")
                        .replace("−", "-"))
        try:
            res = eval(expr, {"__builtins__": {}}, {"math": math})
            return res
        except Exception:
            return None

    def _apply_unary(self, op_name, func):
        if not self._expr:
            val = 0
        else:
            val = self._evaluate_expr(self._expr)
            
        if val is None:
            self._val_var.set("Error")
            self._fresh = True
            return

        try:
            result = func(val)
            if isinstance(result, float) and result.is_integer():
                result = int(result)
            elif isinstance(result, float):
                result = round(result, 10)
                
            self._add_history(f"{op_name}({self._expr})", result)
            self._expr_var.set(f"{op_name}({self._expr})")
            self._val_var.set(str(result))
            self._expr = str(result)
            self._fresh = True
        except ValueError:
            self._val_var.set("Domain Error")
            self._fresh = True
        except ZeroDivisionError:
            self._val_var.set("Divide by 0")
            self._fresh = True
        except Exception:
            self._val_var.set("Error")
            self._fresh = True

    def _handle(self, text):
        if text == "HIST":
            self._toggle_history()
            return
            
        if text == "MC":
            self._mem = None
            self._update_mem_label()
            return
            
        if text == "MR":
            if self._mem is not None:
                if self._fresh:
                    self._expr = str(self._mem)
                else:
                    self._expr += str(self._mem)
                self._val_var.set(self._expr)
                self._fresh = False
            return
            
        if text == "MS":
            val = self._evaluate_expr(self._expr)
            if val is not None:
                self._mem = int(val) if isinstance(val, float) and val.is_integer() else val
                self._update_mem_label()
            return
            
        if text == "AC":
            self._expr = ""
            self._fresh = False
            self._val_var.set("0")
            self._expr_var.set("")
            return
            
        if text == "DEL":
            if self._expr and not self._fresh:
                self._expr = self._expr[:-1]
                self._val_var.set(self._expr if self._expr else "0")
            return
            
        if text == "√":
            self._apply_unary("√", math.sqrt)
            return
            
        if text == "x²":
            self._apply_unary("sqr", lambda x: x*x)
            return
            
        if text == "1/x":
            def inv(x):
                if x == 0: raise ZeroDivisionError()
                return 1/x
            self._apply_unary("1/", inv)
            return
            
        if text == "+/-":
            self._apply_unary("neg", lambda x: -x)
            return
            
        if text == "%":
            self._apply_unary("pct", lambda x: x/100.0)
            return
            
        if text == "=":
            if not self._expr: return
            val = self._evaluate_expr(self._expr)
            if val is None:
                self._val_var.set("Syntax Error")
                self._fresh = True
                return
                
            if isinstance(val, float) and val.is_integer():
                val = int(val)
            elif isinstance(val, float):
                val = round(val, 10)
                
            self._add_history(self._expr, val)
            self._expr_var.set(self._expr + " =")
            self._val_var.set(str(val))
            self._expr = str(val)
            self._fresh = True
            return
            
        if self._fresh:
            if text in ("÷", "×", "−", "+"):
                self._expr += text
            elif text == ".":
                self._expr = "0."
            else:
                self._expr = text
            self._fresh = False
            self._expr_var.set("")
        else:
            self._expr += text

        display_str = self._expr
        if len(display_str) > 16:
            self._val_var_label.config(font=(self.font_family, 32, "bold"))
        else:
            self._val_var_label.config(font=self.f_disp)
        
        self._val_var.set(display_str if display_str else "0")

if __name__ == "__main__":
    Calculator().mainloop()
