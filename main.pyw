# Ты думал тут что-то будет?
#
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
#
# Импорт библиотек
import webbrowser, traceback, threading, requests, datetime, tkinter, winreg, ctypes, string, time, glob, ast, osu, sys, re, os
import rosu_pp_py as rosu
from tkinter import messagebox, filedialog, ttk
from tkinter import *

# Объявление переменных и работа с реестром
program_version = "v1.0.3" # β используется для бета-версий
(user32 := ctypes.windll.user32).SetProcessDPIAware()
ui_scale = user32.GetDpiForSystem() / 96
registry_path = winreg.CreateKey(winreg.HKEY_CURRENT_USER, "Software\\diquoks\\osu!parser")
registry_path_application = winreg.CreateKey(registry_path, "Application")
registry_path_settings = winreg.CreateKey(registry_path, "Settings")
registry_path_previous = winreg.CreateKey(registry_path, "Previous")
try:
    if (osu_path := winreg.QueryValueEx(registry_path_settings, "osu_path")[0]) == "":
        osu_path = "Директория osu! не найдена!"
except:
    osu_path = "Директория osu! не найдена!"
try:
    if (text_parsing_path := winreg.QueryValueEx(registry_path_settings, "text_parsing_path")[0]) == "":
        raise Exception
except:
    try:
        text_parsing_path = f"{glob.glob(os.getenv("USERPROFILE"), recursive=True)[0]}\\Documents\\osu!parser_exports"
        try:
            os.mkdir(text_parsing_path)
        except:
            pass
    except:
        text_parsing_path = f"{glob.glob(os.getenv("HOMEDRIVE"), recursive=True)[0]}\\osu!parser_exports"
        try:
            os.mkdir(text_parsing_path)
        except:
            pass

# Функции os
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Функции requests
def program_version_status():
    global program_version, main_menu_program_version_label
    if "β" not in program_version and requests.get("https://github.com/diquoks/osu-parser/releases/latest").url != f"https://github.com/diquoks/osu-parser/releases/tag/{program_version}":
        program_version = f"{program_version}\n(Доступно обновление!)"
        main_menu_program_version_label.config(text=program_version)
        main_menu_program_version_label.bind("<Button-1>", lambda i: webbrowser.open_new("https://github.com/diquoks/osu-parser/releases/latest"))

# Функции osu.py
def get_profile(client_id, client_secret, player_id, osu_mode):
    try:
        return osu.Client.from_credentials(client_id=client_id, client_secret=client_secret, redirect_url=None).get_user(user=player_id, mode=osu_mode)
    except Exception as e:
        if "not found" not in str(e).lower():
            print("\nПовтор get_profile()") # Для отладки
            return get_profile(client_id, client_secret, player_id, osu_mode)
        else:
            return None

def get_beatmap(client_id, client_secret, beatmap_id):
    try:
        return osu.Client.from_credentials(client_id=client_id, client_secret=client_secret, redirect_url=None).get_beatmap(beatmap=beatmap_id)
    except:
        print("\nПовтор get_beatmap()") # Для отладки
        return get_beatmap(client_id, client_secret, beatmap_id)

def get_beatmap_attributes(client_id, client_secret, beatmap_id, osu_mode):
    try:
        return osu.Client.from_credentials(client_id=client_id, client_secret=client_secret, redirect_url=None).get_beatmap_attributes(beatmap=beatmap_id, ruleset=osu_mode)
    except:
        print("\nПовтор get_beatmap_attributes()") # Для отладки
        return get_beatmap_attributes(client_id, client_secret, beatmap_id, osu_mode)

def get_score(client_id, client_secret, score_id):
    try:
        return osu.Client.from_credentials(client_id=client_id, client_secret=client_secret, redirect_url=None).get_score_by_id_only(score_id=score_id)
    except Exception as e:
        if "couldn't be found" not in str(e).lower() and "invalid" not in str(e).lower():
            print("\nПовтор get_score()") # Для отладки
            return get_score(client_id, client_secret, score_id)
        else:
            return None

def get_last_score(client_id, client_secret, player_id, osu_mode):
    try:
        return osu.Client.from_credentials(client_id=client_id, client_secret=client_secret, redirect_url=None).get_user_scores(user=player_id, mode=osu_mode, type=osu.UserScoreType.RECENT, include_fails=bool(include_fails.get()), limit=1)[0]
    except IndexError:
        return None
    except:
        print("\nПовтор get_last_score()") # Для отладки
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
        print("\nПовтор get_score_weight()") # Для отладки
        return get_score_weight(client_id, client_secret, player_id, score_id, osu_mode)

# Функции tkinter
def window_closed():
    try:
        winreg.SetValueEx(registry_path_previous, "window_position", 0, winreg.REG_SZ, f"{[root.geometry(), root.state()]}")
    finally:
        root.destroy()

def open_settings():
    global main_menu, settings
    main_menu.pack_forget()
    settings.pack(fill=BOTH, expand=True)

def save_settings():
    global client_id, client_secret, settings_app_id_entry, settings_app_secret_entry
    try:
        if winreg.QueryValueEx(registry_path_application, "client_id")[0] == str(settings_app_id_entry.get()) and winreg.QueryValueEx(registry_path_application, "client_secret")[0] == settings_app_secret_entry.get():
            tkinter.messagebox.showinfo(title="osu!parser", message="Настройки уже используются!")
        else:
            raise Exception
    except:
        try:
            client_id = int(settings_app_id_entry.get())
        except:
            tkinter.messagebox.showinfo(title="osu!parser", message="ID приложения должен быть числом!")
        else:
            client_secret = settings_app_secret_entry.get()
            winreg.SetValueEx(registry_path_application, "client_id", 0, winreg.REG_SZ, str(client_id))
            winreg.SetValueEx(registry_path_application, "client_secret", 0, winreg.REG_SZ, client_secret)
            tkinter.messagebox.showinfo(title="osu!parser", message="Настройки сохранены!")

def open_additional_settings():
    global additional_window, additional_osu_path_label, root
    (additional_window := Toplevel(root)).focus_force()
    additional_window.grab_set()
    additional_window.resizable(width=False, height=False)
    additional_window.geometry(f"{str(int(350*ui_scale))}x{str(int(200*ui_scale))}+{int(root.geometry().split("+")[1]) + 30}+{int(root.geometry().split("+")[2]) + 60}")
    additional_window.iconbitmap(resource_path("assets/icons/window_icon.ico"))
    additional_window.title("настройки osu!parser")
    additional_window.attributes("-topmost", True)
    additional_window.protocol("WM_DELETE_WINDOW", close_additional_settings)
    # Дополнительные настройки
    additional_settings = ttk.Frame(additional_window)
    (additional_settings_frame := ttk.Frame(additional_settings)).pack(fill=BOTH, expand=True, side=TOP)
    (additional_parsing_settings_frame := ttk.LabelFrame(additional_settings_frame, text="Настройки парсинга")).pack(side=LEFT, anchor=NW, padx=(10, 4), pady=5)
    (additional_program_settings_frame := ttk.LabelFrame(additional_settings_frame, text="Настройки программы")).pack(side=RIGHT, anchor=NE, padx=(4, 10), pady=5)
    (additional_ignore_classic_switch := ttk.Checkbutton(additional_parsing_settings_frame, text="Игнорировать Classic", variable=ignore_classic, command=ignore_classic_switched)).pack(side=TOP, anchor=NW, padx=5, pady=5)
    (additional_include_fails_switch := ttk.Checkbutton(additional_parsing_settings_frame, text="Учитывать фейлы", variable=include_fails, command=include_fails_switched)).pack(side=TOP, anchor=NW, padx=5, pady=5)
    (additional_recalculations_switch := ttk.Checkbutton(additional_parsing_settings_frame, text="Расчёт pp за FC и SS", variable=recalculations, command=recalculations_switched)).pack(side=TOP, anchor=NW, padx=5, pady=5)
    (additional_autoscaling_switch := ttk.Checkbutton(additional_program_settings_frame, text="Автомасштабирование", variable=autoscaling, command=autoscaling_switched)).pack(side=TOP, anchor=NW, padx=5, pady=5)
    (additional_topmost_switch := ttk.Checkbutton(additional_program_settings_frame, text="Поверх других окон", variable=topmost, command=topmost_switched)).pack(side=TOP, anchor=NW, padx=5, pady=5)
    (additional_osu_path_label := ttk.Label(additional_settings, text=osu_path)).pack(side=TOP, anchor=SW, padx=10)
    if osu_path not in ["Поиск директории osu!...", "Директория osu! не найдена!"]:
        additional_osu_path_label.bind("<Button-1>", lambda i: os.system(f"explorer.exe {osu_path}"))
    (additional_osu_path_button := ttk.Button(additional_settings, text="Выбрать папку osu!", command=osu_path_select, width=20)).pack(fill=X, side=LEFT, anchor=SW, padx=10, pady=10)
    (additional_auto_get_osu_path_button := ttk.Button(additional_settings, text="Автопоиск", command=lambda: threading.Thread(target=auto_get_osu_path, daemon=True).start(), width=5)).pack(fill=X, expand=True, side=LEFT, anchor=SW, pady=10)
    (additional_close_button := ttk.Button(additional_settings, text="Закрыть", command=close_additional_settings, width=15)).pack(side=RIGHT, anchor=SE, padx=10, pady=10)
    # Отрисовка дополнительных настроек
    additional_settings.pack(fill=BOTH, expand=True)
    additional_window.mainloop()

def ignore_classic_switched():
    global ignore_classic
    winreg.SetValueEx(registry_path_settings, "ignore_classic", 0, winreg.REG_SZ, str(ignore_classic.get()))

def include_fails_switched():
    global include_fails
    winreg.SetValueEx(registry_path_settings, "include_fails", 0, winreg.REG_SZ, str(include_fails.get()))

def recalculations_switched():
    global recalculations
    winreg.SetValueEx(registry_path_settings, "recalculations", 0, winreg.REG_SZ, str(recalculations.get()))

def autoscaling_switched():
    global autoscaling
    winreg.SetValueEx(registry_path_settings, "autoscaling", 0, winreg.REG_SZ, str(autoscaling.get()))

def topmost_switched():
    global additional_window, topmost
    root.attributes("-topmost", bool(topmost.get()))
    additional_window.attributes("-topmost", True)
    winreg.SetValueEx(registry_path_settings, "topmost", 0, winreg.REG_SZ, str(topmost.get()))

def osu_path_select():
    global additional_window, additional_osu_path_label, osu_path
    additional_window.focus()
    if (selected_path := filedialog.askdirectory(parent=additional_window, title="Выбор директории osu!", initialdir=osu_path, mustexist=True) .replace("/", "\\")) != "":
        osu_path = selected_path
        winreg.SetValueEx(registry_path_settings, "osu_path", 0, winreg.REG_SZ, osu_path)
    additional_osu_path_label.config(text=osu_path)

def auto_get_osu_path():
    global osu_path, additional_window, settings_credits_label, main_menu_settings_button, settings_additional_button
    additional_window.focus()
    drives = []
    songs_directory = []
    executable_directory = []
    osu_path = "Поиск директории osu!..."
    additional_osu_path_label.config(text=osu_path)
    additional_osu_path_label.unbind("<Button-1>")
    settings_credits_label.pack(expand=True, side=LEFT, padx=(0, 30))
    main_menu_settings_button.configure(text="Настройки (!)")
    settings_additional_button.configure(text="Дополнительно (!)", width=20)
    for i in string.ascii_uppercase:
        if os.path.isdir(i + ":"):
            drives.append(i)
    for i in drives:
        for j in glob.glob(f"{i}:\\**\\osu!\\Songs", recursive=True):
            if "Application Data" not in j and "Local Settings" not in j:
                songs_directory.append(re.sub("\\\\Songs$", "", j))
        for j in glob.glob(f"{i}:\\**\\osu!\\osu!.exe", recursive=True):
            if "Application Data" not in j and "Local Settings" not in j:
                executable_directory.append(re.sub("\\\\osu!.exe$", "", j))
    for j in songs_directory:
        for k in executable_directory:
            if songs_directory == executable_directory:
                osu_path = j
                winreg.SetValueEx(registry_path_settings, "osu_path", 0, winreg.REG_SZ, osu_path)
                if bool(additional_window.winfo_exists()):
                    additional_osu_path_label.config(text=osu_path)
                    additional_osu_path_label.bind("<Button-1>", lambda i: os.system(f"explorer.exe {osu_path}"))
                settings_credits_label.pack(expand=True, side=LEFT, padx=0)
                settings_additional_button.configure(text="Дополнительно", width=15)
                break
            else:
                osu_path = "Директория osu! не найдена!"
                if bool(additional_window.winfo_exists()):
                    winreg.SetValueEx(registry_path_settings, "osu_path", 0, winreg.REG_SZ, osu_path)
                    additional_osu_path_label.config(text=osu_path)
                additional_osu_path_label.unbind("<Button-1>")
    settings_credits_label.pack(expand=True, side=LEFT, padx=0)
    main_menu_settings_button.configure(text="Настройки")
    settings_additional_button.configure(text="Дополнительно", width=15)

def close_additional_settings():
    additional_window.destroy()
    settings.focus()

def close_settings():
    global main_menu, settings
    settings.pack_forget()
    main_menu.pack(fill=BOTH, expand=True)

def open_last_score():
    global main_menu, last_score
    main_menu.pack_forget()
    last_score.pack(fill=BOTH, expand=True)

def get_osu_mode(combobox_value):
    osu_mode = {"osu!": osu.GameModeStr.STANDARD.value,
                "osu!taiko": osu.GameModeStr.TAIKO.value,
                "osu!catch": osu.GameModeStr.CATCH.value,
                "osu!mania": osu.GameModeStr.MANIA.value}[combobox_value]
    return osu_mode

def last_score_parsing(client_id, client_secret, player_id, osu_mode):
    global recalculation, last_score_parsing_status, last_score_update_label, last_score_progressbar, last_score_start_button, last_score_stop_button
    winreg.SetValueEx(registry_path_previous, "player_id", 0, winreg.REG_SZ, str(player_id))
    winreg.SetValueEx(registry_path_previous, "osu_mode", 0, winreg.REG_SZ, osu_mode)
    main_menu_last_score_button.configure(text="Парсинг рекордов (!)")
    last_score_player_label.config(text="Поиск игрока...")
    last_score_update_label.config(text="Обновление...")
    last_score_progressbar.config(value=30)
    if (player := get_profile(client_id, client_secret, player_id, osu_mode)) is not None:
        previous_settings = [bool(ignore_classic.get()), bool(include_fails.get()), bool(recalculations.get()), bool(autoscaling.get()), osu_path]
        previous_score = [player.statistics.pp, None, 0]
        last_score_player_label.config(text=f"{player.username} (#{player.rank_history.data[-1]})")
        last_score_player_label.bind("<Button-1>", lambda i: webbrowser.open_new(f"https://osu.ppy.sh/users/{player.id}/{osu_mode}"))
    else:
        last_score_progressbar.config(mode="determinate")
        last_score_update_label.config(text="")
        last_score_player_label.config(text="Игрок не найден!")
        last_score_parsing_status = False
    while last_score_parsing_status:
        if last_score_parsing_status:
            last_score_update_label.config(text="Обновление...")
            last_score_progressbar.config(value=30)
            if (score := get_last_score(client_id, client_secret, player_id, osu_mode)) is not None:
                if previous_score[1] != score.id or previous_settings != [bool(ignore_classic.get()), bool(include_fails.get()), bool(recalculations.get()), bool(autoscaling.get()), osu_path]:
                    weight = get_score_weight(client_id, client_secret, player_id, score.id, osu_mode)
                    if last_score_parsing_status:
                        last_score_progressbar.config(value=45)
                        player = get_profile(client_id, client_secret, player_id, osu_mode)
                        previous_settings = [bool(ignore_classic.get()), bool(include_fails.get()), bool(recalculations.get()), bool(autoscaling.get()), osu_path]
                        previous_score = [player.statistics.pp, score.id, player.statistics.pp - previous_score[0]]
                    if last_score_parsing_status:
                        last_score_progressbar.config(value=60)
                        beatmap = get_beatmap(client_id, client_secret, score.beatmap_id)
                        beatmap_attributes = get_beatmap_attributes(client_id, client_secret, score.beatmap_id, osu_mode)
                        mods_list = [getattr(score.mods[i].mod, "value") for i in range(len(score.mods))]
                        recalculation = ", Расчёт pp недоступен!"
                    # Перерасчёт pp
                    if last_score_parsing_status and bool(recalculations.get()) and osu_path not in ["Поиск директории osu!...", "Директория osu! не найдена!"]:
                        beatmap_path = ""
                        lazer_score = "CL" not in mods_list
                        try:
                            for i in ["\\", "/", ":", "*", "?", "\"", "<", ">", "|"]:
                                beatmap.version = beatmap.version.replace(i, "")
                            beatmap_path = glob.glob(f"{osu_path}\\Songs\\{beatmap.beatmapset_id}*/*{beatmap.version}].osu", recursive=True)[0]
                        except IndexError:
                            print(f"\nКарта не найдена, расчёт pp невозможен!\nДля расчёта pp загрузите карту по ссылке:\nhttps://osu.ppy.sh/beatmapsets/{beatmap.beatmapset_id}") # Позже будет отображаться в новом элементе GUI
                        except:
                            print(f"\n{traceback.format_exc()}") # Для отладки
                        else:
                            selected_beatmap = rosu.Beatmap(path=beatmap_path)
                            if osu_mode == osu.GameModeStr.STANDARD.value:
                                recalculated_fc = round(rosu.Performance(mods="".join(mods_list), n100=score.statistics.ok, n50=score.statistics.meh, lazer=lazer_score).calculate(selected_beatmap).pp, 2)
                                recalculated_ss = round(rosu.Performance(mods="".join(mods_list), lazer=lazer_score).calculate(selected_beatmap).pp, 2)
                            elif osu_mode == osu.GameModeStr.TAIKO.value:
                                selected_beatmap.convert(mode=rosu.GameMode.Taiko, mods="".join(mods_list))
                                recalculated_fc = round(rosu.Performance(mods="".join(mods_list), n100=score.statistics.ok, lazer=lazer_score).calculate(selected_beatmap).pp, 2)
                                recalculated_ss = round(rosu.Performance(mods="".join(mods_list), lazer=lazer_score).calculate(selected_beatmap).pp, 2)
                            elif osu_mode == osu.GameModeStr.CATCH.value:
                                selected_beatmap.convert(mode=rosu.GameMode.Catch, mods="".join(mods_list))
                                recalculated_fc = round(rosu.Performance(mods="".join(mods_list), n100=score.statistics.large_tick_hit, n50=score.statistics.small_tick_hit, lazer=lazer_score).calculate(selected_beatmap).pp, 2)
                                recalculated_ss = round(rosu.Performance(mods="".join(mods_list), lazer=lazer_score).calculate(selected_beatmap).pp, 2)
                            elif osu_mode == osu.GameModeStr.MANIA.value:
                                selected_beatmap.convert(mode=rosu.GameMode.Mania, mods="".join(mods_list))
                                recalculated_fc = round(rosu.Performance(mods="".join(mods_list), n300=score.statistics.great, n_katu=score.statistics.good, n100=score.statistics.ok, n50=score.statistics.meh, lazer=lazer_score).calculate(selected_beatmap).pp, 2)
                                recalculated_ss = round(rosu.Performance(mods="".join(mods_list), lazer=lazer_score).calculate(selected_beatmap).pp, 2)
                            if score.max_combo < beatmap_attributes.max_combo and recalculated_fc != recalculated_ss:
                                recalculation = f", FC: {recalculated_fc}pp, SS: {recalculated_ss}pp"
                            elif (score.statistics.great != score.maximum_statistics.great) if beatmap_attributes.type.value == osu_mode != osu.GameModeStr.MANIA.value else (score.statistics.perfect != score.maximum_statistics.perfect):
                                print(f"\nОжидаемый перерасчёт: FC: {recalculated_fc}pp") # Для отладки
                                recalculation = f", SS: {recalculated_ss}pp"
                            else:
                                print(f"\nОжидаемый перерасчёт: FC: {recalculated_fc}pp, SS: {recalculated_ss}pp") # Для отладки
                                recalculation = f", {score.rank.name.replace("SILVER_SS", "SS+").replace("SILVER_S", "SS+").replace("S", "SS")}!"
                    if last_score_parsing_status:
                        if bool(autoscaling.get()):
                            root.geometry("")
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
                            last_score_scores_label.config(text=f"300: {score.statistics.great}/{score.maximum_statistics.great}, 100: {score.statistics.ok}, 50: {score.statistics.meh}, Miss: {score.statistics.miss}{f", {"PASSED" if score.passed else "FAILED"}" if bool(include_fails.get()) else ""}".replace("None", "0"))
                        elif osu_mode == osu.GameModeStr.TAIKO.value:
                            last_score_scores_label.config(text=f"300: {score.statistics.great}/{score.maximum_statistics.great}, 100: {score.statistics.ok}, Miss: {score.statistics.miss}{f", {"PASSED" if score.passed else "FAILED"}" if bool(include_fails.get()) else ""}".replace("None", "0"))
                        elif osu_mode == osu.GameModeStr.CATCH.value:
                            last_score_scores_label.config(text=f"Fruits: {score.statistics.great}/{score.maximum_statistics.great}, Ticks: {score.statistics.large_tick_hit}/{score.maximum_statistics.large_tick_hit}, Droplets: {score.statistics.small_tick_hit}/{score.maximum_statistics.small_tick_hit}{f", {"PASSED" if score.passed else "FAILED"}" if bool(include_fails.get()) else ""}".replace("None", "0"))
                        elif osu_mode == osu.GameModeStr.MANIA.value:
                            last_score_scores_label.config(text=f"Max: {score.statistics.perfect}/{score.maximum_statistics.perfect}, 300: {score.statistics.great}, 200: {score.statistics.good}".replace("None", "0"))
                            last_score_scores_additional_label.config(text=f"100: {score.statistics.ok}, 50: {score.statistics.meh}, Miss: {score.statistics.miss}{f", {"PASSED" if score.passed else "FAILED"}" if bool(include_fails.get()) else ""}".replace("None", "0"))
                else:
                    last_score_progressbar.config(value=60)
                    time.sleep(0.5)
                    if bool(autoscaling.get()):
                        root.geometry("")
            else:
                last_score_progressbar.config(value=60)
                player = get_profile(client_id, client_secret, player_id, osu_mode)
                root.geometry("")
                try:
                    last_score_player_label.config(text=f"{player.username} (#{player.rank_history.data[-1]})")
                except:
                    last_score_player_label.config(text=f"{player.username} (#???)")
                last_score_player_label.bind("<Button-1>", lambda i: webbrowser.open_new(f"https://osu.ppy.sh/users/{player.id}/{osu_mode}"))
                last_score_link_label.config(text="Последний рекорд отсутствует!")
                last_score_link_label.unbind("<Button-1>")
            fastmode_current = bool(fastmode.get())
            for i in range(3 if fastmode_current else 15, -1, -1):
                if last_score_parsing_status:
                    last_score_progressbar.config(value=(15 - (i * 5 if fastmode_current else i)))
                    if i == 0:
                        last_score_update_label.config(text=f"Обновление...")
                    else:
                        last_score_update_label.config(text=f"Обновление через: {i}")
                    time.sleep(1)
    main_menu_last_score_button.configure(text="Парсинг рекордов")
    last_score_update_label.config(text="")
    last_score_progressbar.config(value=0)
    last_score_link_label.config(text="")
    last_score_link_label.unbind("<Button-1>")
    last_score_map_label.config(text="")
    last_score_diff_label.config(text="")
    last_score_pp_label.config(text="")
    last_score_mods_label.config(text="")
    last_score_grades_label.config(text="")
    last_score_scores_label.config(text="")
    last_score_scores_additional_label.config(text="")
    last_score_start_button.config(state=ACTIVE)
    last_score_stop_button.config(state=DISABLED)
    last_score_stop_button.pack_forget()
    last_score_start_button.pack(side=TOP, anchor=CENTER, padx=8, pady=7)

def last_score_parsing_start():
    global last_score_parsing_status, client_id, client_secret, last_score_parsing_thread, last_score_start_button, last_score_stop_button
    last_score_parsing_status = True
    try:
        player_id = int(last_score_player_id_entry.get())
    except:
        tkinter.messagebox.showinfo(title="osu!parser", message="ID игрока должен быть числом!")
    else:
        try:
            (last_score_parsing_thread := threading.Thread(target=last_score_parsing, args=(client_id, client_secret, player_id, get_osu_mode(last_score_osu_mode_combobox.get())), daemon=True)).start()
        except:
            tkinter.messagebox.showinfo(title="osu!parser", message="Сначала заполните все поля!")
        else:
            last_score_start_button.config(state=DISABLED)
            last_score_start_button.pack_forget()
            last_score_stop_button.config(state=ACTIVE)
            last_score_stop_button.pack(side=TOP, anchor=CENTER, padx=8, pady=7)

def last_score_parsing_stop():
    global last_score_parsing_status, last_score_parsing_thread
    last_score.focus()
    last_score_parsing_status = False
    last_score_progressbar.config(mode="indeterminate")
    last_score_progressbar.start()
    last_score_parsing_thread.join()
    last_score_player_label.config(text="")
    last_score_player_label.unbind("<Button-1>")
    last_score_progressbar.config(mode="determinate")
    last_score_progressbar.stop()

def fastmode_switched():
    global fastmode
    winreg.SetValueEx(registry_path_settings, "fastmode", 0, winreg.REG_SZ, str(fastmode.get()))

def close_last_score():
    global main_menu, last_score
    last_score.pack_forget()
    main_menu.pack(fill=BOTH, expand=True)

def open_text_parsing():
    global main_menu, main_menu_text_parsing_button, text_parsing
    main_menu.pack_forget()
    main_menu_text_parsing_button.config(text="Текстовый парсинг")
    text_parsing.pack(fill=BOTH, expand=True)

def text_parsing_mode_selected():
    global text_parsing_osu_mode_combobox, text_parsing_mode, text_parsing_id_border, text_parsing_id_entry
    text_parsing_osu_mode_combobox.config(state="readonly" if text_parsing_mode.get() == 0 else DISABLED if text_parsing_mode.get() == 1 else ACTIVE)
    text_parsing_id_border.config(text=f"ID{" игрока" if text_parsing_mode.get() == 0 else " рекорда" if text_parsing_mode.get() == 1 else ""}:")
    try:
        winreg.SetValueEx(registry_path_previous, "text_parsing_profile_id" if text_parsing_mode.get() == 1 else "text_parsing_score_id", 0, winreg.REG_SZ, str(text_parsing_id_entry.get()))
        text_parsing_id_entry.delete(0, END)
        text_parsing_id_entry.insert(END, winreg.QueryValueEx(registry_path_previous, "text_parsing_profile_id" if text_parsing_mode.get() == 0 else "text_parsing_score_id")[0])
    except:
        winreg.SetValueEx(registry_path_previous, "text_parsing_profile_id" if text_parsing_mode.get() == 1 else "text_parsing_score_id", 0, winreg.REG_SZ, str(text_parsing_id_entry.get()))
        text_parsing_id_entry.delete(0, END)
    winreg.SetValueEx(registry_path_settings, "text_parsing", 0, winreg.REG_SZ, str(text_parsing_mode.get()))

def text_parsing_thread(client_id, client_secret, object_id):
    global text_parsing_mode, text_parsing_path, text_parsing_save_button, text_parsing_status_label, text_parsing, empty_values, main_menu_text_parsing_button
    winreg.SetValueEx(registry_path_previous, "text_parsing_profile_id" if text_parsing_mode.get() == 0 else "text_parsing_score_id", 0, winreg.REG_SZ, str(object_id))
    blank_values = ""
    try:
        if text_parsing_mode.get() == 0:
            profile = get_profile(client_id, client_secret, object_id, get_osu_mode(text_parsing_osu_mode_combobox.get()))
            winreg.SetValueEx(registry_path_previous, "osu_mode", 0, winreg.REG_SZ, get_osu_mode(text_parsing_osu_mode_combobox.get()))
            filepath = f"{text_parsing_path}\\osu! профиль {profile.username} ({object_id}).txt"
            with open(filepath, "w") as file:
                file.write(f"({datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")})\nИнформация об игроке {profile.username} ({object_id}):\n")
                for i in list(filter(lambda i: "__" not in i, dir(profile))):
                    if getattr(profile, i) is not None:
                        if "<class 'osu.objects." in str(type(getattr(profile, i))):
                            file.write(f"\n{i}:")
                            blank_values += f"\n{i}:"
                            try:
                                for j in list(filter(lambda i: "__" not in i, dir(getattr(profile, i)))):
                                    if getattr(getattr(profile, i), j) is not None:
                                        if "<class 'osu.objects." not in str(type(getattr(getattr(profile, i), j))):
                                            file.write(f"\n    {j}: {getattr(getattr(profile, i), j)}")
                                    else:
                                        blank_values += f"\n    {j}: {getattr(getattr(profile, i), j)}"
                            except:
                                file.write("\n")
                        else:
                            file.write(f"\n{i}: {getattr(profile, i)}")
                    else:
                        blank_values += f"\n{i}: {getattr(profile, i)}"
                if bool(empty_values.get()):
                    file.write(f"\n\n\nПустые значения:\n\n{blank_values}")
        elif text_parsing_mode.get() == 1:
            score = get_score(client_id, client_secret, object_id)
            filepath = f"{text_parsing_path}\\osu! рекорд {score.user.username} - {int(round(score.pp, 0))}pp на {score.beatmapset.title} ({object_id}).txt"
            with open(filepath, "w") as file:
                file.write(f"({datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")})\nИнформация о рекорде {score.user.username} - {score.pp}pp ({int(round(score.pp, 0))}pp) на {score.beatmapset.creator} - {score.beatmapset.title} от {score.beatmapset.artist} ({score.beatmap.version}, {score.beatmap.difficulty_rating}*, {score.beatmap.ranked.name}) ({object_id}):\n")
                for i in list(filter(lambda i: "__" not in i, dir(score))):
                    if getattr(score, i) is not None:
                        if "<class 'osu.objects." in str(type(getattr(score, i))):
                            file.write(f"\n{i}:")
                            blank_values += f"\n{i}:"
                            try:
                                for j in list(filter(lambda i: "__" not in i, dir(getattr(score, i)))):
                                    if getattr(getattr(score, i), j) is not None:
                                        if "<class 'osu.objects." not in str(type(getattr(getattr(score, i), j))):
                                            file.write(f"\n    {j}: {getattr(getattr(score, i), j)}")
                                    else:
                                        blank_values += f"\n    {j}: {getattr(getattr(score, i), j)}"
                            except:
                                file.write("\n")
                        else:
                            file.write(f"\n{i}: {getattr(score, i)}")
                    else:
                        blank_values += f"\n{i}: {getattr(score, i)}"
                if bool(empty_values.get()):
                    file.write(f"\n\n\nПустые значения:\n\n{blank_values}")
    except:
        if text_parsing_mode.get() == 0:
            if profile is None:
                text_parsing_status_label.config(text="Игрок отсутствует!")
        elif text_parsing_mode.get() == 1:
            if score is None:
                text_parsing_status_label.config(text="Рекорд отсутствует!")
        else:
            print(traceback.format_exc()) # Для отладки
            text_parsing_status_label.config(text="Возникла ошибка!")
            os.remove(filepath)
    else:
        text_parsing_status_label.config(text="Сохранено!")
    try:
        text_parsing.pack_info()
    except:
        main_menu_text_parsing_button.config(text="Текстовый парсинг (!)")
    text_parsing_save_button.config(state=ACTIVE)

def text_parsing_save():
    global text_parsing, text_parsing_id_entry, client_id, client_secret
    text_parsing.focus()
    try:
        object_id = int(text_parsing_id_entry.get())
    except:
        tkinter.messagebox.showinfo(title="osu!parser", message=f"ID{" игрока" if text_parsing_mode.get() == 0 else " рекорда" if text_parsing_mode.get() == 1 else ""} должен быть числом!")
    else:
        try:
            threading.Thread(target=text_parsing_thread, args=(client_id, client_secret, object_id), daemon=True).start()
        except:
            tkinter.messagebox.showinfo(title="osu!parser", message="Сначала заполните все поля!")
        else:
            text_parsing_save_button.config(state=DISABLED)
            text_parsing_status_label.config(text="Сохранение...")

def empty_values_switched():
    global empty_values, text_parsing_id_border
    winreg.SetValueEx(registry_path_settings, "empty_values", 0, winreg.REG_SZ, str(empty_values.get()))

def text_parsing_path_select():
    global text_parsing, root, text_parsing_path_label, text_parsing_path
    text_parsing.focus()
    if (selected_path := filedialog.askdirectory(parent=root, title="Выбор директории osu!", initialdir=text_parsing_path, mustexist=True) .replace("/", "\\")) != "":
        text_parsing_path = selected_path
        winreg.SetValueEx(registry_path_settings, "text_parsing_path", 0, winreg.REG_SZ, text_parsing_path)
    text_parsing_path_label.config(text=text_parsing_path)

def close_text_parsing():
    global text_parsing_status_label, text_parsing, main_menu
    text_parsing_status_label.config(text="")
    text_parsing.pack_forget()
    main_menu.pack(fill=BOTH, expand=True)

# Создание окна
root = Tk()
# Объявление переменных tkinter
try:
    window_position = ast.literal_eval(winreg.QueryValueEx(registry_path_previous, "window_position")[0])
except:
    window_position = [f"{str(int(550 * ui_scale))}x{str(int(300 * ui_scale))}", "normal"]

ignore_classic = IntVar()
try:
    ignore_classic.set(int(winreg.QueryValueEx(registry_path_settings, "ignore_classic")[0]))
except:
    ignore_classic.set(1)

include_fails = IntVar()
try:
    include_fails.set(int(winreg.QueryValueEx(registry_path_settings, "include_fails")[0]))
except:
    include_fails.set(0)

recalculations = IntVar()
try:
    recalculations.set(int(winreg.QueryValueEx(registry_path_settings, "recalculations")[0]))
except:
    recalculations.set(1)

autoscaling = IntVar()
try:
    autoscaling.set(int(winreg.QueryValueEx(registry_path_settings, "autoscaling")[0]))
except:
    autoscaling.set(1)

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

text_parsing_mode = IntVar()
try:
    text_parsing_mode.set(int(winreg.QueryValueEx(registry_path_settings, "text_parsing")[0]))
except:
    text_parsing_mode.set(0)

empty_values = IntVar()
try:
    empty_values.set(int(winreg.QueryValueEx(registry_path_settings, "empty_values")[0]))
except:
    empty_values.set(1)
# Параметры окна
root.geometry(window_position[0])
root.state(window_position[1])
root.minsize(int(550 * ui_scale), int(300 * ui_scale))
root.resizable(width=True, height=True)
root.iconbitmap(resource_path("assets/icons/window_icon.ico"))
root.title("osu!parser")
root.attributes("-topmost", bool(topmost.get()))
root.protocol("WM_DELETE_WINDOW", window_closed)
# Главное меню
main_menu = ttk.Frame(root)
(main_menu_title := ttk.Label(main_menu, text="osu!parser")).pack(side=TOP, anchor=CENTER, pady=2)
(main_menu_last_score_button := ttk.Button(main_menu, text="Парсинг рекордов", command=open_last_score, width=25)).pack(side=TOP, anchor=CENTER, pady=(40, 30))
(main_menu_recalculation_button := ttk.Button(main_menu, text="Калькулятор pp", command=lambda: tkinter.messagebox.showinfo(title="osu!parser", message="Будет доступно в версии 1.2!"), width=25)).pack(side=TOP, anchor=CENTER, pady=10)
(main_menu_text_parsing_button := ttk.Button(main_menu, text="Текстовый парсинг", command=open_text_parsing, width=25)).pack(side=TOP, anchor=CENTER, pady=10)
(main_menu_bottom_frame := ttk.Frame(main_menu)).pack(fill=BOTH, side=BOTTOM)
(main_menu_language_button := ttk.Button(main_menu_bottom_frame, text="Язык / Language", command=lambda: tkinter.messagebox.showinfo(title="osu!parser", message="Будет доступно в версии 1.4!\nWill be available in version 1.4!"), width=15)).pack(side=LEFT, anchor=SW, padx=10, pady=10)
(main_menu_program_version_label := ttk.Label(main_menu_bottom_frame, text=program_version, justify=CENTER)).pack(expand=True, side=LEFT)
main_menu_program_version_label.bind("<Button-1>", lambda i: webbrowser.open_new("https://github.com/diquoks/osu-parser/releases"))
(main_menu_settings_button := ttk.Button(main_menu_bottom_frame, text="Настройки", command=open_settings, width=15)).pack(side=RIGHT, anchor=SE, padx=10, pady=10)
# Настройки
settings = ttk.Frame(root)
(settings_title := ttk.Label(settings, text="настройки osu!parser")).pack(side=TOP, anchor=CENTER, pady=2)
(settings_app_settings_border := ttk.LabelFrame(settings)).pack(side=TOP, anchor=CENTER, pady=(35, 10))
(settings_app_id_border := ttk.LabelFrame(settings_app_settings_border, text="ID:")).pack(side=LEFT, anchor=NW, padx=10, pady=8)
(settings_app_id_entry := ttk.Entry(settings_app_id_border, width=7)).pack(side=LEFT, anchor=NW, padx=7, pady=5)
(settings_app_secret_border := ttk.LabelFrame(settings_app_settings_border, text="Секретный ключ приложения:")).pack(side=LEFT, anchor=NW, pady=8)
(settings_app_secret_entry := ttk.Entry(settings_app_secret_border, width=49)).pack(side=LEFT, anchor=NW, padx=7, pady=5)
(settings_app_settings_save_button := ttk.Button(settings_app_settings_border, text="ОК", command=save_settings, width=5)).pack(side=LEFT, anchor=NW, padx=7, pady=15, ipady=7)
(settings_app_settings_setup_label_link := ttk.Label(settings, text="Создайте своё приложение: https://osu.ppy.sh/home/account/edit#oauth")).pack(side=TOP, anchor=CENTER, pady=1)
settings_app_settings_setup_label_link.bind("<Button-1>", lambda i: webbrowser.open_new("https://osu.ppy.sh/home/account/edit#oauth"))
(settings_app_settings_setup_label_path := ttk.Label(settings, text="OAuth -> мои приложения -> новое приложение OAuth -> Зарегистрировать")).pack(side=TOP, anchor=CENTER)
(settings_bottom_frame := ttk.Frame(settings)).pack(fill=BOTH, side=BOTTOM)
(settings_additional_button := ttk.Button(settings_bottom_frame, text="Дополнительно", command=open_additional_settings, width=15)).pack(side=LEFT, anchor=SW, padx=10, pady=10)
(settings_help_button := ttk.Button(settings, text="Помощь", command=lambda: webbrowser.open_new("https://github.com/diquoks/osu-parser/blob/main/README.md"), width=15)).pack(side=BOTTOM, anchor=SW, padx=10)
(settings_credits_label := ttk.Label(settings_bottom_frame, text="Сделано diquoks ❤")).pack(expand=True, side=LEFT)
settings_credits_label.bind("<Button-1>", lambda i: webbrowser.open_new("https://diquoks.ru"))
(settings_close_button := ttk.Button(settings_bottom_frame, text="Назад", command=close_settings, width=15)).pack(side=RIGHT, anchor=SE, padx=10, pady=10)
# Последний рекорд
last_score = ttk.Frame(root)
(last_score_title := ttk.Label(last_score, text="osu!parser")).pack(side=TOP, anchor=CENTER, pady=2)
(last_score_settings_border := ttk.LabelFrame(last_score)).pack(fill=BOTH, side=LEFT, anchor=CENTER)
(last_score_player_id_frame := ttk.Frame(last_score_settings_border)).pack(fill=BOTH, side=TOP, anchor=NW, padx=10, pady=3)
(last_score_player_id_border := ttk.LabelFrame(last_score_player_id_frame, text="ID игрока:")).pack(fill=X, side=TOP, anchor=CENTER, pady=3)
(last_score_player_id_entry := ttk.Entry(last_score_player_id_border, width=17)).pack(padx=7, pady=5)
(last_score_osu_mode_border := ttk.LabelFrame(last_score_settings_border, text="Режим:")).pack(fill=X, side=TOP, anchor=CENTER, padx=10, pady=3)
(last_score_osu_mode_combobox := ttk.Combobox(last_score_osu_mode_border, values=["osu!", "osu!taiko", "osu!catch", "osu!mania"], state="readonly", width=14)).pack(expand=True, side=LEFT, padx=7, pady=5)
(last_score_progressbar_border := ttk.LabelFrame(last_score_settings_border, text="Прогресс:")).pack(side=TOP, anchor=CENTER, fill=X, padx=10, pady=3)
(last_score_progressbar := ttk.Progressbar(last_score_progressbar_border, orient="horizontal", maximum=60)).pack(fill=X, expand=True, side=TOP, anchor=CENTER, padx=8, pady=5)
(last_score_start_button := ttk.Button(last_score_settings_border, text="Запустить", command=last_score_parsing_start, width=20)).pack(side=TOP, anchor=CENTER, padx=8, pady=7)
last_score_stop_button = ttk.Button(last_score_settings_border, text="Остановить", command=lambda: threading.Thread(target=last_score_parsing_stop, daemon=True).start(), width=20)
(last_score_fastmode_switch := ttk.Checkbutton(last_score_settings_border, text="Быстрый режим", variable=fastmode, command=fastmode_switched)).pack(side=BOTTOM, anchor=CENTER, padx=10, pady=10)
(last_score_update_top_frame := ttk.Frame(last_score)).pack(fill=BOTH, side=TOP, pady=10)
(last_score_player_label := ttk.Label(last_score_update_top_frame)).pack(side=LEFT, anchor=NW, padx=10)
(last_score_update_label := ttk.Label(last_score_update_top_frame)).pack(side=RIGHT, anchor=NE, padx=16)
(last_score_link_label := ttk.Label(last_score)).pack(side=TOP, anchor=NW, padx=10, pady=2)
(last_score_map_label := ttk.Label(last_score)).pack(side=TOP, anchor=NW, padx=10, pady=2)
(last_score_diff_label := ttk.Label(last_score)).pack(side=TOP, anchor=NW, padx=10, pady=2)
(last_score_pp_label := ttk.Label(last_score)).pack(side=TOP, anchor=NW, padx=10, pady=2)
(last_score_mods_label := ttk.Label(last_score)).pack(side=TOP, anchor=NW, padx=10, pady=2)
(last_score_grades_label := ttk.Label(last_score)).pack(side=TOP, anchor=NW, padx=10, pady=2)
(last_score_scores_label := ttk.Label(last_score)).pack(side=TOP, anchor=NW, padx=10, pady=2)
(last_score_scores_additional_label := ttk.Label(last_score)).pack(side=TOP, anchor=NW, padx=10)
(last_score_bottom_frame := ttk.Frame(last_score)).pack(fill=X, side=BOTTOM)
(last_score_recalculate_button := ttk.Button(last_score_bottom_frame, text="Расчитать pp", command=lambda: tkinter.messagebox.showinfo(title="osu!parser", message="Будет доступно в версии 1.2!"), width=15)).pack(side=LEFT, anchor=SW, padx=10, pady=10)
(last_score_close_button := ttk.Button(last_score_bottom_frame, text="Назад", command=close_last_score, width=15)).pack(side=RIGHT, anchor=SE, padx=10, pady=10)
# Текстовый парсинг
text_parsing = ttk.Frame(root)
(text_parsing_title := ttk.Label(text_parsing, text="osu!parser")).pack(side=TOP, anchor=CENTER, pady=2)
(text_parsing_settings_border := ttk.LabelFrame(text_parsing)).pack(fill=BOTH, side=LEFT, anchor=CENTER)
(text_parsing_id_frame := ttk.Frame(text_parsing_settings_border)).pack(fill=BOTH, side=TOP, anchor=NW, padx=10, pady=3)
(text_parsing_id_border := ttk.LabelFrame(text_parsing_id_frame, text=f"ID{" игрока" if text_parsing_mode.get() == 0 else " рекорда" if text_parsing_mode.get() == 1 else ""}:")).pack(fill=X, side=TOP, anchor=CENTER, pady=3)
(text_parsing_id_entry := ttk.Entry(text_parsing_id_border, width=17)).pack(padx=7, pady=5)
(text_parsing_osu_mode_border := ttk.LabelFrame(text_parsing_settings_border, text="Режим:")).pack(side=TOP, anchor=CENTER, padx=10, pady=3)
(text_parsing_osu_mode_combobox := ttk.Combobox(text_parsing_osu_mode_border, values=["osu!", "osu!taiko", "osu!catch", "osu!mania"], state="readonly" if text_parsing_mode.get() == 0 else DISABLED if text_parsing_mode.get() == 1 else ACTIVE, width=14)).pack(side=TOP, anchor=NW, padx=7, pady=5)
(text_parsing_mode_border := ttk.LabelFrame(text_parsing_settings_border, text="Режим парсинга:")).pack(fill=X, side=TOP, anchor=CENTER, padx=10, pady=3)
(text_parsing_profile_switch := ttk.Radiobutton(text_parsing_mode_border, text="Профиль", value=0, command=text_parsing_mode_selected, variable=text_parsing_mode)).pack(side=TOP, anchor=NW, padx=8, pady=(5, 3))
(text_parsing_score_switch := ttk.Radiobutton(text_parsing_mode_border, text="Рекорд", value=1, command=text_parsing_mode_selected, variable=text_parsing_mode)).pack(side=TOP, anchor=NW, padx=8, pady=3)
(text_parsing_save_button := ttk.Button(text_parsing_settings_border, text="Сохранить", command=text_parsing_save, width=20)).pack(side=BOTTOM, anchor=CENTER, padx=8, pady=8)
(text_parsing_status_label := ttk.Label(text_parsing)).pack(side=TOP, anchor=NE, padx=10, pady=10)
(text_parsing_bottom_frame := ttk.Frame(text_parsing)).pack(fill=BOTH, side=BOTTOM)
(text_parsing_path_label := ttk.Label(text_parsing, text=text_parsing_path)).pack(side=BOTTOM, anchor=NW, padx=10)
text_parsing_path_label.bind("<Button-1>", lambda i: os.system(f"explorer.exe {text_parsing_path}"))
(text_parsing_path_select_button := ttk.Button(text_parsing_bottom_frame, text="Выбрать папку...", command=text_parsing_path_select, width=20)).pack(side=LEFT, anchor=SW, padx=10, pady=10)
(text_parsing_empty_values_switch := ttk.Checkbutton(text_parsing_bottom_frame, text="Пустые значения", variable=empty_values, command=empty_values_switched)).pack(fill=Y, expand=True, side=LEFT, anchor=CENTER, pady=10)
(text_parsing_close_button := ttk.Button(text_parsing_bottom_frame, text="Назад", command=close_text_parsing, width=15)).pack(side=RIGHT, anchor=SE, padx=10, pady=10)
# Подстановка значений и отрисовка главного меню
threading.Thread(target=program_version_status, daemon=True).start()
try:
    try:
        settings_app_id_entry.insert(END, (client_id := winreg.QueryValueEx(registry_path_application, "client_id")[0]))
    except:
        pass
    try:
        settings_app_secret_entry.insert(END, (client_secret := winreg.QueryValueEx(registry_path_application, "client_secret")[0]))
    except:
        pass
except:
    pass
try:
    try:
        last_score_osu_mode_combobox.current({osu.GameModeStr.STANDARD.value: osu.GameModeInt.STANDARD.value,
                                              osu.GameModeStr.TAIKO.value: osu.GameModeInt.TAIKO.value,
                                              osu.GameModeStr.CATCH.value: osu.GameModeInt.CATCH.value,
                                              osu.GameModeStr.MANIA.value: osu.GameModeInt.MANIA.value}[winreg.QueryValueEx(registry_path_previous, "osu_mode")[0]])
    except:
        pass
    try:
        last_score_player_id_entry.insert(END, winreg.QueryValueEx(registry_path_previous, "player_id")[0])
    except:
        pass
except:
    pass
try:
    try:
        text_parsing_osu_mode_combobox.current({osu.GameModeStr.STANDARD.value: osu.GameModeInt.STANDARD.value,
                                                osu.GameModeStr.TAIKO.value: osu.GameModeInt.TAIKO.value,
                                                osu.GameModeStr.CATCH.value: osu.GameModeInt.CATCH.value,
                                                osu.GameModeStr.MANIA.value: osu.GameModeInt.MANIA.value}[winreg.QueryValueEx(registry_path_previous, "osu_mode")[0]])
    except:
        pass
    try:
        text_parsing_id_entry.insert(END, winreg.QueryValueEx(registry_path_previous, "text_parsing_profile_id" if text_parsing_mode.get() == 0 else "text_parsing_score_id")[0])
    except:
        pass
except:
    pass
main_menu.pack(fill=BOTH, expand=True)
root.mainloop()