import threading, waitress, logging, flask
import interface, query, data


class LocalhostFlask(flask.Flask):
    def __init__(self, application: interface.Application = None):
        super().__init__(import_name="osu!parser")
        self._application = application
        self._config = data.ConfigProvider()
        self._logger = data.LoggerService(
            name=__name__,
            file_handling=self._config.settings.logging,
            level=logging.DEBUG if self._config.settings.beta else logging.INFO,
        )
        self.add_url_rule(rule="/", view_func=self.base_redirect)
        self.add_url_rule(rule="/osu-parser", view_func=self.get_code)

    def serve(self):
        waitress.serve(app=self, host="127.0.0.1", port=727)

    @staticmethod
    def base_redirect() -> str:
        return """<script>window.location="https://diquoks.ru/";</script>"""

    def get_code(self) -> str | None:
        code = flask.request.args.get(key="code")
        try:
            if isinstance(self._application, interface.Application):
                self._application._oauth.get_access_token(code)
                threading.Thread(target=self._application.oauth_thread, args=(True,), daemon=True, name="oauthThread").start()
            else:
                query.OAuthClient(config=self._config).get_access_token(code)
        except Exception as e:
            self._logger.debug(msg=e, exc_info=True)
            return """<script>window.location="https://diquoks.ru/?from=osu-parser-error";</script>"""
        else:
            return """<script>window.location="https://diquoks.ru/?from=osu-parser-success";</script>"""
