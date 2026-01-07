import pydantic
import pyquoks

import src.data
import src.models


# region models.py

class TestData(pydantic.BaseModel):
    beatmap_id: int
    beatmapset_id: int
    message: str
    ruleset: src.models.Ruleset
    score_id: int
    user_id: int


# endregion

# region data.py

class ConfigManager(src.data.ConfigManager):
    _PATH = pyquoks.utils.get_path("tests/config.ini")

    oauth: src.data.ConfigManager.OAuthConfig
    settings: src.data.ConfigManager.SettingsConfig

# endregion
