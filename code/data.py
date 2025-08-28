from __future__ import annotations
import configparser, datetime, logging, winreg, sys, os
import utils


class ConfigProvider:
    """
    :var oauth: ``OAuthConfig``
    :var settings: ``SettingsConfig``
    """

    class IConfig:
        _SECTION: str = None
        _CONFIG_VALUES: set = None

        def __init__(self, parent: ConfigProvider = None) -> None:
            if isinstance(parent, ConfigProvider):
                self._CONFIG_VALUES = parent._CONFIG_VALUES[self._SECTION]
                self._config = configparser.ConfigParser()
                self._config.read(utils.get_path(relative_path="config.ini"))
                if not self._config.has_section(self._SECTION):
                    self._config.add_section(self._SECTION)
                for i in self._CONFIG_VALUES:
                    try:
                        setattr(self, i, self._config.get(self._SECTION, i))
                    except:
                        self._config.set(self._SECTION, i, i)
                        self._config.write(open(utils.get_path(relative_path="config.ini"), "w"))

        @property
        def values(self) -> dict:
            return {i: getattr(self, i) for i in self._CONFIG_VALUES}

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

        def __init__(self, parent: ConfigProvider) -> None:
            super().__init__(parent)
            try:
                self.client_id = int(self.client_id)
            except:
                self.client_id = None
                raise configparser.ParsingError("config.ini is filled incorrectly!")

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

        def __init__(self, parent: ConfigProvider) -> None:
            super().__init__(parent)
            for i in ["beta", "logging"]:
                if getattr(self, i) not in [str(True), str(False)]:
                    setattr(self, i, None)
                    raise configparser.ParsingError("config.ini is filled incorrectly!")
                else:
                    setattr(self, i, getattr(self, i) == str(True))

    _CONFIG_VALUES = {
        "OAuth":
            {
                "client_id",
                "client_secret",
                "redirect_uri",
                "scopes",
                "server",
            },
        "Settings":
            {
                "beta",
                "logging",
                "version",
            },
    }

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
        def values(self) -> dict:
            return {i: getattr(self, i) for i in self._REGISTRY_VALUES}

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


class LoggerService(logging.Logger):
    def __init__(self, name: str, file_handling: bool = True, filename: str = datetime.datetime.now().strftime("%d-%m-%y-%H-%M-%S"), level: int = logging.NOTSET, folder_name: str = "logs") -> None:
        super().__init__(name, level)
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setFormatter(logging.Formatter(fmt="$levelname $asctime $name - $message", datefmt="%d-%m-%y %H:%M:%S", style="$"))
        self.handlers.append(stream_handler)
        if file_handling:
            os.makedirs(folder_name, exist_ok=True)
            file_handler = logging.FileHandler(f"{folder_name}/{filename}-{name}.log")
            file_handler.setFormatter(logging.Formatter(fmt="$levelname $asctime - $message", datefmt="%d-%m-%y %H:%M:%S", style="$"))
            self.handlers.append(file_handler)
