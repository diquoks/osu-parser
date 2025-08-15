from __future__ import annotations
import threading
import interface, localhost


def main():
    application = interface.Application()
    localhost_thread = threading.Thread(target=localhost.localhost_serve, args=(application,), daemon=True, name="localhostThread")
    localhost_thread.start()
    application.mainloop()


if __name__ == "__main__":
    main()
