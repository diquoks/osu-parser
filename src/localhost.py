from __future__ import annotations
import threading, logging
import flask
import pyquoks.localhost
import interface, query, data


class LocalhostFlask(pyquoks.localhost.ILocalhostFlask):
    def __init__(self, application: interface.Application = None):
        self._RULES = {
            "/": self.base_redirect,
            "/osu-parser": self.get_code,
        }
        self._application = application
        self._config = data.ConfigProvider()
        self._logger = data.LoggerService(
            name=__name__,
            file_handling=self._config.settings.file_logging,
            level=logging.DEBUG if self._config.settings.beta else logging.INFO,
        )
        super().__init__(import_name="osu!parser")

    @staticmethod
    def base_redirect() -> str:
        return """<script>window.location="https://diquoks.ru/";</script>"""

    def get_code(self) -> str | None:
        code = flask.request.args.get(key="code")
        try:
            if isinstance(self._application, interface.Application):
                self._application._oauth.get_access_token(code)
                threading.Thread(target=self._application.oauth_thread, kwargs={"login": True}, daemon=True, name="oauthThread").start()
            else:
                query.OAuthClient(config=self._config).get_access_token(code)
        except Exception as e:
            self._logger.log_exception(e)
            return """<script>window.location="https://diquoks.ru/?from=osu-parser-error";</script>"""
        else:
            return """<script>window.location="https://diquoks.ru/?from=osu-parser-success";</script>"""
