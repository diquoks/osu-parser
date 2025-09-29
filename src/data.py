from __future__ import annotations
import winreg
import PIL.Image, PIL.ImageDraw
import pyquoks.data, pyquoks.utils


# Named classes
class ConfigProvider(pyquoks.data.IConfigProvider):
    class OAuthConfig(pyquoks.data.IConfigProvider.IConfig):
        _SECTION = "OAuth"
        client_id: int
        client_secret: str
        redirect_uri: str
        scopes: str
        server: str

    class SettingsConfig(pyquoks.data.IConfigProvider.IConfig):
        _SECTION = "Settings"
        beta: bool
        file_logging: bool
        version: str

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
                "file_logging": bool,
                "version": str,
            },
    }
    _CONFIG_OBJECTS = {
        "oauth": OAuthConfig,
        "settings": SettingsConfig,
    }
    oauth: OAuthConfig
    settings: SettingsConfig


class AssetsProvider(pyquoks.data.IAssetsProvider):
    class GradesDirectory(pyquoks.data.IAssetsProvider.IDirectory):
        _PATH = "grades/{0}.png"
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

    class ImagesDirectory(pyquoks.data.IAssetsProvider.IDirectory):
        _PATH = "images/{0}.png"
        _NAMES = {
            "avatar_guest",
        }
        avatar_guest: PIL.Image.Image

    _PATH = pyquoks.utils.get_path("assets/{0}")
    _ASSETS_OBJECTS = {
        "grades": GradesDirectory,
        "images": ImagesDirectory,
    }


class StringsProvider(pyquoks.data.IStringsProvider):
    class DebugStrings(pyquoks.data.IStringsProvider.IStrings):
        function_data = "{0} - {1}"
        test_data = "{0}:\nData: {1}\nExpected: {2}"
        attribute_data = "{0}: {1}"

    class LocalisableStrings(pyquoks.data.IStringsProvider.IStrings):
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

    class LogStrings(pyquoks.data.IStringsProvider.IStrings):
        initialized = "initialized!"
        debug_close_window = "close_window = {0}"
        error_combobox_value = "Failed to insert combobox value"
        debug_localhost_deploy = "Deploying localhost... | localhost_thread.daemon = {0}"
        error_localhost_deploy = "Failed to refresh access token | localhost_thread.daemon = {0}"
        error_refresh_token = "Failed to refresh access token"
        debug_revoke_token = "Current token revoking skipped | SKIP_REVOKE = {0}"
        error_revoke_token = "Failed to revoke current token"

    class SeparatorStrings(pyquoks.data.IStringsProvider.IStrings):
        comma = ", "
        space = " "
        newline = "\n"
        arrow = " -> "
        column = " | "
        dash = " - "

    class UrlStrings(pyquoks.data.IStringsProvider.IStrings):
        score = "https://osu.ppy.sh/scores/{0}"
        user_ruleset = "https://osu.ppy.sh/users/{0}/{1}"
        beatmap_ruleset = "https://osu.ppy.sh/beatmaps/{0}?mode={1}"
        latest_release = "https://github.com/diquoks/osu-parser/releases/latest"
        guide = "https://github.com/diquoks/osu-parser/blob/master/GUIDE.md"
        diquoks_web = "https://diquoks.ru"

    _STRINGS_OBJECTS = {
        "debug": DebugStrings,
        "log": LogStrings,
        "localisable": LocalisableStrings,
        "separator": SeparatorStrings,
        "url": UrlStrings,
    }
    debug: DebugStrings
    log: LogStrings
    localisable: LocalisableStrings
    separator: SeparatorStrings
    url: UrlStrings


class RegistryManager(pyquoks.data.IRegistryManager):
    class OAuthRegistry(pyquoks.data.IRegistryManager.IRegistry):
        _NAME = "OAuth"
        access_token: str
        expires_in: int
        refresh_token: str
        token_type: str

    class PreviousRegistry(pyquoks.data.IRegistryManager.IRegistry):
        _NAME = "Previous"
        ruleset: str
        score: str
        user: int

    class SettingsRegistry(pyquoks.data.IRegistryManager.IRegistry):
        _NAME = "Settings"
        float_values: bool
        include_fails: bool
        lazer_mode: bool

    class WindowRegistry(pyquoks.data.IRegistryManager.IRegistry):
        _NAME = "Window"
        dimensions: str
        state: str
        theme: str
        topmost: bool

    _KEY = "Software\\diquoks Software\\osu!parser"
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
    _REGISTRY_OBJECTS = {
        "oauth": OAuthRegistry,
        "previous": PreviousRegistry,
        "settings": SettingsRegistry,
        "window": WindowRegistry,
    }
    oauth: OAuthRegistry
    previous: PreviousRegistry
    settings: SettingsRegistry
    window: WindowRegistry


class LoggerService(pyquoks.data.LoggerService):
    pass
