from __future__ import annotations
import rosu_pp_py


def convert_mods(data: list[dict]) -> list | None:
    return None if len(data) == int() else [i["acronym"] for i in data]


class Rulesets:
    """
    https://osu.ppy.sh/docs/#ruleset
    """
    OSU = "osu"
    TAIKO = "taiko"
    CATCH = "fruits"
    MANIA = "mania"
    index = [
        OSU,
        TAIKO,
        CATCH,
        MANIA,
    ]
    names = {
        OSU: "osu!",
        TAIKO: "osu!taiko",
        CATCH: "osu!catch",
        MANIA: "osu!mania",
    }
    rosu_pp = {
        OSU: rosu_pp_py.GameMode.Osu,
        TAIKO: rosu_pp_py.GameMode.Taiko,
        CATCH: rosu_pp_py.GameMode.Catch,
        MANIA: rosu_pp_py.GameMode.Mania,
    }
    rulesets = {
        "osu!": OSU,
        "osu!taiko": TAIKO,
        "osu!catch": CATCH,
        "osu!mania": MANIA,
    }


class RawBeatmapContainer:
    id: int
    bytes: bytes

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


class SampleModel:
    _ATTRIBUTES = None
    _OBJECTS = None
    data: dict

    def __init__(self, data: dict):
        setattr(self, "data", data)
        if isinstance(self._ATTRIBUTES, set):
            for i in self._ATTRIBUTES:
                try:
                    setattr(self, i, data[i])
                except:
                    setattr(self, i, None)
        if isinstance(self._ATTRIBUTES, dict):
            for i, j in self._ATTRIBUTES.items():
                if isinstance(j, set):
                    for k in j:
                        try:
                            setattr(self, k, data[i][k])
                        except:
                            setattr(self, k, None)
        if isinstance(self._OBJECTS, dict):
            for i in self._OBJECTS.keys():
                try:
                    setattr(self, i, self._OBJECTS[i](data=data[i]))
                except:
                    setattr(self, i, None)


class UserStatistics(SampleModel):
    """
    https://osu.ppy.sh/docs/#userstatistics
    """
    _ATTRIBUTES = {
        "global_rank",
        "pp",
    }
    data: dict
    global_rank: int | None
    pp: int | None


class User(SampleModel):
    """
    https://osu.ppy.sh/docs/#userextended
    """
    _ATTRIBUTES = {
        "avatar_url",
        "id",
        "playmode",
        "username",
    }
    _OBJECTS = {
        "statistics": UserStatistics,
    }
    data: dict
    avatar_url: str | None
    id: int | None
    playmode: str | None
    statistics: UserStatistics | None
    username: str | None


class BeatmapAttributes(SampleModel):
    """
    https://osu.ppy.sh/docs/#beatmapdifficultyattributes
    """
    _ATTRIBUTES = {
        "attributes": {
            "star_rating",
            "max_combo",
        },
    }
    data: dict
    star_rating: float | None
    max_combo: int | None


class Beatmap(SampleModel):
    """
    https://osu.ppy.sh/docs/#beatmapextended
    """
    _ATTRIBUTES = {
        "beatmapset_id",
        "id",
        "status",
        "version",
    }
    data: dict
    beatmapset_id: int | None
    id: int | None
    status: str | None
    version: str | None


class Beatmapset(SampleModel):
    _ATTRIBUTES = {
        "artist",
        "creator",
        "id",
        "title",
    }
    data: dict
    artist: str | None
    creator: str | None
    id: int | None
    title: str | None


class ScoreWeight(SampleModel):
    _ATTRIBUTES = {
        "percentage",
        "pp",
    }
    data: dict
    percentage: float | None
    pp: float | None


class ScoreStatistics(SampleModel):
    _ATTRIBUTES = {
        "good",
        "great",
        "ignore_hit",
        "ignore_miss",
        "large_bonus",
        "large_tick_hit",
        "meh",
        "miss",
        "ok",
        "perfect",
        "slider_tail_hit",
        "small_bonus",
        "small_tick_hit",
    }
    data: dict
    good: int | None
    great: int | None
    ignore_hit: int | None
    ignore_miss: int | None
    large_bonus: int | None
    large_tick_hit: int | None
    meh: int | None
    miss: int | None
    ok: int | None
    perfect: int | None
    slider_tail_hit: int | None
    small_bonus: int | None
    small_tick_hit: int | None


class Score(SampleModel):
    """
    https://osu.ppy.sh/docs/#score
    """
    _ATTRIBUTES = {
        "accuracy",
        "has_replay",
        "id",
        "max_combo",
        "passed",
        "pp",
        "rank",
        "rank_global",
        "ruleset_id",
        "is_perfect_combo",
    }
    _OBJECTS = {
        "beatmap": Beatmap,
        "beatmapset": Beatmapset,
        "maximum_statistics": ScoreStatistics,
        "mods": convert_mods,
        "statistics": ScoreStatistics,
        "weight": ScoreWeight
    }
    data: dict
    accuracy: float | None
    beatmap: Beatmap | None
    beatmapset: Beatmapset | None
    has_replay: bool | None
    id: int | None
    max_combo: int | None
    maximum_statistics: ScoreStatistics | None
    mods: list | None
    passed: bool | None
    pp: float | None
    rank: str | None
    rank_global: int | None
    ruleset_id: int | None
    statistics: ScoreStatistics | None
    is_perfect_combo: bool | None
    weight: ScoreWeight | None
