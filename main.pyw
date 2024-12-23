#        ▄▄   ▄▄
#      ▀███   ██                             ▀██▄
#        ██                                    ██
#   ▄█▀▀███ ▀███  ▄██▀██▄▀███  ▀███   ▄██▀██▄  ██  ▄██▀ ▄██▀██▄
# ▄██    ██   ██ ▄█▀   ██  ██    ██  ██▀   ▀██ ██ ▄█    ██   ▀▀
# ███    ██   ██ ██    ██  ██    ██  ██     ██ ██▄██    ▀█████▄
# ▀██    ██   ██ ██▄   ██  ██    ██  ██▄   ▄██ ██ ▀██▄  █▄   ██
#  ▀████▀███▄████▄▀██████  ▀████▀███▄ ▀█████▀▄████▄ ██▄▄▀█████▀
#                      ██
#                   ▄████▄
# Импорт библиотек
import webbrowser, threading, datetime, tkinter, winreg, time, glob, osu, re, os
import rosu_pp_py as rosu
from tkinter import filedialog, ttk
from tkinter import *

# Объявление переменных
program_version = "v0.7.5"
registry_path = winreg.CreateKey(winreg.HKEY_CURRENT_USER, "Software\\diquoks\\osu!parser")
registry_path_application = winreg.CreateKey(registry_path, "Application")
registry_path_settings = winreg.CreateKey(registry_path, "Settings")
registry_path_previous = winreg.CreateKey(registry_path, "Previous")

# Функции os
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Функции osu.py
def get_profile(client_id, client_secret, player_id, osu_mode):
    try:
        return osu.Client.from_credentials(client_id=client_id, client_secret=client_secret, redirect_url=None).get_user(user=player_id, mode=osu_mode)
    except Exception as e:
        if "Not Found" not in str(e):
            return get_profile(client_id, client_secret, player_id, osu_mode)
        else:
            return None

def get_beatmap(client_id, client_secret, beatmap_id):
    try:
        return osu.Client.from_credentials(client_id=client_id, client_secret=client_secret, redirect_url=None).get_beatmap(beatmap=beatmap_id)
    except:
        return get_beatmap(client_id, client_secret, beatmap_id)

def get_beatmap_attributes(client_id, client_secret, beatmap_id, osu_mode):
    try:
        return osu.Client.from_credentials(client_id=client_id, client_secret=client_secret, redirect_url=None).get_beatmap_attributes(beatmap=beatmap_id, ruleset=osu_mode)
    except:
        return get_beatmap_attributes(client_id, client_secret, beatmap_id, osu_mode)

def get_score(client_id, client_secret, score_id):
    try:
        return osu.Client.from_credentials(client_id=client_id, client_secret=client_secret, redirect_url=None).get_score_by_id_only(score_id=score_id)
    except Exception as e:
        if "not found" not in e:
            return get_score(client_id, client_secret, score_id)
        else:
            return None

def get_last_score(client_id, client_secret, player_id, osu_mode):
    try:
        return osu.Client.from_credentials(client_id=client_id, client_secret=client_secret, redirect_url=None).get_user_scores(user=player_id, mode=osu_mode, type=osu.UserScoreType.RECENT, include_fails=True, limit=1)[0]
    except IndexError:
        return None
    except:
        return get_last_score(client_id, client_secret, player_id, osu_mode)

def get_score_weight(client_id, client_secret, player_id, score_id, osu_mode):
    try:
        n = 0
        for top_score in osu.Client.from_credentials(client_id=client_id, client_secret=client_secret, redirect_url=None).get_user_scores(user=player_id, mode=osu_mode, type=osu.UserScoreType.BEST, limit=100):
            n += 1
            if score_id == top_score.id:
                return [top_score.weight, n]
        else:
            return None
    except:
        return get_score_weight(client_id, client_secret, player_id, score_id, osu_mode)

# Функции tkinter
def open_settings():
    global main_menu, settings
    main_menu.pack_forget()
    settings.pack(expand=True, fill=BOTH)

def save_settings():
    global client_id, client_secret, app_id_entry, app_secret_entry
    try:
        if winreg.QueryValueEx(registry_path_application, "client_id")[0] == str(app_id_entry.get()) and winreg.QueryValueEx(registry_path_application, "client_secret")[0] == app_secret_entry.get():
            tkinter.messagebox.showinfo(title="osu!parser", message="Настройки уже используются!")
        else:
            raise Exception
    except:
        try:
            client_id = int(app_id_entry.get())
        except:
            tkinter.messagebox.showinfo(title="osu!parser", message="ID приложения должен быть числом!")
        else:
            client_secret = app_secret_entry.get()
            winreg.SetValueEx(registry_path_application, "client_id", 0, winreg.REG_SZ, str(client_id))
            winreg.SetValueEx(registry_path_application, "client_secret", 0, winreg.REG_SZ, client_secret)
            tkinter.messagebox.showinfo(title="osu!parser", message="Настройки сохранены!")

def open_additional_settings():
    global additional_window, additional_osu_path_label, root
    (additional_window := Toplevel(root)).focus_force()
    additional_window.grab_set()
    additional_window.resizable(width=False, height=False)
    additional_window.geometry("300x200")
    additional_window.iconbitmap(resource_path("window_icon.ico"))
    additional_window.title("настройки osu!parser")
    additional_window.attributes("-topmost", True)
    # Дополнительные настройки
    additional_settings = ttk.Frame(additional_window)
    (additional_frame := ttk.Frame(additional_settings)).pack(fill=BOTH, expand=True, side=TOP)
    (additional_left_frame := ttk.Frame(additional_frame)).pack(fill=BOTH, side=LEFT, pady=5)
    (additional_right_frame := ttk.Frame(additional_frame)).pack(fill=BOTH, side=RIGHT, pady=5)
    (additional_last_score__settings_label := ttk.Label(additional_left_frame, text="Настройки парсинга")).pack(side=TOP, anchor=N, padx=5)
    (additional_ignore_classic := ttk.Checkbutton(additional_left_frame, text="Игнорировать Classic", variable=ignore_classic, command=ignore_classic_switched)).pack(side=TOP, anchor=NW, padx=5, pady=5)
    (additional_recalculations := ttk.Checkbutton(additional_left_frame, text="Расчёт pp за FC и SS", variable=recalculations)).pack(side=TOP, anchor=NW, padx=5, pady=5)
    (additional_program_settings_label := ttk.Label(additional_right_frame, text="Настройки программы")).pack(side=TOP, anchor=N, padx=5)
    (additional_topmost_switch := ttk.Checkbutton(additional_right_frame, text="Поверх других окон", variable=topmost, command=topmost_switched)).pack(side=TOP, anchor=NE, padx=5, pady=5)
    (additional_osu_path_label := ttk.Label(additional_settings, text=osu_path)).pack(side=TOP, anchor=SW, padx=10)
    additional_osu_path_label.bind("<Button-1>", lambda i: os.system(f"explorer.exe {osu_path}"))
    (additional_osu_path_button := ttk.Button(additional_settings, text="Выбрать папку osu!", command=osu_path_select)).pack(side=LEFT, anchor=SW, padx=10, pady=10, fill=X, expand=True)
    (additional_close_button := ttk.Button(additional_settings, text="Закрыть", command=additional_window.destroy, width=15)).pack(side=RIGHT, anchor=SE, padx=10, pady=10)
    # Отрисовка дополнительных настроек
    additional_settings.pack(expand=True, fill=BOTH)
    # Цикл окна настроек
    additional_window.mainloop()

def ignore_classic_switched():
    global ignore_classic
    winreg.SetValueEx(registry_path_settings, "ignore_classic", 0, winreg.REG_SZ, str(ignore_classic.get()))

def recalculations_switched():
    global recalculations
    winreg.SetValueEx(registry_path_settings, "recalculations", 0, winreg.REG_SZ, str(recalculations.get()))

def topmost_switched():
    global additional_window, topmost
    root.attributes("-topmost", bool(topmost.get()))
    additional_window.attributes("-topmost", True)
    winreg.SetValueEx(registry_path_settings, "topmost", 0, winreg.REG_SZ, str(topmost.get()))

def osu_path_select():
    global additional_window, additional_osu_path_label, osu_path
    if (selected_path := filedialog.askdirectory(parent=additional_window, title="Выбор директории osu!", initialdir=osu_path, mustexist=True) .replace("/", "\\")) != "":
        osu_path = selected_path
        winreg.SetValueEx(registry_path_settings, "osu_path", 0, winreg.REG_SZ, osu_path)
    additional_osu_path_label["text"] = osu_path

def close_settings():
    global main_menu, settings
    settings.pack_forget()
    main_menu.pack(expand=True, fill=BOTH)

def open_last_score():
    global main_menu, last_score
    main_menu.pack_forget()
    last_score.pack(expand=True, fill=BOTH)

def get_osu_mode():
    global last_score_osu_mode_combobox
    return {"osu!": osu.GameModeStr.STANDARD.value,
            "osu!taiko": osu.GameModeStr.TAIKO.value,
            "osu!catch": osu.GameModeStr.CATCH.value,
            "osu!mania": osu.GameModeStr.MANIA.value}[last_score_osu_mode_combobox.get()]

def last_score_parsing(client_id, client_secret, player_id, osu_mode):
    global recalculation, last_score_parsing_status, last_score_update_label, last_score_progressbar, last_score_start, last_score_stop
    winreg.SetValueEx(registry_path_previous, "player_id", 0, winreg.REG_SZ, str(player_id))
    winreg.SetValueEx(registry_path_previous, "osu_mode", 0, winreg.REG_SZ, osu_mode)
    last_score_update_label.config(text=f"Обновление...")
    last_score_progressbar.config(value=25)
    if (player := get_profile(client_id, client_secret, player_id, osu_mode)) is not None:
        previous_score = [player.statistics.pp, None, 0]
    else:
        last_score_progressbar.config(mode="determinate")
        last_score_update_label.config(text="")
        last_score_player_label.config(text="Игрок не найден!")
        last_score_parsing_status = False
    while last_score_parsing_status:
        if last_score_parsing_status:
            last_score_update_label.config(text=f"Обновление...")
            last_score_progressbar.config(value=35)
            if (score := get_last_score(client_id, client_secret, player_id, osu_mode)) is not None:
                weight = get_score_weight(client_id, client_secret, player_id, score.id, osu_mode)
                if last_score_parsing_status:
                    last_score_progressbar.config(value=45)
                    player = get_profile(client_id, client_secret, player_id, osu_mode)
                    if previous_score[1] != score.id:
                        previous_score = [player.statistics.pp, score.id, player.statistics.pp - previous_score[0]]
                if last_score_parsing_status:
                    last_score_progressbar.config(value=55)
                    beatmap = get_beatmap(client_id, client_secret, score.beatmap_id)
                    beatmap_attributes = get_beatmap_attributes(client_id, client_secret, score.beatmap_id, osu_mode)
                if last_score_parsing_status and bool(recalculations.get()):
                    recalculation = beatmap_path = ""
                    lazer_score = "CL" not in (mods_list := [getattr(score.mods[i].mod, "value") for i in range(len(score.mods))])
                    try:
                        beatmap_path = glob.glob(f"{osu_path}\\Songs\\{beatmap.beatmapset_id}*/*{beatmap.version}].osu", recursive=True)[0]
                        if score.max_combo/beatmap_attributes.max_combo < 0.975 and score.rank.name not in ["S", "SILVER_S"]:
                            recalculation = f", FC: {round(rosu.Performance(mods="".join(mods_list), n100=score.statistics.ok, n50=score.statistics.meh, lazer=lazer_score, hitresult_priority=rosu.HitResultPriority.BestCase).calculate(rosu.Beatmap(path=beatmap_path)).pp, 2)}pp"
                        elif score.rank.name not in ["SS", "SILVER_SS"]:
                            recalculation = f", SS: {round(rosu.Performance(mods="".join(mods_list), lazer=lazer_score, hitresult_priority=rosu.HitResultPriority.BestCase).calculate(rosu.Beatmap(path=beatmap_path)).pp, 2)}pp"
                    except Exception as e:
                        print(e)
                if last_score_parsing_status:
                    last_score_player_label.config(text=f"{player.username} (#{player.rank_history.data[-1]})")
                    last_score_player_label.bind("<Button-1>", lambda i: webbrowser.open_new(f"https://osu.ppy.sh/users/{player.id}/{osu_mode}"))
                    last_score_link_label.config(text=f"https://osu.ppy.sh/scores/{score.id}")
                    last_score_link_label.bind("<Button-1>", lambda i: webbrowser.open_new(f"https://osu.ppy.sh/scores/{score.id}"))
                    last_score_map_label.config(text=f"{score.beatmapset.artist} - {score.beatmapset.title} от {score.beatmapset.creator}")
                    last_score_diff_label.config(text=f"({score.beatmap.version}, {score.beatmap.difficulty_rating}*, {score.beatmap.ranked.name}){recalculation}")
                    last_score_pp_label.config(text=f"Всего: {round(player.statistics.pp, 2)}pp{"" if (difference_pp := round(previous_score[2], 2)) == 0.00 else f" {f"({"{:+.2f}".format(difference_pp)}pp)"}"}{f", Рекорд: {round(score.pp, 2)}pp{f" - #{weight[1]}, Вес: {int(weight[0].percentage)}% ({round(weight[0].pp, 2)}pp)" if weight is not None else ""}" if score.pp is not None else ""}")
                    last_score_mods_label.config(text=f"{mods_str if (mods_str := f"Моды: {", ".join(map(str, ((mods_list, mods_list.remove("CL") if "CL" in mods_list and bool(ignore_classic.get()) else None), mods_list if mods_list is not None else "")[1]))}") != "Моды: " else ""}".replace("None", "0"))
                    last_score_grades_label.config(text=f"Ранк: {score.rank.name.replace("SILVER_SS", "SS+").replace("SILVER_S", "S+")}, Точность: {round(score.accuracy * 100, 2)}%, Комбо: {score.max_combo}x{f"/{beatmap_attributes.max_combo}x"}")
                    if osu_mode == osu.GameModeStr.STANDARD.value:
                        last_score_scores_label.config(text=f"300: {score.statistics.great}/{score.maximum_statistics.great}, 100: {score.statistics.ok}, 50: {score.statistics.meh}, Miss: {score.statistics.miss}".replace("None", "0"))
                        last_score_scores_additional_label.config(text=f"{"PASSED" if score.passed else "FAILED"}")
                    elif osu_mode == osu.GameModeStr.TAIKO.value:
                        last_score_scores_label.config(text=f"300: {score.statistics.great}/{score.maximum_statistics.great}, 100: {score.statistics.ok}, Miss: {score.statistics.miss}".replace("None", "0"))
                        last_score_scores_additional_label.config(text=f"{"PASSED" if score.passed else "FAILED"}")
                    elif osu_mode == osu.GameModeStr.CATCH.value:
                        last_score_scores_label.config(text=f"Fruits: {score.statistics.great}/{score.maximum_statistics.great}, Ticks: {score.statistics.large_tick_hit}/{score.maximum_statistics.large_tick_hit}, Droplets: {score.statistics.small_tick_hit}/{score.maximum_statistics.small_tick_hit}".replace("None", "0"))
                        last_score_scores_additional_label.config(text=f"{"PASSED" if score.passed else "FAILED"}")
                    elif osu_mode == osu.GameModeStr.MANIA.value:
                        last_score_scores_label.config(text=f"Max: {score.statistics.perfect}/{score.maximum_statistics.perfect}, 300: {score.statistics.great}, 200: {score.statistics.good}".replace("None", "0"))
                        last_score_scores_additional_label.config(text=f"100: {score.statistics.ok}, 50: {score.statistics.meh}, Miss: {score.statistics.miss}, {"PASSED" if score.passed else "FAILED"}".replace("None", "0"))
            else:
                last_score_progressbar.config(value=55)
                player = get_profile(client_id, client_secret, player_id, osu_mode)
                last_score_player_label.config(text=f"{player.username} (#{player.rank_history.data[-1]})")
                last_score_player_label.bind("<Button-1>", lambda i: webbrowser.open_new(f"https://osu.ppy.sh/users/{player.id}/{osu_mode}"))
                last_score_link_label.config(text="Последний рекорд отсутствует!")
            fastmode_current = fastmode.get()
            for i in range(3 if fastmode_current == 1 else 15, 0, -1):
                if last_score_parsing_status:
                    last_score_progressbar.config(value=(15 - (i * 5 if fastmode_current == 1 else i) + 1))
                    last_score_update_label.config(text=f"Обновление через: {i}")
                    time.sleep(1)
    last_score_update_label.config(text="")
    last_score_progressbar.config(value=0)
    last_score_player_label.config(text="")
    last_score_player_label.unbind("<Button-1>")
    last_score_link_label.config(text="")
    last_score_link_label.unbind("<Button-1>")
    last_score_map_label.config(text="")
    last_score_diff_label.config(text="")
    last_score_pp_label.config(text="")
    last_score_mods_label.config(text="")
    last_score_grades_label.config(text="")
    last_score_scores_label.config(text="")
    last_score_scores_additional_label.config(text="")
    last_score_start.config(state=ACTIVE)
    last_score_stop.config(state=DISABLED)
    last_score_stop.pack_forget()
    last_score_start.pack(side=TOP, anchor=NW, padx=8, pady=7)

def last_score_parsing_start():
    global last_score_parsing_status, client_id, client_secret, player_id, last_score_parsing_thread, last_score_start, last_score_stop
    last_score_parsing_status = True
    try:
        player_id = int(last_score_player_id_entry.get())
    except:
        tkinter.messagebox.showinfo(title="osu!parser", message="ID игрока должен быть числом!")
    else:
        try:
            (last_score_parsing_thread := threading.Thread(target=last_score_parsing, args=(client_id, client_secret, player_id, get_osu_mode()), daemon=True)).start()
        except:
            tkinter.messagebox.showinfo(title="osu!parser", message="Сначала заполните все поля!")
        else:
            last_score_start.config(state=DISABLED)
            last_score_start.pack_forget()
            last_score_stop.config(state=ACTIVE)
            last_score_stop.pack(side=TOP, anchor=NW, padx=8, pady=7)

def last_score_parsing_stop():
    global last_score_parsing_status, last_score_parsing_thread
    last_score_parsing_status = False
    last_score_progressbar.config(mode="indeterminate")
    last_score_progressbar.start()
    try:
        last_score_parsing_thread.join()
    except:
        pass
    last_score_progressbar.config(mode="determinate")
    last_score_progressbar.stop()

def fastmode_switched():
    global fastmode
    winreg.SetValueEx(registry_path_settings, "fastmode", 0, winreg.REG_SZ, str(fastmode.get()))

def close_last_score():
    global main_menu, last_score
    threading.Thread(target=last_score_parsing_stop, daemon=True).start()
    last_score.pack_forget()
    main_menu.pack(expand=True, fill=BOTH)

# Создание окна
root = Tk()
# Объявление переменных tkinter
ignore_classic = IntVar()
try:
    ignore_classic.set(int(winreg.QueryValueEx(registry_path_settings, "ignore_classic")[0]))
except:
    ignore_classic.set(0)

recalculations = IntVar()
try:
    recalculations.set(int(winreg.QueryValueEx(registry_path_settings, "recalculations")[0]))
except:
    recalculations.set(1)

topmost = IntVar()
try:
    topmost.set(int(winreg.QueryValueEx(registry_path_settings, "topmost")[0]))
except:
    topmost.set(0)

fastmode = IntVar()
try:
    fastmode.set(int(winreg.QueryValueEx(registry_path_settings, "fastmode")[0]))
except:
    fastmode.set(0)
# Настройки окна
root.resizable(width=True, height=True)
root.minsize(550, 300)
root.iconbitmap(resource_path("window_icon.ico"))
root.title("osu!parser")
root.attributes("-topmost", bool(topmost.get()))
# Главное меню
main_menu = ttk.Frame(root)
(title := ttk.Label(main_menu, text="osu!parser")).pack(side=TOP, anchor=CENTER, pady=2)
(last_score_button := ttk.Button(main_menu, text="Парсинг последнего рекорда", command=open_last_score, width=30)).pack(side=TOP, anchor=CENTER, pady=40)
(profile_button := ttk.Button(main_menu, text="Парсинг профиля в .txt", state=DISABLED, width=30)).pack(side=TOP, anchor=CENTER, pady=10)
(score_button := ttk.Button(main_menu, text="Парсинг рекорда в .txt", state=DISABLED, width=30)).pack(side=TOP, anchor=CENTER, pady=10)
(main_menu_bottom := ttk.Frame(main_menu)).pack(fill=BOTH, side=BOTTOM)
(help_button := ttk.Button(main_menu_bottom, text="Помощь", command=lambda: webbrowser.open_new("https://github.com/diquoks/osu-parser/blob/master/README.md"), width=15)).pack(side=LEFT, anchor=SW, padx=10, pady=10)
(main_menu_program_version_label := ttk.Label(main_menu_bottom, text=program_version)).pack(side=LEFT, expand=True)
main_menu_program_version_label.bind("<Button-1>", lambda i: webbrowser.open_new("https://github.com/diquoks/osu-parser/releases"))
(settings_button := ttk.Button(main_menu_bottom, text="Настройки", command=open_settings, width=15)).pack(side=RIGHT, anchor=SE, padx=10, pady=10)
# Настройки
settings = ttk.Frame(root)
(settings_title := ttk.Label(settings, text="настройки osu!parser")).pack(side=TOP, anchor=CENTER, pady=2)
(app_settings_border := ttk.LabelFrame(settings)).pack(side=TOP, anchor=CENTER, pady=15)
(app_id_border := ttk.LabelFrame(app_settings_border, text="ID:")).pack(side=LEFT, anchor=NW, padx=10, pady=8)
(app_id_entry := ttk.Entry(app_id_border, width=7)).pack(side=LEFT, anchor=NW, padx=7, pady=3)
(app_secret_border := ttk.LabelFrame(app_settings_border, text="Секретный ключ приложения:")).pack(side=LEFT, anchor=NW, pady=8)
(app_secret_entry := ttk.Entry(app_secret_border, width=48)).pack(side=LEFT, anchor=NW, padx=7, pady=3)
(app_settings_save := ttk.Button(app_settings_border, text="ОК", command=save_settings, width=5)).pack(side=LEFT, anchor=NW, padx=7, pady=15, ipady=7)
(app_settings_setup_link := ttk.Label(settings, text="Создайте своё приложение: https://osu.ppy.sh/home/account/edit#oauth")).pack(side=TOP, anchor=CENTER, pady=1)
(app_settings_setup_path := ttk.Label(settings, text="OAuth -> мои приложения -> новое приложение OAuth -> Зарегистрировать")).pack(side=TOP, anchor=CENTER)
app_settings_setup_link.bind("<Button-1>", lambda i: webbrowser.open_new("https://osu.ppy.sh/home/account/edit#oauth"))
(settings_bottom := ttk.Frame(settings)).pack(fill=BOTH, side=BOTTOM)
(settings_additional_button := ttk.Button(settings_bottom, text="Дополнительно", command=open_additional_settings, width=15)).pack(side=LEFT, anchor=SW, padx=10, pady=10)
(settings_credits_label := ttk.Label(settings_bottom, text="Сделано diquoks ❤")).pack(side=LEFT, expand=True)
settings_credits_label.bind("<Button-1>", lambda i: webbrowser.open_new("https://diquoks.ru"))
(settings_close_button := ttk.Button(settings_bottom, text="Назад", command=close_settings, width=15)).pack(side=RIGHT, anchor=SE, padx=10, pady=10)
# Последний рекорд
last_score = ttk.Frame(root)
(last_score_title := ttk.Label(last_score, text="osu!parser")).pack(side=TOP, anchor=CENTER, pady=2)
(last_score_settings_border := ttk.LabelFrame(last_score)).pack(fill=BOTH, side=LEFT, anchor=CENTER)
(last_score_player_id_frame := ttk.Frame(last_score_settings_border)).pack(fill=BOTH, side=TOP, anchor=NW, padx=(10, 0), pady=3)
(last_score_player_id_border := ttk.LabelFrame(last_score_player_id_frame, text="ID игрока:")).pack(side=LEFT, anchor=NW, pady=3)
(last_score_player_id_entry := ttk.Entry(last_score_player_id_border, width=17)).pack(padx=7, pady=3)
(last_score_osu_mode_border := ttk.LabelFrame(last_score_settings_border, text="Режим:")).pack(side=TOP, anchor=NW, padx=10, pady=3)
(last_score_osu_mode_combobox := ttk.Combobox(last_score_osu_mode_border, values=["osu!", "osu!taiko", "osu!catch", "osu!mania"], state="readonly", width=14)).pack(side=LEFT, padx=7, pady=3)
(last_score_progressbar_border := ttk.LabelFrame(last_score_settings_border, text="Прогресс:")).pack(side=TOP, anchor=NW, padx=10, pady=3)
(last_score_progressbar := ttk.Progressbar(last_score_progressbar_border, orient="horizontal", length=107, maximum=55)).pack(side=TOP, anchor=CENTER, padx=7, pady=3)
(last_score_start := ttk.Button(last_score_settings_border, text="Запустить", command=last_score_parsing_start, width=20)).pack(side=TOP, anchor=NW, padx=8, pady=7)
last_score_stop = ttk.Button(last_score_settings_border, text="Остановить", command=lambda: threading.Thread(target=last_score_parsing_stop, daemon=True).start(), width=20)
(last_score_fastmode_switch := ttk.Checkbutton(last_score_settings_border, text="Быстрый режим", variable=fastmode, command=fastmode_switched)).pack(side=BOTTOM, anchor=CENTER, padx=10, pady=10)
(last_score_update_frame_top := ttk.Frame(last_score)).pack(fill=BOTH, side=TOP, pady=10)
(last_score_player_label := ttk.Label(last_score_update_frame_top)).pack(side=LEFT, anchor=NW, padx=10)
(last_score_update_label := ttk.Label(last_score_update_frame_top)).pack(side=RIGHT, anchor=NE, padx=16)
(last_score_link_label := ttk.Label(last_score)).pack(side=TOP, anchor=NW, padx=10, pady=2)
(last_score_map_label := ttk.Label(last_score)).pack(side=TOP, anchor=NW, padx=10, pady=2)
(last_score_diff_label := ttk.Label(last_score)).pack(side=TOP, anchor=NW, padx=10, pady=2)
(last_score_pp_label := ttk.Label(last_score)).pack(side=TOP, anchor=NW, padx=10, pady=2)
(last_score_mods_label := ttk.Label(last_score)).pack(side=TOP, anchor=NW, padx=10, pady=2)
(last_score_grades_label := ttk.Label(last_score)).pack(side=TOP, anchor=NW, padx=10, pady=2)
(last_score_scores_label := ttk.Label(last_score)).pack(side=TOP, anchor=NW, padx=10, pady=2)
(last_score_scores_additional_label := ttk.Label(last_score)).pack(side=TOP, anchor=NW, padx=10)
(last_score_close_button := ttk.Button(last_score, text="Назад", command=close_last_score, width=15)).pack(side=BOTTOM, anchor=SE, padx=10, pady=10)
# Подстановка значений и отрисовка главного меню
try:
    if (osu_path := winreg.QueryValueEx(registry_path_settings, "osu_path")[0]) == "":
        osu_path = f"{os.getenv("LOCALAPPDATA")}\\osu!"
except:
    osu_path = f"{os.getenv("LOCALAPPDATA")}\\osu!"

try:
    app_id_entry.insert(END, (client_id := winreg.QueryValueEx(registry_path_application, "client_id")[0]))
    app_secret_entry.insert(END, (client_secret := winreg.QueryValueEx(registry_path_application, "client_secret")[0]))
except:
    pass

try:
    last_score_osu_mode_combobox.current({osu.GameModeStr.STANDARD.value: osu.GameModeInt.STANDARD.value,
                                          osu.GameModeStr.TAIKO.value: osu.GameModeInt.TAIKO.value,
                                          osu.GameModeStr.CATCH.value: osu.GameModeInt.CATCH.value,
                                          osu.GameModeStr.MANIA.value: osu.GameModeInt.MANIA.value}[winreg.QueryValueEx(registry_path_previous, "osu_mode")[0]])
    last_score_player_id_entry.insert(END, winreg.QueryValueEx(registry_path_previous, "player_id")[0])
except:
    pass

main_menu.pack(expand=True, fill=BOTH)
# Цикл главного окна
root.mainloop()