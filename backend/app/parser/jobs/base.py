from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ParserJob(ABC):
    id: str
    type: str

    @abstractmethod
    def run(self) -> None:
        ...
