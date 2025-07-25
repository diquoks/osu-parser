import threading
import interface, localhost


def main():
    application = interface.Application()
    threading.Thread(target=localhost.localhost_serve, args=(application,), daemon=True, name="localhostThread").start()
    application.mainloop()


if __name__ == "__main__":
    main()
