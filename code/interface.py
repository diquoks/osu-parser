from __future__ import annotations
import webbrowser, threading, logging, ctypes, time, sys
import customtkinter as ctk
import models, query, data, utils, misc


class Application(ctk.CTk):
    _NAME = "osu!parser"

    def __getstate__(self):
        state = self.__dict__.copy()
        del state["_registry"]
        return state

    def __init__(self):
        self.initialized = False
        self._parsing_thread = None
        self._oauth_thread = None
        self._config = data.ConfigProvider()
        self._registry = data.RegistryProvider()
        self._strings = data.StringsProvider()
        self._assets = data.AssetsProvider()
        self._logger = data.LoggerService(
            name=__name__,
            file_handling=self._config.settings.logging,
            level=logging.DEBUG if self._config.settings.beta else logging.INFO,
        )
        self._oauth = query.OAuthClient(config=self._config)
        ctk.set_appearance_mode("system" if self._registry.window.theme is None else self._registry.window.theme)
        ctk.set_default_color_theme("blue")
        super().__init__()
        # Attributes
        self._colors = misc.Colors()
        self._fonts = misc.Fonts()
        self._id_entry_validation = (self.register(lambda i: not self.initialized or ((i == str() or i.isdigit()) and len(i) < 16)), "%P")
        self.parsing_settings_ruleset_combobox_str = ctk.StringVar(value=self._strings.localisable_text.parsing_settings_ruleset)
        self.parsing_settings_start_button_str = ctk.StringVar(value=self._strings.localisable_text.parsing_settings_start)
        self.settings_options_window_theme_combobox_str = ctk.StringVar()
        self.settings_options_window_topmost_checkbox_bool = ctk.BooleanVar(value=self._registry.window.topmost)
        self.settings_options_parsing_float_values_bool = ctk.BooleanVar(value=self._registry.settings.float_values)
        self.settings_options_parsing_include_fails_bool = ctk.BooleanVar(value=self._registry.settings.include_fails)
        self.settings_options_parsing_lazer_mode_bool = ctk.BooleanVar(value=self._registry.settings.lazer_mode)
        # Window settings
        self.title("osu!parser")
        self.iconbitmap(utils.get_path("assets/icons/application.ico"))
        self.geometry("550x300" if self._registry.window.dimensions is None else f"550x300+{"+".join(self._registry.window.dimensions.split("+")[1:])}" if self._registry.window.state == "zoomed" else self._registry.window.dimensions)
        self.minsize(550, 300)
        self.resizable(width=True, height=True)
        self.protocol("WM_DELETE_WINDOW", lambda: self._save_window_settings(close_window=True))
        self.after_idle(lambda i: self.state(i), "withdrawn" if self._registry.window.state == "normal" or self._registry.window.state is None else self._registry.window.state)
        self.attributes("-topmost", self._registry.window.topmost)
        # Tabview
        self.main_tabview = ctk.CTkTabview(master=self)
        self.main_tabview.pack(expand=True, fill=ctk.BOTH)
        # Parsing Tab
        self.main_parsing_tab = self.main_tabview.add(name=self._strings.localisable_text.main_parsing)
        self.parsing_settings_frame = ctk.CTkFrame(master=self.main_parsing_tab, fg_color=self._colors.fg_color)
        self.parsing_settings_frame.pack(fill=ctk.Y, anchor=ctk.W, side=ctk.LEFT)
        self.parsing_settings_id_entry = ctk.CTkEntry(master=self.parsing_settings_frame, placeholder_text=self._strings.localisable_text.parsing_settings_id, validate="key", validatecommand=self._id_entry_validation)
        self.parsing_settings_id_entry.pack(side=ctk.TOP, padx=10, pady=15)
        self.parsing_settings_ruleset_combobox = ctk.CTkComboBox(master=self.parsing_settings_frame, variable=self.parsing_settings_ruleset_combobox_str, values=models.Rulesets.rulesets.keys(), text_color=self._colors.entry_placeholder_text_color, state="readonly", command=self._parsing_settings_ruleset_combobox_select)
        self.parsing_settings_ruleset_combobox.pack(side=ctk.TOP, padx=10)
        self.parsing_settings_start_button = ctk.CTkButton(master=self.parsing_settings_frame, command=self.parsing_start, textvariable=self.parsing_settings_start_button_str)
        self.parsing_settings_start_button.pack(side=ctk.BOTTOM, padx=10, pady=15)
        self.parsing_settings_progressbar = ctk.CTkProgressBar(master=self.parsing_settings_frame, mode="determinate", width=int(), fg_color=self._colors.fg_color, progress_color=self._colors.fg_color, indeterminate_speed=1.3)
        self.parsing_settings_progressbar.pack(fill=ctk.X, side=ctk.BOTTOM, padx=10)
        self.parsing_score_frame = ctk.CTkFrame(master=self.main_parsing_tab)
        self.parsing_score_frame.pack(expand=True, fill=ctk.BOTH, anchor=ctk.E, side=ctk.RIGHT, padx=(10, 5))
        self.parsing_score_top_frame = ctk.CTkFrame(master=self.parsing_score_frame, fg_color=self._colors.transparent)
        self.parsing_score_top_frame.pack(fill=ctk.X, anchor=ctk.N, side=ctk.TOP, pady=10)
        self.parsing_score_top_score_label = ctk.CTkLabel(master=self.parsing_score_top_frame, text=str(), font=self._fonts.underlined, cursor="hand2", anchor=ctk.W, height=int())
        self.parsing_score_top_score_label.pack(anchor=ctk.NW, side=ctk.LEFT)
        self.parsing_score_top_user_label = ctk.CTkLabel(master=self.parsing_score_top_frame, text=str(), font=self._fonts.underlined, cursor="hand2", anchor=ctk.E, height=int())
        self.parsing_score_top_user_label.pack(anchor=ctk.NE, side=ctk.RIGHT, padx=(10, int()))
        self.parsing_score_beatmap_label = ctk.CTkLabel(master=self.parsing_score_frame, text=str(), font=self._fonts.underlined, cursor="hand2", anchor=ctk.W, height=int())
        self.parsing_score_beatmap_label.pack(anchor=ctk.W, side=ctk.TOP)
        self.parsing_score_difficulty_label = ctk.CTkLabel(master=self.parsing_score_frame, text=str(), anchor=ctk.W, height=int())
        self.parsing_score_difficulty_label.pack(anchor=ctk.W, side=ctk.TOP, pady=10)
        self.parsing_score_pp_label = ctk.CTkLabel(master=self.parsing_score_frame, text=str(), anchor=ctk.W, height=int())
        self.parsing_score_pp_label.pack(anchor=ctk.W, side=ctk.TOP)
        self.parsing_score_mods_label = ctk.CTkLabel(master=self.parsing_score_frame, text=str(), anchor=ctk.W, height=int())
        self.parsing_score_mods_label.pack(anchor=ctk.W, side=ctk.TOP, pady=10)
        self.parsing_score_data_frame = ctk.CTkFrame(master=self.parsing_score_frame, fg_color=self._colors.transparent)
        self.parsing_score_data_frame.pack(fill=ctk.X, anchor=ctk.W, side=ctk.TOP)
        self.parsing_score_data_grade_label = ctk.CTkLabel(master=self.parsing_score_data_frame, text=str(), anchor=ctk.W, height=int())
        self.parsing_score_data_grade_label.pack(anchor=ctk.W, side=ctk.LEFT, padx=(int(), 5))
        self.parsing_score_data_stats_label = ctk.CTkLabel(master=self.parsing_score_data_frame, text=str(), anchor=ctk.W, height=int())
        self.parsing_score_data_stats_label.pack(anchor=ctk.W, side=ctk.LEFT)
        self.parsing_score_hits_label = ctk.CTkLabel(master=self.parsing_score_frame, text=str(), anchor=ctk.W, height=int())
        self.parsing_score_hits_label.pack(anchor=ctk.W, side=ctk.TOP, pady=10)
        self.parsing_score_supp_hits_label = ctk.CTkLabel(master=self.parsing_score_frame, text=str(), anchor=ctk.W, height=int())
        self.parsing_score_supp_hits_label.pack(anchor=ctk.W, side=ctk.TOP)
        self.parsing_score_bottom_frame = ctk.CTkFrame(master=self.parsing_score_frame, fg_color=self._colors.transparent)
        self.parsing_score_bottom_frame.pack(fill=ctk.X, anchor=ctk.S, side=ctk.BOTTOM, pady=5)
        self.parsing_score_bottom_status_label = ctk.CTkLabel(master=self.parsing_score_bottom_frame, text=str())
        self.parsing_score_bottom_status_label.pack(anchor=ctk.W, side=ctk.LEFT)
        self.parsing_score_bottom_recalculate_button = ctk.CTkButton(master=self.parsing_score_bottom_frame, text=self._strings.localisable_text.parsing_score_bottom_recalculate, state=ctk.DISABLED)
        self.parsing_score_bottom_recalculate_button.pack(anchor=ctk.E, side=ctk.RIGHT)
        # Calculator Tab
        self.main_calculator_tab = self.main_tabview.add(name=self._strings.localisable_text.main_calculator)
        self.main_tabview._segmented_button._buttons_dict[self._strings.localisable_text.main_calculator].configure(state=ctk.DISABLED)
        # Settings Tab
        self.main_settings_tab = self.main_tabview.add(name=self._strings.localisable_text.main_settings)
        self.settings_oauth_frame = ctk.CTkFrame(master=self.main_settings_tab, fg_color=self._colors.fg_color)
        self.settings_oauth_frame.pack(fill=ctk.X, anchor=ctk.N, side=ctk.TOP, pady=(int(), 10))
        self.settings_oauth_avatar_label = ctk.CTkLabel(master=self.settings_oauth_frame, text=str())
        self.settings_oauth_avatar_label.pack(side=ctk.LEFT, padx=10, pady=10)
        self.settings_oauth_username_label = ctk.CTkLabel(master=self.settings_oauth_frame, text=self._strings.localisable_text.settings_oauth_username_logged_out)
        self.settings_oauth_username_label.pack(side=ctk.LEFT)
        self.settings_oauth_login_button = ctk.CTkButton(master=self.settings_oauth_frame, text=self._strings.localisable_text.settings_oauth_login, command=self.oauth_login)
        self.settings_oauth_login_button.pack(side=ctk.RIGHT, padx=10, pady=10)
        self.settings_bottom_frame = ctk.CTkFrame(master=self.main_settings_tab, fg_color=self._colors.transparent)
        self.settings_bottom_frame.pack(fill=ctk.X, anchor=ctk.S, side=ctk.BOTTOM, padx=5, pady=(20, 5))
        self.settings_bottom_help_button = ctk.CTkButton(master=self.settings_bottom_frame, text=self._strings.localisable_text.settings_bottom_help, command=lambda: webbrowser.open(self._strings.url.guide), font=self._fonts.underlined)
        self.settings_bottom_help_button.pack(anchor=ctk.W, side=ctk.LEFT)
        self.settings_bottom_creator_label = ctk.CTkLabel(master=self.settings_bottom_frame, text=self._strings.localisable_text.settings_bottom_creator, font=self._fonts.underlined, cursor="hand2", anchor=ctk.W, height=int())
        self.settings_bottom_creator_label.bind(sequence="<ButtonPress-1>", command=lambda i: webbrowser.open(self._strings.url.diquoks_web))
        self.settings_bottom_creator_label.pack(anchor=ctk.E, side=ctk.RIGHT)
        self.settings_bottom_version_label = ctk.CTkLabel(master=self.settings_bottom_frame, text=self._strings.localisable_text.settings_bottom_version_beta.format(self._config.settings.version) if self._config.settings.beta else self._config.settings.version, font=self._fonts.underlined, cursor="hand2", anchor=ctk.E, height=int())
        self.settings_bottom_version_label.bind(sequence="<ButtonPress-1>", command=lambda i: webbrowser.open(self._strings.url.latest_release))
        self.settings_bottom_version_label.pack(expand=True, anchor=ctk.CENTER, side=ctk.LEFT)
        self.settings_options_frame = ctk.CTkFrame(master=self.main_settings_tab, fg_color=self._colors.fg_color)
        self.settings_options_frame.pack(fill=ctk.BOTH, anchor=ctk.N, side=ctk.TOP)
        self.settings_options_window_frame = ctk.CTkFrame(master=self.settings_options_frame, fg_color=self._colors.transparent, background_corner_colors=tuple([self._colors.frame_fg_color, self._colors.fg_color, self._colors.fg_color, self._colors.frame_fg_color]))
        self.settings_options_window_frame.pack(fill=ctk.BOTH, anchor=ctk.N, side=ctk.LEFT)
        self.settings_options_window_title_label = ctk.CTkLabel(master=self.settings_options_window_frame, text=self._strings.localisable_text.settings_options_window_title)
        self.settings_options_window_title_label.pack(anchor=ctk.CENTER, side=ctk.TOP, padx=10, pady=5)
        self.settings_options_window_topmost_checkbox = ctk.CTkCheckBox(master=self.settings_options_window_frame, text=self._strings.localisable_text.settings_options_window_topmost, variable=self.settings_options_window_topmost_checkbox_bool, command=self._settings_options_window_topmost_checkbox_select, hover_color=self._colors.progressbar_fg_color)
        self.settings_options_window_topmost_checkbox.pack(anchor=ctk.NW, side=ctk.TOP, padx=10, pady=5)
        self.settings_options_window_theme_combobox = ctk.CTkComboBox(master=self.settings_options_window_frame, variable=self.settings_options_window_theme_combobox_str, values=self._strings.localisable_text.settings_options_window_themes_list, state="readonly", command=self._settings_options_window_theme_combobox_select)
        self.settings_options_window_theme_combobox.pack(fill=ctk.X, anchor=ctk.NW, side=ctk.TOP, padx=10, pady=10)
        self.settings_options_parsing_frame = ctk.CTkFrame(master=self.settings_options_frame, fg_color=self._colors.transparent, background_corner_colors=tuple([self._colors.fg_color, self._colors.frame_fg_color, self._colors.frame_fg_color, self._colors.fg_color]))
        self.settings_options_parsing_frame.pack(fill=ctk.BOTH, anchor=ctk.N, side=ctk.RIGHT, ipadx=5)
        self.settings_options_parsing_title_label = ctk.CTkLabel(master=self.settings_options_parsing_frame, text=self._strings.localisable_text.settings_options_parsing_title)
        self.settings_options_parsing_title_label.pack(anchor=ctk.CENTER, side=ctk.TOP, padx=10, pady=5)
        self.settings_options_parsing_left_frame = ctk.CTkFrame(master=self.settings_options_parsing_frame, fg_color=self._colors.transparent)
        self.settings_options_parsing_left_frame.pack(anchor=ctk.N, side=ctk.LEFT)
        self.settings_options_parsing_left_float_values_checkbox = ctk.CTkCheckBox(master=self.settings_options_parsing_left_frame, text=self._strings.localisable_text.settings_options_parsing_float_values, variable=self.settings_options_parsing_float_values_bool, command=self._settings_options_parsing_float_values_checkbox_select, hover_color=self._colors.progressbar_fg_color)
        self.settings_options_parsing_left_float_values_checkbox.pack(anchor=ctk.NW, side=ctk.TOP, padx=10, pady=5)
        self.settings_options_parsing_left_include_fails_checkbox = ctk.CTkCheckBox(master=self.settings_options_parsing_left_frame, text=self._strings.localisable_text.settings_options_parsing_include_fails, variable=self.settings_options_parsing_include_fails_bool, command=self._settings_options_parsing_include_fails_checkbox_select, hover_color=self._colors.progressbar_fg_color)
        self.settings_options_parsing_left_include_fails_checkbox.pack(anchor=ctk.NW, side=ctk.TOP, padx=10, pady=10)
        self.settings_options_parsing_right_frame = ctk.CTkFrame(master=self.settings_options_parsing_frame, fg_color=self._colors.transparent)
        self.settings_options_parsing_right_frame.pack(anchor=ctk.N, side=ctk.RIGHT)
        self.settings_options_parsing_right_lazer_mode_checkbox = ctk.CTkCheckBox(master=self.settings_options_parsing_right_frame, text=self._strings.localisable_text.settings_options_parsing_lazer_mode, variable=self.settings_options_parsing_lazer_mode_bool, command=self._settings_options_parsing_lazer_mode_checkbox_select, hover_color=self._colors.progressbar_fg_color)
        self.settings_options_parsing_right_lazer_mode_checkbox.pack(anchor=ctk.NW, side=ctk.TOP, padx=10, pady=5)
        # Values assignment
        self._oauth_thread = threading.Thread(target=self.oauth_thread, daemon=True, name="oauthThread")
        self._check_for_updates_thread = threading.Thread(target=self.check_for_updates_thread, daemon=True, name="checkForUpdatesThread")
        self._oauth_thread.start()
        self._check_for_updates_thread.start()
        if self._registry.previous.user:
            self.parsing_settings_id_entry.insert(int(), self._registry.previous.user)
        if self._registry.previous.ruleset:
            try:
                self.parsing_settings_ruleset_combobox_str.set(value=models.Rulesets.names[self._registry.previous.ruleset])
                self.parsing_settings_ruleset_combobox.configure(text_color=self._colors.combobox_text_color)
            except Exception as e:
                self._logger.info(self._strings.log.error_combobox_value, exc_info=e)
        try:
            self.settings_options_window_theme_combobox_str.set(value=self._strings.localisable_text.settings_options_window_themes_list[self._colors.available_appearance_modes.index(ctk.get_appearance_mode().lower())])
        except Exception as e:
            self._logger.info(self._strings.log.error_combobox_value, exc_info=e)
        self._logger.info(self._strings.separator.space.join((
            self._NAME,
            self._config.settings.version,
            self._strings.log.initialized,
        )))
        self.initialized = True

    def _autoresize_window(self) -> None:
        width = self.winfo_width() if self.winfo_width() > self.winfo_reqwidth() else self.winfo_reqwidth()
        height = self.winfo_height() if self.winfo_height() > self.winfo_reqheight() else self.winfo_reqheight()
        self._logger.debug(self._strings.debug.function_data.format(sys._getframe().f_code.co_name, self._strings.separator.arrow.join((
            self.geometry(),
            f"{width}x{height}+{"+".join(self.geometry().split("+")[1:])}",
        ))))
        self.geometry(f"{width}x{height}+{"+".join(self.geometry().split("+")[1:])}")

    def _save_window_settings(self, close_window: bool = False) -> None:
        self._registry.window.update(dimensions=self.geometry(), state=self.state(), theme=ctk.get_appearance_mode(), topmost=self.attributes("-topmost"))
        self.destroy() if close_window else None
        self._logger.debug(self._strings.debug.function_data.format(sys._getframe().f_code.co_name, self._strings.separator.column.join((
            self._strings.log.debug_close_window.format(close_window),
            str(self._registry.window.values),
        ))))

    def _round_float_values(self, number: float, adaptive: bool = True, ndigits: int = 2) -> str:
        return format(round(number, ndigits if self._registry.settings.float_values or not adaptive else None), f".{ndigits}f" if self._registry.settings.float_values or not adaptive else str())

    def _parsing_settings_ruleset_combobox_select(self, value: str) -> None:
        self.parsing_settings_ruleset_combobox.configure(text_color=self._colors.combobox_text_color)
        self._logger.debug(self._strings.debug.function_data.format(sys._getframe().f_code.co_name, models.Rulesets.rulesets[value]))

    def _parsing_settings_progressbar_set(self, value: float = float()) -> None:
        ratio = 0.02
        if value == float():
            self.parsing_settings_progressbar.configure(progress_color=self._colors.progressbar_fg_color, fg_color=self._colors.progressbar_fg_color)
            time.sleep(ratio * 10)
        else:
            self.parsing_settings_progressbar.configure(progress_color=self._colors.progressbar_progress_color, fg_color=self._colors.progressbar_fg_color)
            current_value = self.parsing_settings_progressbar.get()
            while current_value + ratio * 2 <= value:
                current_value = self.parsing_settings_progressbar.get()
                self.parsing_settings_progressbar.set(value=current_value + ratio)
                time.sleep(ratio / 2)
        self.parsing_settings_progressbar.set(value=value)
        self._logger.debug(self._strings.debug.function_data.format(sys._getframe().f_code.co_name, value))

    def _settings_options_window_theme_combobox_select(self, value: str) -> None:
        ctk.set_appearance_mode(self._colors.available_appearance_modes[self._strings.localisable_text.settings_options_window_themes_list.index(value)])
        self._save_window_settings()
        self._logger.debug(self._strings.debug.function_data.format(sys._getframe().f_code.co_name, self._colors.available_appearance_modes[self._strings.localisable_text.settings_options_window_themes_list.index(value)]))

    def _settings_options_window_topmost_checkbox_select(self) -> None:
        self._logger.debug(self._strings.debug.function_data.format(sys._getframe().f_code.co_name, self._strings.separator.arrow.join((
            str(bool(self.attributes("-topmost"))),
            str(not self.attributes("-topmost")),
        ))))
        self.settings_options_window_topmost_checkbox_bool.set(not self.attributes("-topmost"))
        self.attributes("-topmost", not self.attributes("-topmost"))
        self._save_window_settings()

    def _settings_options_parsing_float_values_checkbox_select(self) -> None:
        self._logger.debug(self._strings.debug.function_data.format(sys._getframe().f_code.co_name, self._strings.separator.arrow.join((
            str(bool(self._registry.settings.float_values)),
            str(not self._registry.settings.float_values),
        ))))
        self.settings_options_parsing_float_values_bool.set(not self._registry.settings.float_values)
        self._registry.settings.update(float_values=not self._registry.settings.float_values)

    def _settings_options_parsing_include_fails_checkbox_select(self) -> None:
        self._logger.debug(self._strings.debug.function_data.format(sys._getframe().f_code.co_name, self._strings.separator.arrow.join((
            str(bool(self._registry.settings.include_fails)),
            str(not self._registry.settings.include_fails),
        ))))
        self.settings_options_parsing_include_fails_bool.set(not self._registry.settings.include_fails)
        self._registry.settings.update(include_fails=not self._registry.settings.include_fails)

    def _settings_options_parsing_lazer_mode_checkbox_select(self) -> None:
        self._logger.debug(self._strings.debug.function_data.format(sys._getframe().f_code.co_name, self._strings.separator.arrow.join((
            str(bool(self._registry.settings.lazer_mode)),
            str(not self._registry.settings.lazer_mode),
        ))))
        self.settings_options_parsing_lazer_mode_bool.set(not self._registry.settings.lazer_mode)
        self._registry.settings.update(lazer_mode=not self._registry.settings.lazer_mode)

    def parsing_thread(self, parsing_user: int, parsing_ruleset: str) -> None:
        try:
            self.parsing_score_bottom_status_label.configure(text=self._strings.localisable_text.parsing_score_bottom_status_player)
            try:
                user = self._oauth.get_user(user=parsing_user, ruleset=parsing_ruleset)
                self.parsing_score_top_user_label.configure(text=self._strings.localisable_text.parsing_score_top_user.format(user.username, user.statistics.global_rank) if user.statistics.global_rank else user.username)
                self.parsing_score_top_user_label.bind(sequence="<ButtonPress-1>", command=lambda i: webbrowser.open(self._strings.url.user_ruleset.format(parsing_user, parsing_ruleset)))
            except:
                self.parsing_score_top_user_label.configure(text=str())
                self.parsing_score_top_user_label.unbind(sequence="<ButtonPress-1>")
                self.parsing_score_bottom_status_label.configure(text=str())
                raise SystemExit
            else:
                parsing_values = misc.ParsingValues(pp_total=user.statistics.pp, pp_diff=float(), score_id=None, settings=self._registry.settings.refresh())
                while True:
                    self.parsing_score_bottom_status_label.configure(text=self._strings.localisable_text.parsing_score_bottom_status_score)
                    self._parsing_settings_progressbar_set(value=0.2)
                    score = self._oauth.get_latest_score(user=parsing_user, ruleset=parsing_ruleset, include_fails=bool(self._registry.settings.include_fails), legacy_only=not bool(self._registry.settings.lazer_mode))
                    if score and (parsing_values.score_id != score.id or parsing_values.settings.values != self._registry.settings.refresh().values):
                        self._parsing_settings_progressbar_set(value=0.4)
                        best_scores = self._oauth.get_best_scores(user=parsing_user, ruleset=parsing_ruleset, legacy_only=not bool(self._registry.settings.lazer_mode))
                        score_weight = utils.get_score_weight(score=score, best_scores=best_scores)
                        if score_weight:
                            score = score_weight.score
                        self.parsing_score_bottom_status_label.configure(text=self._strings.localisable_text.parsing_score_bottom_status_profile)
                        self._parsing_settings_progressbar_set(value=0.6)
                        user = self._oauth.get_user(user=parsing_user, ruleset=parsing_ruleset)
                        self.parsing_score_bottom_status_label.configure(text=self._strings.localisable_text.parsing_score_bottom_status_beatmap)
                        self._parsing_settings_progressbar_set(value=0.8)
                        beatmap = score.beatmap
                        beatmapset = score.beatmapset
                        beatmap_raw = self._oauth.get_raw_beatmap(beatmap=beatmap.id)
                        recalculation = utils.calculate(score=score, beatmap_raw=beatmap_raw, lazer_mode=bool(self._registry.settings.lazer_mode))
                        self._parsing_settings_progressbar_set(value=1.0)
                        parsing_score_hits_values = [
                            [score.statistics.great, score.maximum_statistics.great, score.statistics.ok, score.statistics.meh, score.statistics.miss],
                            [score.statistics.great, score.maximum_statistics.great, score.statistics.ok, score.statistics.miss],
                            [score.statistics.great, score.maximum_statistics.great, score.statistics.large_tick_hit, score.maximum_statistics.large_tick_hit, score.statistics.small_tick_hit, score.maximum_statistics.small_tick_hit],
                            [score.statistics.perfect, score.maximum_statistics.perfect, score.statistics.great, score.statistics.good],
                        ]
                        parsing_score_supp_hits_values = [
                            list(),
                            list(),
                            [score.statistics.large_bonus, score.maximum_statistics.large_bonus, score.statistics.miss],
                            [score.statistics.ok, score.statistics.meh, score.statistics.miss],
                        ]
                        ruleset_index = models.Rulesets.index.index(parsing_ruleset)
                        parsing_values.update(pp_total=user.statistics.pp, pp_diff=user.statistics.pp - parsing_values.pp_total, score_id=score.id, settings=self._registry.settings.refresh())
                        self.parsing_score_top_score_label.configure(text=self._strings.url.score.format(score.id) if user.statistics.global_rank else user.username)
                        self.parsing_score_top_score_label.unbind(sequence="<ButtonPress-1>")
                        self.parsing_score_top_score_label.bind(sequence="<ButtonPress-1>", command=lambda i: webbrowser.open(self._strings.url.score.format(score.id)))
                        self.parsing_score_top_user_label.configure(text=self._strings.localisable_text.parsing_score_top_user.format(user.username, user.statistics.global_rank) if user.statistics.global_rank else user.username)
                        self.parsing_score_top_user_label.unbind(sequence="<ButtonPress-1>")
                        self.parsing_score_top_user_label.bind(sequence="<ButtonPress-1>", command=lambda i: webbrowser.open(self._strings.url.user_ruleset.format(parsing_user, parsing_ruleset)))
                        self.parsing_score_beatmap_label.configure(text=self._strings.localisable_text.parsing_score_beatmap.format(beatmapset.artist, beatmapset.title, beatmapset.creator))
                        self.parsing_score_beatmap_label.unbind(sequence="<ButtonPress-1>")
                        self.parsing_score_beatmap_label.bind(sequence="<ButtonPress-1>", command=lambda i: webbrowser.open(self._strings.url.beatmap_ruleset.format(beatmap.id, parsing_ruleset)))
                        self.parsing_score_difficulty_label.configure(
                            text=self._strings.separator.column.join(
                                (i for i in (
                                    self._strings.localisable_text.parsing_score_difficulty.format(beatmap.version, beatmap.status.capitalize(), self._round_float_values(recalculation.difficulty.stars, adaptive=False)),
                                    self._strings.separator.comma.join(
                                        (i for i in (
                                            self._strings.localisable_text.parsing_score_pp_fc.format(self._round_float_values(recalculation.performance_fc.pp)) if not score.is_perfect_combo else None,
                                            self._strings.localisable_text.parsing_score_pp_ss.format(self._round_float_values(recalculation.performance_ss.pp))
                                        ) if i)
                                    ) if "x" not in score.rank.lower() else None,
                                ) if i)
                            )
                        )
                        self.parsing_score_pp_label.configure(
                            text=self._strings.separator.comma.join(
                                (i for i in (
                                    self._strings.separator.space.join(i for i in (
                                        self._strings.localisable_text.parsing_score_pp_total.format(self._round_float_values(user.statistics.pp)),
                                        self._strings.localisable_text.parsing_score_pp_diff.format(self._round_float_values(parsing_values.pp_diff)) if parsing_values.pp_diff != float() else None
                                    ) if i),
                                    self._strings.separator.dash.join(i for i in (
                                        self._strings.localisable_text.parsing_score_pp_score.format(self._round_float_values(score.pp)),
                                        self._strings.localisable_text.parsing_score_pp_rank.format(score.rank_global) if score.rank_global else None,
                                    ) if i) if score.pp else None,
                                    self._strings.localisable_text.parsing_score_pp_weight.format(self._round_float_values(score.weight.percentage), score_weight.place, self._round_float_values(score.weight.pp)) if score.weight else None,
                                ) if i)
                            )
                        )
                        self.parsing_score_mods_label.configure(text=self._strings.localisable_text.parsing_score_mods.format(self._strings.separator.comma.join(score.mods.mods_string)) if score.mods.mods else str())
                        self.parsing_score_data_grade_label.configure(image=ctk.CTkImage(dark_image=getattr(self._assets.grades, score.rank.lower()) if score.passed else self._assets.grades.f, size=(32, 16)))
                        self.parsing_score_data_stats_label.configure(text=self._strings.localisable_text.parsing_score_data_stats.format(self._round_float_values(score.accuracy * 100, adaptive=False), score.max_combo))
                        self.parsing_score_hits_label.configure(text=self._strings.localisable_text.parsing_score_hits_list[ruleset_index].format(*parsing_score_hits_values[ruleset_index]).replace(str(None), str(int())))
                        self.parsing_score_supp_hits_label.configure(text=self._strings.localisable_text.parsing_score_supp_hits_list[ruleset_index].format(*parsing_score_supp_hits_values[ruleset_index]).replace(str(None), str(int())))
                        # self.parsing_score_bottom_recalculate_button.configure(state=ctk.NORMAL)
                    else:
                        self._parsing_settings_progressbar_set(value=1.0)
                    self._autoresize_window()
                    self._registry.refresh()
                    self.parsing_score_bottom_status_label.configure(text=self._strings.localisable_text.parsing_score_bottom_status_wait)
                    for i in range(6):
                        self._parsing_settings_progressbar_set(value=0.2 * i)
                        time.sleep(1)
                    self._parsing_settings_progressbar_set()
        finally:
            self.parsing_score_top_score_label.configure(text=str())
            self.parsing_score_top_score_label.unbind(sequence="<ButtonPress-1>")
            self.parsing_score_top_user_label.configure(text=str())
            self.parsing_score_top_user_label.unbind(sequence="<ButtonPress-1>")
            self.parsing_score_beatmap_label.configure(text=str())
            self.parsing_score_difficulty_label.configure(text=str())
            self.parsing_score_pp_label.configure(text=str())
            self.parsing_score_mods_label.configure(text=str())
            self.parsing_score_data_grade_label.configure(image=None)
            self.parsing_score_data_stats_label.configure(text=str())
            self.parsing_score_bottom_status_label.configure(text=str())
            self.parsing_score_supp_hits_label.configure(text=str())
            self.parsing_score_hits_label.configure(text=str())
            self.parsing_score_bottom_recalculate_button.configure(state=ctk.DISABLED)
            self._autoresize_window()
            self.parsing_settings_start_button.configure(command=self.parsing_start)
            self.parsing_settings_start_button_str.set(value=self._strings.localisable_text.parsing_settings_start)
            self.parsing_settings_progressbar.configure(progress_color=self._colors.fg_color, fg_color=self._colors.fg_color)
            self.parsing_settings_progressbar.stop()
            self.parsing_settings_start_button.configure(state=ctk.NORMAL)
            self.bell()

    def parsing_start(self) -> None:
        if not self.parsing_settings_id_entry.get().isdigit() or self.parsing_settings_ruleset_combobox.get() is None or self.parsing_settings_ruleset_combobox.get() == self._strings.localisable_text.parsing_settings_ruleset:
            self.bell()
        else:
            self._registry.previous.update(user=int(self.parsing_settings_id_entry.get()), ruleset=models.Rulesets.rulesets[self.parsing_settings_ruleset_combobox.get()])
            self.parsing_settings_progressbar.configure(mode="determinate")
            self._parsing_settings_progressbar_set()
            self._parsing_thread = threading.Thread(target=self.parsing_thread, args=[int(self.parsing_settings_id_entry.get()), models.Rulesets.rulesets[self.parsing_settings_ruleset_combobox.get()]], daemon=True, name="parsingThread")
            self._parsing_thread.start()
            self.parsing_settings_start_button.configure(command=lambda: threading.Thread(target=self.parsing_stop, daemon=True, name="localhostThread").start())
            self.parsing_settings_start_button_str.set(value=self._strings.localisable_text.parsing_settings_stop)

    def parsing_stop(self) -> None:
        self.parsing_settings_progressbar.configure(mode="indeterminate", progress_color=self._colors.progressbar_progress_color)
        self.parsing_settings_progressbar.start()
        self.parsing_settings_start_button.configure(state=ctk.DISABLED)
        ctypes.pythonapi.PyThreadState_SetAsyncExc(self._parsing_thread.ident, ctypes.py_object(SystemExit))
        self._parsing_thread.join()

    def oauth_thread(self, login: bool = False) -> None:
        self.parsing_settings_start_button.configure(state=ctk.DISABLED)
        try:
            self.settings_oauth_avatar_label.configure(image=ctk.CTkImage(dark_image=self._assets.round_corners(image=self._assets.images.avatar_guest, radius=24), size=(32, 32)))
            self.settings_oauth_username_label.configure(text=self._strings.localisable_text.settings_oauth_username_logging_in)
            self.settings_oauth_login_button.configure(state=ctk.DISABLED, text=self._strings.localisable_text.settings_oauth_login, command=self.oauth_login)
            if not login:
                self._oauth.refresh_access_token(refresh_token=self._registry.oauth.refresh_token)
            user_data = self._oauth.get_own_data()
            self.settings_oauth_avatar_label.configure(image=ctk.CTkImage(dark_image=self._assets.round_corners(image=self._assets.network_image(url=user_data.avatar_url).resize(self._assets.images.avatar_guest.size), radius=24), size=(32, 32)))
            self.settings_oauth_username_label.configure(text=self._strings.localisable_text.settings_oauth_username_logged_in.format(user_data.username))
            self.settings_oauth_login_button.configure(state=ctk.NORMAL, text=self._strings.localisable_text.settings_oauth_logout, command=self.oauth_logout)
            self.parsing_settings_start_button.configure(state=ctk.NORMAL)
        except Exception as e:
            self._logger.info(self._strings.log.error_refresh_token, exc_info=e)
            self.settings_oauth_avatar_label.configure(image=ctk.CTkImage(dark_image=self._assets.round_corners(image=self._assets.images.avatar_guest, radius=24), size=(32, 32)))
            self.settings_oauth_username_label.configure(text=self._strings.localisable_text.settings_oauth_username_logged_out)
            self.settings_oauth_login_button.configure(state=ctk.NORMAL)
        finally:
            if login:
                self.bell()

    def oauth_login(self) -> None:
        webbrowser.open(url=self._oauth.get_auth_url())

    def oauth_logout(self) -> None:
        self.parsing_settings_start_button.configure(state=ctk.DISABLED)
        try:
            self._oauth.revoke_current_token()
        except Exception as e:
            self._logger.info(self._strings.log.error_revoke_token, exc_info=e)
        finally:
            self.settings_oauth_avatar_label.configure(image=ctk.CTkImage(dark_image=self._assets.round_corners(image=self._assets.images.avatar_guest, radius=24), size=(32, 32)))
            self.settings_oauth_username_label.configure(text=self._strings.localisable_text.settings_oauth_username_logged_out)
            self.settings_oauth_login_button.configure(state=ctk.NORMAL, text=self._strings.localisable_text.settings_oauth_login, command=self.oauth_login)

    def check_for_updates_thread(self) -> None:
        if query.check_for_updates(version=self._config.settings.version, beta=self._config.settings.beta):
            self.settings_bottom_version_label.configure(text=self._strings.localisable_text.settings_bottom_version_update.format(self._config.settings.version))
