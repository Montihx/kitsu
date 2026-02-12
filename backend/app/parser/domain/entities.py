from dataclasses import dataclass, field
from datetime import datetime
from typing import Literal


@dataclass(frozen=True, slots=True)
class AnimeRelationExternal:
    relation_type: str
    related_source_id: str


@dataclass(frozen=True, slots=True)
class TranslationExternal:
    code: str
    name: str
    type: Literal["voice", "sub"] | None = None


@dataclass(frozen=True, slots=True)
class AnimeExternal:
    source_id: str
    title: str
    original_title: str | None = None
    title_ru: str | None = None
    title_en: str | None = None
    description: str | None = None
    poster_url: str | None = None
    year: int | None = None
    season: str | None = None
    status: str | None = None
    genres: list[str] = field(default_factory=list)
    relations: list[AnimeRelationExternal] = field(default_factory=list)

    @property
    def title_original(self) -> str | None:
        return self.original_title


@dataclass(frozen=True, slots=True)
class EpisodeExternal:
    anime_source_id: str
    number: int
    title: str | None = None
    translation: str | None = None
    quality: str | None = None
    aired_at: datetime | None = None
    stream_url: str | None = None
    translations: list[TranslationExternal] = field(default_factory=list)
    qualities: list[str] = field(default_factory=list)

    @property
    def episode_number(self) -> int:
        return self.number


@dataclass(frozen=True, slots=True)
class ScheduleItem:
    anime_source_id: str
    episode_number: int | None = None
    airs_at: datetime | None = None
    source_url: str | None = None
    source_hash: str | None = None

    @property
    def air_datetime(self) -> datetime | None:
        return self.airs_at
