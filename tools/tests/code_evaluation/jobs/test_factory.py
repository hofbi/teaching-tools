"""Evaluation Job Creation Test."""

import unittest
from pathlib import Path

from sel_tools.code_evaluation.jobs.factory import EvaluationJobFactory
from tests.helper import SimplePassingJob


class EvaluationJobFactoryTest(unittest.TestCase):
    """Test for the abstract factory."""

    def setUp(self) -> None:
        self.module_path = Path(__file__).parent / "modules" / "factory_test_module.py"

    def test_load_factory_from_file__homework_one__expect_empty_list(self) -> None:
        factory = EvaluationJobFactory.load_factory_from_file(self.module_path)
        self.assertListEqual([], factory.create([], 1))

    def test_load_factory_from_file__homework_zero__expect_raises(self) -> None:
        factory = EvaluationJobFactory.load_factory_from_file(self.module_path)
        with self.assertRaises(KeyError):
            factory.create([], 0)

    def test_load_factory_from_file__homework_two__simple_passing_job(self) -> None:
        factory = EvaluationJobFactory.load_factory_from_file(self.module_path)
        self.assertEqual(1, len(factory.create([], 2)))
        self.assertEqual(type(SimplePassingJob()), type(factory.create([], 2)[0]))

    def test_load_factory_from_file__no_module__expect_raises(self) -> None:
        emypt_module_path = Path(__file__).parent / "modules" / "empty_test_module.py"
        with self.assertRaisesRegex(Exception, "No subclass of EvaluationJobFactory"):
            EvaluationJobFactory.load_factory_from_file(emypt_module_path)
