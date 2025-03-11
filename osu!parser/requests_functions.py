import webbrowser, traceback, threading, requests, datetime, tkinter, winreg, ctypes, string, time, glob, ast, osu, sys, re, os
import rosu_pp_py as rosu
from tkinter import messagebox, filedialog, ttk
from tkinter import *


# Функции osu.py
def get_osu_mode(value: str | int) -> str | None:
    """
    Возвращает значение из ``osu.GameModeStr``, принимает значение из ``ttk.Combobox`` или из ``osu.GameModeStr``.
    :param value: ``str`` или ``int``
    """
    if type(value) == str:
        osu_mode = {"osu!": osu.GameModeStr.STANDARD.value,
                    "osu!taiko": osu.GameModeStr.TAIKO.value,
                    "osu!catch": osu.GameModeStr.CATCH.value,
                    "osu!mania": osu.GameModeStr.MANIA.value}[value]
    elif type(value) == int:
        osu_mode = {osu.GameModeInt.STANDARD.value: osu.GameModeStr.STANDARD.value,
                    osu.GameModeInt.TAIKO.value: osu.GameModeStr.TAIKO.value,
                    osu.GameModeInt.CATCH.value: osu.GameModeStr.CATCH.value,
                    osu.GameModeInt.MANIA.value: osu.GameModeStr.MANIA.value}[value]
    else:
        osu_mode = None
    return osu_mode


def get_profile(client_id: int, client_secret: str, player_id: int, osu_mode: str) -> osu.User | None:
    """
    Возвращает профиль игрока, принимает данные приложения, ID игрока и нужный режим игры.
    :param client_id: ID приложения OAuth
    :param client_secret: Ключ приложения OAuth
    :param player_id: ID игрока
    :param osu_mode: Режим игры
    """
    try:
        return osu.Client.from_credentials(client_id=client_id, client_secret=client_secret, redirect_url=None).get_user(user=player_id, mode=osu_mode)
    except requests.exceptions.HTTPError:
        return None
    except:
        print(f"\n{traceback.format_exc()}\nПовтор get_profile()")  # Для отладки
        return get_profile(client_id, client_secret, player_id, osu_mode)


def get_score(client_id: int, client_secret: str, score_id: int) -> osu.SoloScore | None:
    """
    Возвращает информацию о рекорде, принимает данные приложения и ID рекорда.
    :param client_id: ID приложения OAuth
    :param client_secret: Ключ приложения OAuth
    :param score_id: ID рекорда
    """
    try:
        return osu.Client.from_credentials(client_id=client_id, client_secret=client_secret, redirect_url=None).get_score_by_id_only(score_id=score_id)
    except osu.exceptions.RequestException:
        return None
    except:
        print(f"\n{traceback.format_exc()}\nПовтор get_score()")  # Для отладки
        return get_score(client_id, client_secret, score_id)


def get_last_score(client_id: int, client_secret: str, player_id: int, osu_mode: str, include_fails: bool) -> osu.objects.SoloScore | None:
    """
    Возвращает информацию о последнем рекорде пользователя, принимает данные приложения, ID игрока и нужный режим игры.
    :param client_id: ID приложения OAuth
    :param client_secret: Ключ приложения OAuth
    :param player_id: ID игрока
    :param osu_mode: Режим игры
    :param include_fails: Значение одноимённой переменной
    """
    try:
        return osu.Client.from_credentials(client_id=client_id, client_secret=client_secret, redirect_url=None).get_user_scores(user=player_id, mode=osu_mode, type=osu.UserScoreType.RECENT, include_fails=include_fails, limit=1)[0]
    except (requests.exceptions.HTTPError, IndexError):
        return None
    except:
        print(f"\n{traceback.format_exc()}\nПовтор get_last_score()")  # Для отладки
        return get_last_score(client_id, client_secret, player_id, osu_mode, include_fails)


def get_score_weight(client_id: int, client_secret: str, player_id: int, score: osu.SoloScore) -> list | None:
    """
    Возвращает информацию о весе рекорда в профиле пользователя, принимает данные приложения, ID игрока и ID рекорда.
    :param client_id: ID приложения OAuth
    :param client_secret: Ключ приложения OAuth
    :param player_id: ID игрока
    :param score: Рекорд
    """
    try:
        iteration = 1
        for top_score in osu.Client.from_credentials(client_id=client_id, client_secret=client_secret, redirect_url=None).get_user_scores(user=player_id, mode=get_osu_mode(score.ruleset_id), type=osu.UserScoreType.BEST, limit=100):
            if score.id == top_score.id:
                return [top_score.weight, iteration]
            iteration += 1
        else:
            return None
    except:
        print(f"\n{traceback.format_exc()}\nПовтор get_score_weight()")  # Для отладки
        return get_score_weight(client_id, client_secret, player_id, score)


def get_beatmap(client_id: int, client_secret: str, beatmap_id: int) -> osu.Beatmap | None:
    """
    Возвращает информацию о сложности, принимает данные приложения и ID сложности.
    :param client_id: ID приложения OAuth
    :param client_secret: Ключ приложения OAuth
    :param beatmap_id: ID сложности
    """
    try:
        return osu.Client.from_credentials(client_id=client_id, client_secret=client_secret, redirect_url=None).get_beatmap(beatmap=beatmap_id)
    except osu.exceptions.RequestException:
        return None
    except:
        print(f"\n{traceback.format_exc()}\nПовтор get_beatmap()")  # Для отладки
        return get_beatmap(client_id, client_secret, beatmap_id)


def get_beatmap_attributes(client_id: int, client_secret: str, beatmap_id: int, osu_mode: str, score: osu.SoloScore) -> osu.BeatmapDifficultyAttributes | None:
    """
    Возвращает аттрибуты сложности, принимает данные приложения, ID сложности и нужный режим игры.
    :param client_id: ID приложения OAuth
    :param client_secret: Ключ приложения OAuth
    :param beatmap_id: ID сложности
    :param osu_mode: Режим игры
    :param score: Рекорд
    """
    scoreable_mods = []
    for i in [score.mods[i].mod.value for i in range(len(score.mods))]:
        try:
            osu.Mods(0).parse_any_list([i])
            scoreable_mods.append(i)
        except:
            pass
    try:
        return osu.Client.from_credentials(client_id=client_id, client_secret=client_secret, redirect_url=None).get_beatmap_attributes(beatmap=beatmap_id, ruleset=osu_mode, mods=osu.Mods(0).parse_any_list(scoreable_mods))
    except osu.exceptions.RequestException:
        return None
    except:
        print(f"\n{traceback.format_exc()}\nПовтор get_beatmap_attributes()")  # Для отладки
        return get_beatmap_attributes(client_id, client_secret, beatmap_id, osu_mode, score)


# Функции rosu_pp_py

def calculate_pp(score: osu.SoloScore, beatmap_attributes: osu.BeatmapDifficultyAttributes) -> str | None:
    """
    Возвращает форматированную строку с расчётом pp для FC и SS, принимает рекорд и атрибуты сложности.
    :param score: Рекорд
    :param beatmap_attributes: Атрибуты сложности
    """
    recalculation = "Расчёт pp недоступен!"
    selected_beatmap = rosu.Beatmap(content=requests.get(f"https://osu.ppy.sh/osu/{score.beatmap_id}").content)
    mods_list = "".join([getattr(score.mods[i].mod, "value") for i in range(len(score.mods))])
    lazer_score = "CL" not in mods_list
    if score.ruleset_id is None:
        return recalculation
    elif score.ruleset_id == osu.GameModeInt.STANDARD.value:
        recalculated_fc = round(rosu.Performance(mods=mods_list, n100=score.statistics.ok, n50=score.statistics.meh, lazer=lazer_score).calculate(selected_beatmap).pp, 2)
        recalculated_ss = round(rosu.Performance(mods=mods_list, lazer=lazer_score).calculate(selected_beatmap).pp, 2)
    elif score.ruleset_id == osu.GameModeInt.TAIKO.value:
        selected_beatmap.convert(mode=rosu.GameMode.Taiko, mods=mods_list)
        recalculated_fc = round(rosu.Performance(mods=mods_list, n100=score.statistics.ok, lazer=lazer_score).calculate(selected_beatmap).pp, 2)
        recalculated_ss = round(rosu.Performance(mods=mods_list, lazer=lazer_score).calculate(selected_beatmap).pp, 2)
    elif score.ruleset_id == osu.GameModeInt.CATCH.value:
        selected_beatmap.convert(mode=rosu.GameMode.Catch, mods=mods_list)
        recalculated_fc = round(rosu.Performance(mods=mods_list, n100=score.statistics.large_tick_hit, n50=score.statistics.small_tick_hit, lazer=lazer_score).calculate(selected_beatmap).pp, 2)
        recalculated_ss = round(rosu.Performance(mods=mods_list, lazer=lazer_score).calculate(selected_beatmap).pp, 2)
    elif score.ruleset_id == osu.GameModeInt.MANIA.value:
        selected_beatmap.convert(mode=rosu.GameMode.Mania, mods=mods_list)
        recalculated_fc = round(rosu.Performance(mods=mods_list, n300=score.statistics.great, n_katu=score.statistics.good, n100=score.statistics.ok, n50=score.statistics.meh, lazer=lazer_score).calculate(selected_beatmap).pp, 2)
        recalculated_ss = round(rosu.Performance(mods=mods_list, lazer=lazer_score).calculate(selected_beatmap).pp, 2)
    if score.max_combo < beatmap_attributes.max_combo and recalculated_fc != recalculated_ss:
        recalculation = f"FC: {recalculated_fc}pp, SS: {recalculated_ss}pp"
    elif (score.statistics.great != score.maximum_statistics.great) if beatmap_attributes.type.value != osu.GameModeStr.MANIA.value else (score.statistics.perfect != score.maximum_statistics.perfect):
        print(f"\nОжидаемый перерасчёт: FC: {recalculated_fc}pp")  # Для отладки
        recalculation = f"SS: {recalculated_ss}pp"
    else:
        print(f"\nОжидаемый перерасчёт: FC: {recalculated_fc}pp, SS: {recalculated_ss}pp")  # Для отладки
        recalculation = f"SS{"+" if "SILVER" in score.rank.name else ""}!"
    return recalculation
