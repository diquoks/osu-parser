from __future__ import annotations
import configparser, winreg
import various


class ParsingValues:
    """
    :var pp_total: ``float``
    :var pp_diff: ``float``
    :var score_id: ``int`` | ``None``
    :var score_id: ``dict``
    """
    pp_total: float
    pp_diff: float
    score_id: int | None
    settings: ApplicationRegistry.SampleRegistry

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    def update(self, **kwargs):
        self.__init__(**kwargs)


class ApplicationConfig:
    """
    :var oauth: ``OAuthConfig``
    :var settings: ``SettingsConfig``
    """

    class SampleConfig:
        _NAME: str

        def __init__(self, parent: ApplicationConfig) -> None:
            self._config = configparser.ConfigParser()
            self._config.read(various.get_path("config.ini"))
            if not self._config.has_section(self._NAME):
                self._config.add_section(self._NAME)
            for i in parent._CONFIG_VALUES[self._NAME]:
                try:
                    setattr(self, i, self._config.get(self._NAME, i))
                except:
                    self._config.set(self._NAME, i, i)
                    self._config.write(open(various.get_path("config.ini"), "w"))

    class OAuthConfig(SampleConfig):
        """
        :var client_id: ``int``
        :var client_secret: ``str``
        :var redirect_uri: ``str``
        :var scopes: ``str``
        """
        _NAME = "OAuth"
        client_id: int | str | None
        client_secret: str | None
        redirect_uri: str | None
        scopes: str | None

        def __init__(self, parent: ApplicationConfig) -> None:
            super().__init__(parent=parent)
            try:
                self.client_id = int(self.client_id)
            except:
                raise configparser.ParsingError("_config.ini is filled incorrectly!")

    class SettingsConfig(SampleConfig):
        """
        :var beta: ``bool``
        :var version: ``str``
        """
        _NAME = "Settings"
        beta: bool | str | None
        version: str | None

        def __init__(self, parent: ApplicationConfig) -> None:
            super().__init__(parent=parent)
            if self.beta not in [str(True), str(False)]:
                raise configparser.ParsingError("_config.ini is filled incorrectly!")
            else:
                self.beta = self.beta == str(True)

    _CONFIG_VALUES = {
        "OAuth":
            {
                "client_id",
                "client_secret",
                "redirect_uri",
                "scopes",
            },
        "Settings":
            {
                "beta",
                "version",
            },
    }

    def __init__(self) -> None:
        self.oauth = self.OAuthConfig(self)
        self.settings = self.SettingsConfig(self)
        super().__init__()


class ApplicationRegistry:
    """
    :var oauth: ``OAuthRegistry``
    :var previous: ``PreviousRegistry``
    :var settings: ``SettingsRegistry``
    :var window: ``WindowRegistry``
    """

    class SampleRegistry:
        _NAME: str
        _REGISTRY_VALUES: dict

        def __init__(self, parent: ApplicationRegistry = None) -> None:
            if isinstance(parent, ApplicationRegistry):
                self._REGISTRY_VALUES = parent._REGISTRY_VALUES[self._NAME]
                self._path = winreg.CreateKey(parent._path, self._NAME)
            for i in self._REGISTRY_VALUES.keys():
                try:
                    setattr(self, i, winreg.QueryValueEx(self._path, i)[int()])
                except:
                    setattr(self, i, None)
            super().__init__()

        def refresh(self) -> data.ApplicationRegistry.SampleRegistry:
            self.__init__()
            return self

        def update(self, **kwargs) -> None:
            for k, v in kwargs.items():
                winreg.SetValueEx(self._path, k, None, self._REGISTRY_VALUES[k], v)
                setattr(self, k, v)

        def values(self) -> dict:
            return {i: getattr(self, i) for i in self._REGISTRY_VALUES}

    class OAuthRegistry(SampleRegistry):
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

    class PreviousRegistry(SampleRegistry):
        """
        :var user: ``int``
        :var ruleset: ``str``
        :var score: ``str``
        """
        _NAME = "Previous"
        _REGISTRY_VALUES: dict
        _path: winreg.HKEYType
        user: int | None
        ruleset: str | None
        score: str | None

    class SettingsRegistry(SampleRegistry):
        """
        :var float_values: ``bool``
        :var include_fails: ``bool``
        :var lazer_mode: ``bool``
        """
        _NAME = "Settings"
        _REGISTRY_VALUES: dict
        _path: winreg.HKEYType
        float_values: bool | None
        lazer_mode: bool | None
        include_fails: bool | None

    class WindowRegistry(SampleRegistry):
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
            "user": winreg.REG_DWORD,
            "ruleset": winreg.REG_SZ,
            "score": winreg.REG_SZ,
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

    def refresh(self) -> data.ApplicationRegistry:
        self.__init__()
        return self
