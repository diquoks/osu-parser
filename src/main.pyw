import threading
import interface, localhost


def main() -> None:
    application = interface.Application()
    localhost_flask = localhost.LocalhostFlask(application)
    localhost_thread = threading.Thread(
        target=localhost_flask.serve,
        kwargs={"port": 727},
        daemon=True,
        name="localhostThread",
    )
    localhost_thread.start()
    application.mainloop()


if __name__ == "__main__":
    main()
