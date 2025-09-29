from __future__ import annotations
import rosu_pp_py
import enum
import pyquoks.models, pyquoks.data


# Enums
class RulesetsType(enum.StrEnum):
    """
    osu! documentation: https://osu.ppy.sh/docs/#ruleset
    """

    OSU = "osu"
    TAIKO = "taiko"
    CATCH = "fruits"
    MANIA = "mania"
    # AUTO = "auto"


# Utils
class RulesetsUtils:
    list = [
        RulesetsType.OSU,
        RulesetsType.TAIKO,
        RulesetsType.CATCH,
        RulesetsType.MANIA,
        # RulesetsType.AUTO,
    ]
    names = {
        RulesetsType.OSU: "osu!",
        RulesetsType.TAIKO: "osu!taiko",
        RulesetsType.CATCH: "osu!catch",
        RulesetsType.MANIA: "osu!mania",
        # RulesetsType.AUTO: "Automatic",
    }
    rosu_pp = {
        RulesetsType.OSU: rosu_pp_py.GameMode.Osu,
        RulesetsType.TAIKO: rosu_pp_py.GameMode.Taiko,
        RulesetsType.CATCH: rosu_pp_py.GameMode.Catch,
        RulesetsType.MANIA: rosu_pp_py.GameMode.Mania,
    }
    rulesets = {
        "osu!": RulesetsType.OSU,
        "osu!taiko": RulesetsType.TAIKO,
        "osu!catch": RulesetsType.CATCH,
        "osu!mania": RulesetsType.MANIA,
        # "Automatic": RulesetsType.AUTO,
    }


# Models & Containers
class UserStatistics(pyquoks.models.IModel):
    """
    osu! documentation: https://osu.ppy.sh/docs/#userstatistics
    """

    _ATTRIBUTES = {
        "global_rank",
        "pp",
    }
    global_rank: int | None
    pp: int | None


class User(pyquoks.models.IModel):
    """
    osu! documentation: https://osu.ppy.sh/docs/#userextended
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
    avatar_url: str | None
    id: int | None
    playmode: str | None
    statistics: UserStatistics | None
    username: str | None


class RawBeatmapContainer(pyquoks.models.IContainer):
    _ATTRIBUTES = {
        "id",
        "bytes",
    }
    id: int
    bytes: bytes


class BeatmapAttributes(pyquoks.models.IModel):
    """
    osu! documentation: https://osu.ppy.sh/docs/#beatmapdifficultyattributes
    """

    _ATTRIBUTES = {
        "attributes": {
            "star_rating",
            "max_combo",
        },
    }
    star_rating: float | None
    max_combo: int | None


class Beatmap(pyquoks.models.IModel):
    """
    osu! documentation: https://osu.ppy.sh/docs/#beatmapextended
    """

    _ATTRIBUTES = {
        "beatmapset_id",
        "difficulty_rating",
        "id",
        "status",
        "version",
    }
    beatmapset_id: int | None
    difficulty_rating: float | None
    id: int | None
    status: str | None
    version: str | None


class Beatmapset(pyquoks.models.IModel):
    """
    osu! documentation: https://osu.ppy.sh/docs/#beatmapset
    """

    _ATTRIBUTES = {
        "artist",
        "creator",
        "id",
        "title",
    }
    artist: str | None
    creator: str | None
    id: int | None
    title: str | None


class Mod(pyquoks.models.IModel):
    _ATTRIBUTES = {
        "acronym",
        "settings",
    }
    acronym: str | None
    settings: dict | None


class ModsContainer(pyquoks.models.IContainer):
    _DATA = {
        "mods": Mod,
    }
    mods: list[Mod]

    @property
    def mods_string(self) -> list | None:
        return None if len(self.mods) == int() else [i.acronym + ("*" if i.settings else str()) for i in self.mods]


class ScoreWeight(pyquoks.models.IModel):
    _ATTRIBUTES = {
        "percentage",
        "pp",
    }
    percentage: float | None
    pp: float | None


class ScoreStatistics(pyquoks.models.IModel):
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


class Score(pyquoks.models.IModel):
    """
    osu! documentation: https://osu.ppy.sh/docs/#score
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
        "mods": ModsContainer,
        "statistics": ScoreStatistics,
        "weight": ScoreWeight
    }
    accuracy: float | None
    beatmap: Beatmap | None
    beatmapset: Beatmapset | None
    has_replay: bool | None
    id: int | None
    max_combo: int | None
    maximum_statistics: ScoreStatistics | None
    mods: ModsContainer | None
    passed: bool | None
    pp: float | None
    rank: str | None
    rank_global: int | None
    ruleset_id: int | None
    statistics: ScoreStatistics | None
    is_perfect_combo: bool | None
    weight: ScoreWeight | None


class SeasonalBackground(pyquoks.models.IModel):
    _ATTRIBUTES = {
        "url",
    }
    _OBJECTS = {
        "user": User,
    }
    url: str | None
    user: User | None


class SeasonalBackgroundSetContainer(pyquoks.models.IContainer):
    _ATTRIBUTES = {
        "ends_at",
    }
    _OBJECTS = {
        "backgrounds": SeasonalBackground,
    }
    backgrounds: list[SeasonalBackground] | None
    ends_at: str | None


# Values
class ScoreWeightValues(pyquoks.models.IValues):
    _ATTRIBUTES = {
        "place",
        "score",
    }
    place: int | None
    score: Score | None


class RecalculatedValues(pyquoks.models.IValues):
    _ATTRIBUTES = {
        "performance_fc",
        "performance_ss",
        "difficulty",
    }
    performance_fc: rosu_pp_py.PerformanceAttributes | None
    performance_ss: rosu_pp_py.PerformanceAttributes | None
    difficulty: rosu_pp_py.DifficultyAttributes | None


class DifficultyColorsValues(pyquoks.models.IValues):
    _ATTRIBUTES = {
        "difficulty_color",
        "text_color",
    }
    difficulty_color: str | None
    text_color: str | None


class ParsingValues(pyquoks.models.IValues):
    _ATTRIBUTES = {
        "pp_total",
        "pp_diff",
        "score_id",
        "settings",
    }
    pp_total: float | None
    pp_diff: float | None
    score_id: int | None
    settings: pyquoks.data.IRegistryManager.IRegistry | None
