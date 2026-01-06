import enum

import pydantic


# region Enums

class Ruleset(enum.StrEnum):
    """
    osu! documentation:
        https://osu.ppy.sh/docs/#ruleset
    """

    OSU = "osu"
    TAIKO = "taiko"
    CATCH = "fruits"
    MANIA = "mania"


# endregion

# region Models

class RawBeatmap(pydantic.BaseModel):
    id: int
    raw: bytes


class UserExtended(pydantic.BaseModel):
    """
    osu! documentation:
        https://osu.ppy.sh/docs/#userextended
    """

    id: int
    username: str
    playmode: Ruleset

# endregion
