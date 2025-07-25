import threading, traceback, waitress, logging, flask
import interface, query, data

_localhost_flask = flask.Flask(import_name="osu!parser")


@_localhost_flask.route("/")
def base_redirect() -> str:
    return """<script>window.location="https://diquoks.ru/";</script>"""


def get_code(app: interface.Application = None) -> str | None:
    code = flask.request.args.get("code")
    try:
        if isinstance(app, interface.Application):
            app._oauth.get_access_token(code=code)
            threading.Thread(target=app.oauth_thread, args=(True,), daemon=True, name="oauthThread").start()
        else:
            query.OAuthApplication.from_config(config=data.ApplicationConfig().oauth).get_access_token(code=code)
    except:
        logging.error(traceback.format_exc())
        return """<script>window.location="https://diquoks.ru/?from=osu-parser-error";</script>"""
    else:
        return """<script>window.location="https://diquoks.ru/?from=osu-parser-success";</script>"""


def localhost_serve(app: interface.Application = None) -> None:
    _localhost_flask.add_url_rule("/osu-parser", view_func=lambda: get_code(app=app))
    waitress.serve(_localhost_flask, host="127.0.0.1", port=727)
