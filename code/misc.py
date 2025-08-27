from __future__ import annotations
import customtkinter as ctk, requests, PIL.Image, PIL.ImageDraw, io
import data, utils


class ParsingValues:
    """
    :var pp_total: ``float``
    :var pp_diff: ``float``
    :var score_id: ``int`` | ``None``
    :var settings: ``IRegistry``
    """

    pp_total: float
    pp_diff: float
    score_id: int | None
    settings: data.RegistryProvider.IRegistry

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    def update(self, **kwargs):
        self.__init__(**kwargs)


class Strings:
    class Debug:
        function_data = "{0}:{1}"
        test_data = "\n{0}:\nData: {1}\nExpected: {2}"
        attribute_data = "{0}: {1}"

    class LocalisableText:
        main_parsing = "Парсинг"
        main_calculator = "Калькулятор"
        main_settings = "Настройки"
        parsing_settings_id = "ID игрока"
        parsing_settings_ruleset = "Режим игры"
        parsing_settings_start = "Запустить"
        parsing_settings_stop = "Остановить"
        parsing_score_top_user = "{0} (#{1})"
        parsing_score_beatmap = "{0} - {1} от {2}"
        parsing_score_difficulty = "{0}, {1}, {2}*"
        parsing_score_pp_fc = "FC: {0}pp"
        parsing_score_pp_ss = "SS: {0}pp"
        parsing_score_pp_total = "Всего: {0}pp"
        parsing_score_pp_diff = "(+{0}pp)"
        parsing_score_pp_score = "Рекорд: {0}pp"
        parsing_score_pp_rank = "#{0}"
        parsing_score_pp_weight = "Вес: {0}% - #{1} ({2}pp)"
        parsing_score_mods = "Моды: {0}"
        parsing_score_data_stats = "Точность: {0}%, Комбо: {1}x"
        parsing_score_hits_list = [
            "300: {0}/{1}, 100: {2}, 50: {3}, Miss: {4}",
            "300: {0}/{1}, 100: {2}, Miss: {3}",
            "Fruits: {0}/{1}, Ticks: {2}/{3}, Droplets: {4}/{5}",
            "Max: {0}/{1}, 300: {2}, 200: {3}",
        ]
        parsing_score_supp_hits_list = [
            str(),
            str(),
            "Banana: {0}/{1}, Miss: {2}",
            "100: {0}, 50: {1}, Miss: {2}",
        ]
        parsing_score_bottom_status_wait = "Ожидание..."
        parsing_score_bottom_status_player = "Поиск игрока..."
        parsing_score_bottom_status_score = "Получение рекорда..."
        parsing_score_bottom_status_profile = "Получение профиля..."
        parsing_score_bottom_status_beatmap = "Получение карты..."
        parsing_score_bottom_recalculate = "Перерасчёт pp"
        settings_oauth_username_logging_in = "Производится вход..."
        settings_oauth_username_logged_out = "Вход не выполнен!"
        settings_oauth_username_logged_in = "Привет, {0}!"
        settings_oauth_login = "Войти"
        settings_oauth_logout = "Выйти"
        settings_options_window_title = "Настройки окна"
        settings_options_window_themes_list = [
            "Системная тема",
            "Светлая тема",
            "Тёмная тема",
        ]
        settings_options_window_topmost = "Поверх других окон"
        settings_options_parsing_title = "Настройки парсинга"
        settings_options_parsing_float_values = "Дробные значения"
        settings_options_parsing_include_fails = "Учитывать фейлы"
        settings_options_parsing_lazer_mode = "Lazer-рекорды"
        settings_bottom_help = "Помощь"
        settings_bottom_creator = "Сделано diquoks ❤"
        settings_bottom_version_beta = "{0} (β)"
        settings_bottom_version_update = "{0} (Доступно обновление!)"

    class Log:
        test_localhost_deploy = "Deploying localhost...\nlocalhost_thread.daemon = {0}"
        error_localhost_deploy = "Failed to refresh access token\nlocalhost_thread.daemon = {0}"
        error_refresh_token = "Failed to refresh access token"
        error_combobox_value = "Failed to insert combobox value"
        test_revoke_token = "Current token revoking skipped\nSKIP_REVOKE = {0}"
        error_revoke_token = "Failed to revoke current token"

    class Separator:
        comma = ", "
        space = " "
        newline = "\n"
        arrow = " -> "
        column = " | "
        dash = " - "

    class Url:
        score = "https://osu.ppy.sh/scores/{0}"
        user_ruleset = "https://osu.ppy.sh/users/{0}/{1}"
        beatmap_ruleset = "https://osu.ppy.sh/beatmaps/{0}?mode={1}"
        latest_release = "https://github.com/diquoks/osu-parser/releases/latest"
        guide = "https://github.com/diquoks/osu-parser/blob/master/GUIDE.md"
        diquoks_web = "https://diquoks.ru"

    def __init__(self):
        self.debug = self.Debug()
        self.log = self.Log()
        self.localisable_text = self.LocalisableText()
        self.separator = self.Separator()
        self.url = self.Url()


class Assets:
    class IDirectory:
        _PATH: str = None
        _NAMES: set[str] = None

        def __init__(self, parent: Assets):
            for i in self._NAMES:
                setattr(self, i, parent.file_image(path=self._PATH.format(i)))

    class Grades(IDirectory):
        _PATH = utils.get_path("assets/grades/{0}.png")
        _NAMES = {
            "a",
            "b",
            "c",
            "d",
            "f",
            "s",
            "sh",
            "x",
            "xh",
        }
        a: PIL.Image.Image
        b: PIL.Image.Image
        c: PIL.Image.Image
        d: PIL.Image.Image
        f: PIL.Image.Image
        s: PIL.Image.Image
        sh: PIL.Image.Image
        x: PIL.Image.Image
        xh: PIL.Image.Image

    class Images(IDirectory):
        _PATH = utils.get_path("assets/images/{0}.png")
        _NAMES = {
            "avatar_guest",
        }
        avatar_guest: PIL.Image.Image

    def __init__(self):
        self.grades = self.Grades(parent=self)
        self.images = self.Images(parent=self)

    @staticmethod
    def file_image(path: str) -> PIL.Image.Image:
        return PIL.Image.open(fp=io.BytesIO(initial_bytes=open(path, "rb").read()))

    @staticmethod
    def network_image(url: str) -> PIL.Image.Image:
        return PIL.Image.open(fp=io.BytesIO(initial_bytes=requests.get(url=url).content))

    @staticmethod
    def round_corners(image: PIL.Image.Image, radius: int) -> PIL.Image.Image:
        if image.mode != 'RGB':
            image = image.convert('RGB')
        width, height = image.size
        shape = PIL.Image.new('L', (radius * 2, radius * 2), 0)
        alpha = PIL.Image.new('L', image.size, "white")
        PIL.ImageDraw.Draw(shape).ellipse((0, 0, radius * 2, radius * 2), fill=255)
        alpha.paste(shape.crop((0, 0, radius, radius)), (0, 0))
        alpha.paste(shape.crop((0, radius, radius, radius * 2)), (0, height - radius))
        alpha.paste(shape.crop((radius, 0, radius * 2, radius)), (width - radius, 0))
        alpha.paste(shape.crop((radius, radius, radius * 2, radius * 2)), (width - radius, height - radius))
        image.putalpha(alpha)
        return image


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
