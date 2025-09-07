from __future__ import annotations
import configparser, datetime, logging, winreg, json, sys, io, os
import requests, PIL.Image, PIL.ImageDraw
import utils


class ConfigProvider:
    """
    :var oauth: ``OAuthConfig``
    :var settings: ``SettingsConfig``
    """

    class IConfig:
        _SECTION: str = None
        _CONFIG_VALUES: dict = None

        def __init__(self, parent: ConfigProvider = None) -> None:
            if isinstance(parent, ConfigProvider):
                self._CONFIG_VALUES = parent._CONFIG_VALUES[self._SECTION]
                self._incorrect_content_exception = configparser.ParsingError("config.ini is filled incorrectly!")
                self._config = configparser.ConfigParser()
                self._config.read(utils.get_path("config.ini"))
                if not self._config.has_section(self._SECTION):
                    self._config.add_section(self._SECTION)
                for k, v in self._CONFIG_VALUES.items():
                    try:
                        setattr(self, k, self._config.get(self._SECTION, k))
                    except:
                        self._config.set(self._SECTION, k, v.__name__)
                        with open(utils.get_path("config.ini"), "w") as file:
                            self._config.write(fp=file)
                for k, v in self._CONFIG_VALUES.items():
                    try:
                        if v == int:
                            setattr(self, k, int(getattr(self, k)))
                        elif v == bool:
                            if getattr(self, k) not in [str(True), str(False)]:
                                setattr(self, k, None)
                                raise self._incorrect_content_exception
                            else:
                                setattr(self, k, getattr(self, k) == str(True))
                        elif v in [dict, list]:
                            setattr(self, k, json.loads(getattr(self, k)))
                    except:
                        setattr(self, k, None)
                        raise self._incorrect_content_exception
                if not self.values:
                    raise self._incorrect_content_exception

        @property
        def values(self) -> dict | None:
            try:
                return {i: getattr(self, i) for i in self._CONFIG_VALUES}
            except:
                return None

    class OAuthConfig(IConfig):
        """
        :var client_id: ``int``
        :var client_secret: ``str``
        :var redirect_uri: ``str``
        :var scopes: ``str``
        :var server: ``str``
        """

        _SECTION = "OAuth"
        client_id: int | str | None
        client_secret: str | None
        redirect_uri: str | None
        scopes: str | None
        server: str | None

    class SettingsConfig(IConfig):
        """
        :var beta: ``bool``
        :var logging: ``bool``
        :var version: ``str``
        """

        _SECTION = "Settings"
        beta: bool | str | None
        logging: bool | str | None
        version: str | None

    _CONFIG_VALUES = {
        "OAuth":
            {
                "client_id": int,
                "client_secret": str,
                "redirect_uri": str,
                "scopes": str,
                "server": str,
            },
        "Settings":
            {
                "beta": bool,
                "logging": bool,
                "version": str,
            },
    }
    oauth: OAuthConfig
    settings: SettingsConfig

    def __init__(self) -> None:
        self.oauth = self.OAuthConfig(self)
        self.settings = self.SettingsConfig(self)
        super().__init__()


class RegistryProvider:
    """
    :var oauth: ``OAuthRegistry``
    :var previous: ``PreviousRegistry``
    :var settings: ``SettingsRegistry``
    :var window: ``WindowRegistry``
    """

    class IRegistry:
        _NAME: str = None
        _REGISTRY_VALUES: dict = None

        def __init__(self, parent: RegistryProvider = None) -> None:
            if isinstance(parent, RegistryProvider):
                self._REGISTRY_VALUES = parent._REGISTRY_VALUES[self._NAME]
                self._path = winreg.CreateKey(parent._path, self._NAME)
                for i in self._REGISTRY_VALUES.keys():
                    try:
                        setattr(self, i, winreg.QueryValueEx(self._path, i)[int()])
                    except:
                        setattr(self, i, None)
            super().__init__()

        def refresh(self) -> data.RegistryProvider.IRegistry:
            self.__init__()
            return self

        def update(self, **kwargs) -> None:
            for k, v in kwargs.items():
                winreg.SetValueEx(self._path, k, None, self._REGISTRY_VALUES[k], v)
                setattr(self, k, v)

        @property
        def values(self) -> dict | None:
            try:
                return {i: getattr(self, i) for i in self._REGISTRY_VALUES}
            except:
                return None

    class OAuthRegistry(IRegistry):
        """
        :var access_token: ``str``
        :var expires_in: ``int``
        :var refresh_token: ``str``
        :var token_type: ``str``
        """

        _NAME = "OAuth"
        _REGISTRY_VALUES: dict
        _path: winreg.HKEYType
        access_token: str | None
        expires_in: int | None
        refresh_token: str | None
        token_type: str | None

    class PreviousRegistry(IRegistry):
        """
        :var ruleset: ``str``
        :var score: ``str``
        :var user: ``int``
        """

        _NAME = "Previous"
        _REGISTRY_VALUES: dict
        _path: winreg.HKEYType
        ruleset: str | None
        score: str | None
        user: int | None

    class SettingsRegistry(IRegistry):
        """
        :var float_values: ``bool``
        :var include_fails: ``bool``
        :var lazer_mode: ``bool``
        """

        _NAME = "Settings"
        _REGISTRY_VALUES: dict
        _path: winreg.HKEYType
        float_values: bool | None
        include_fails: bool | None
        lazer_mode: bool | None

    class WindowRegistry(IRegistry):
        """
        :var dimensions: ``str``
        :var state: ``str``
        :var theme: ``str``
        :var topmost: ``bool``
        """

        _NAME = "Window"
        _REGISTRY_VALUES: dict
        _path: winreg.HKEYType
        dimensions: str | None
        state: str | None
        theme: str | None
        topmost: bool | None

    _REGISTRY_VALUES = {
        "OAuth": {
            "access_token": winreg.REG_SZ,
            "expires_in": winreg.REG_DWORD,
            "refresh_token": winreg.REG_SZ,
            "token_type": winreg.REG_SZ,
        },
        "Previous": {
            "ruleset": winreg.REG_SZ,
            "score": winreg.REG_SZ,
            "user": winreg.REG_DWORD,
        },
        "Settings": {
            "float_values": winreg.REG_DWORD,
            "include_fails": winreg.REG_DWORD,
            "lazer_mode": winreg.REG_DWORD,
        },
        "Window": {
            "dimensions": winreg.REG_SZ,
            "state": winreg.REG_SZ,
            "theme": winreg.REG_SZ,
            "topmost": winreg.REG_DWORD,
        },
    }
    _path: winreg.HKEYType
    oauth: OAuthRegistry
    previous: PreviousRegistry
    settings: SettingsRegistry
    window: WindowRegistry

    def __init__(self) -> None:
        self._path = winreg.CreateKey(winreg.HKEY_CURRENT_USER, "Software\\diquoks Software\\osu!parser")
        self.oauth = self.OAuthRegistry(self)
        self.previous = self.PreviousRegistry(self)
        self.settings = self.SettingsRegistry(self)
        self.window = self.WindowRegistry(self)
        super().__init__()

    def refresh(self) -> data.RegistryProvider:
        self.__init__()
        return self


class StringsProvider:
    class Debug:
        function_data = "{0} - {1}"
        test_data = "{0}:\nData: {1}\nExpected: {2}"
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
        initialized = "initialized!"
        debug_close_window = "close_window = {0}"
        error_combobox_value = "Failed to insert combobox value"
        debug_localhost_deploy = "Deploying localhost... | localhost_thread.daemon = {0}"
        error_localhost_deploy = "Failed to refresh access token | localhost_thread.daemon = {0}"
        error_refresh_token = "Failed to refresh access token"
        debug_revoke_token = "Current token revoking skipped | SKIP_REVOKE = {0}"
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


class AssetsProvider:
    class IDirectory:
        _PATH: str = None
        _NAMES: set[str] = None

        def __init__(self, parent: AssetsProvider):
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
        self.grades = self.Grades(self)
        self.images = self.Images(self)

    @staticmethod
    def file_image(path: str) -> PIL.Image.Image:
        with open(path, "rb") as file:
            return PIL.Image.open(io.BytesIO(file.read()))

    @staticmethod
    def network_image(url: str) -> PIL.Image.Image:
        return PIL.Image.open(io.BytesIO(requests.get(url).content))

    @staticmethod
    def round_corners(image: PIL.Image.Image, radius: int) -> PIL.Image.Image:
        if image.mode != "RGB":
            image = image.convert("RGB")
        width, height = image.size
        shape = PIL.Image.new("L", (radius * 2, radius * 2), 0)
        alpha = PIL.Image.new("L", image.size, "white")
        PIL.ImageDraw.Draw(shape).ellipse((0, 0, radius * 2, radius * 2), fill=255)
        alpha.paste(shape.crop((0, 0, radius, radius)), (0, 0))
        alpha.paste(shape.crop((0, radius, radius, radius * 2)), (0, height - radius))
        alpha.paste(shape.crop((radius, 0, radius * 2, radius)), (width - radius, 0))
        alpha.paste(shape.crop((radius, radius, radius * 2, radius * 2)), (width - radius, height - radius))
        image.putalpha(alpha)
        return image


class LoggerService(logging.Logger):
    def __init__(self, name: str, file_handling: bool = True, filename: str = datetime.datetime.now().strftime("%d-%m-%y-%H-%M-%S"), level: int = logging.NOTSET, folder_name: str = "logs") -> None:
        super().__init__(name, level)
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setFormatter(logging.Formatter(fmt="$levelname $asctime $name - $message", datefmt="%d-%m-%y %H:%M:%S", style="$"))
        self.addHandler(stream_handler)
        if file_handling:
            os.makedirs(utils.get_path(folder_name, only_abspath=True), exist_ok=True)
            file_handler = logging.FileHandler(utils.get_path(f"{folder_name}/{filename}-{name}.log", only_abspath=True), encoding="utf-8")
            file_handler.setFormatter(logging.Formatter(fmt="$levelname $asctime - $message", datefmt="%d-%m-%y %H:%M:%S", style="$"))
            self.addHandler(file_handler)

    def log_exception(self, e: Exception) -> None:
        self.error(msg=e, exc_info=True)
