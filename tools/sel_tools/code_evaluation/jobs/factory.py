"""Evaluation Job Creation Module."""

import importlib.util
import inspect
import sys
from abc import abstractmethod
from collections.abc import Generator
from contextlib import contextmanager
from importlib.abc import Loader
from pathlib import Path

from sel_tools.code_evaluation.jobs.common import EvaluationJob
from sel_tools.utils.repo import GitlabProject


@contextmanager
def add_temporarily_to_pythonpath(folder: Path) -> Generator:
    """Add folder temporarily to pythonpath."""
    folder_to_add = str(folder.resolve())
    sys.path.append(folder_to_add)
    yield
    sys.path.remove(folder_to_add)


class EvaluationJobFactory:
    """Evaluation Job Factory.

    Implement the create function to return the list of evaluation jobs that
    should be used for the given homework number.
    """

    @staticmethod
    @abstractmethod
    def create(
        gitlab_projects: list[GitlabProject], homework_number: int
    ) -> list[EvaluationJob]:
        msg = "Don't call me, I'm abstract."
        raise NotImplementedError(msg)

    @staticmethod
    def load_factory_from_file(module_path: Path) -> type["EvaluationJobFactory"]:
        spec = importlib.util.spec_from_file_location(module_path.stem, module_path)
        if spec is None:
            msg = f"No subclass of EvaluationJobFactory in {module_path}"
            raise ImportError(msg)
        module = importlib.util.module_from_spec(spec)
        # To enable loading files with additionally required python files lying besides them
        with add_temporarily_to_pythonpath(module_path.parent):
            if isinstance(spec.loader, Loader):
                spec.loader.exec_module(module)
        for name, attribute in module.__dict__.items():
            # Feel free to adapt the below conditions to your use case
            if name.startswith("_") or not inspect.isclass(attribute):
                continue
            if (
                issubclass(attribute, EvaluationJobFactory)
                and name != "EvaluationJobFactory"
            ):
                return attribute
        msg = f"No subclass of EvaluationJobFactory in {module_path}"
        raise ModuleNotFoundError(msg)
