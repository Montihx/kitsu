from typing import Literal

from pydantic import BaseModel, Field


class ParserSettings(BaseModel):
    mode: Literal["manual", "auto"] = Field(default="manual")
    stage_only: bool = Field(default=True)
    autopublish_enabled: bool = Field(default=False)
    enable_autoupdate: bool = Field(default=False)
    update_interval_minutes: int = Field(default=60)
    dry_run_default: bool = Field(default=True)
    allowed_translation_types: list[Literal["voice", "sub"]] = Field(
        default_factory=lambda: ["voice", "sub"]
    )
    allowed_translations: list[str] = Field(default_factory=list)
    allowed_qualities: list[str] = Field(default_factory=list)
    preferred_translation_priority: list[str] = Field(default_factory=list)
    preferred_quality_priority: list[str] = Field(default_factory=list)
    blacklist_titles: list[str] = Field(default_factory=list)
    blacklist_external_ids: list[str] = Field(default_factory=list)
