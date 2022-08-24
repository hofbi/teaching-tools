"""File utils for software engineering tools."""

from abc import ABCMeta, abstractmethod
from pathlib import Path

from sel_tools.utils.config import (
    CMAKE_FILE_ENDING,
    CMAKELISTS_FILE_NAME,
    CPP_FILE_ENDINGS,
)


class FileVisitor:
    """Interface for file visitor.

    Children implement visit_file
    """

    __metaclass__ = ABCMeta

    @abstractmethod
    def visit_file(self, file: Path) -> None:
        raise NotImplementedError("Don't call me, I'm abstract.")


class FileTree:
    """Caller of the visitor pattern.

    Accepts visitors on it is file tree, applies FileVisitor.visit_file() to each
    file in item
    """

    def __init__(self, item: Path):
        self._item = item

    def accept(self, visitor: FileVisitor) -> None:
        if self._item.is_file():
            visitor.visit_file(self._item)
        elif self._item.is_dir():
            for sub_item in self.rglob_but(".git"):
                if sub_item.is_file():
                    visitor.visit_file(sub_item)
        else:
            raise FileNotFoundError(f"Path {self._item} does not exist")

    def rglob_but(self, ignore_folder: str) -> list[Path]:
        return sorted(
            set(self._item.rglob("*"))
            - set(self._item.rglob(ignore_folder))
            - set((self._item / ignore_folder).rglob("*"))
        )


def is_cmake(file: Path) -> bool:
    """Return true if the file is a cmake file, otherwise false."""
    return (file.name == CMAKELISTS_FILE_NAME) or (file.suffix == CMAKE_FILE_ENDING)


def is_cpp(file: Path) -> bool:
    """Return true if the file is a cpp file, otherwise false."""
    return file.suffix in CPP_FILE_ENDINGS
