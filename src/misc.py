from __future__ import annotations
import customtkinter as ctk


class Colors:
    def __init__(self):
        self.transparent = "transparent"
        self.fg_color = ctk.ThemeManager.theme["CTk"]["fg_color"]
        self.frame_fg_color = ctk.ThemeManager.theme["CTkFrame"]["fg_color"]
        self.label_text_color = ctk.ThemeManager.theme["CTkLabel"]["text_color"]
        self.button_fg_color = ctk.ThemeManager.theme["CTkButton"]["fg_color"]
        self.entry_placeholder_text_color = ctk.ThemeManager.theme["CTkEntry"]["placeholder_text_color"]
        self.combobox_text_color = ctk.ThemeManager.theme["CTkComboBox"]["text_color"]
        self.progressbar_progress_color = ctk.ThemeManager.theme["CTkProgressBar"]["progress_color"]
        self.progressbar_fg_color = ctk.ThemeManager.theme["CTkProgressBar"]["fg_color"]
        self.available_appearance_modes = ["system", "light", "dark"]


class Fonts:
    def __init__(self):
        self.underlined = ctk.CTkFont(underline=True)
