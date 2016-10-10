""" Our tests are defined in here """
from django_json_api import run


def test_run():
    TEST_NUMBER = 21
    assert run(TEST_NUMBER) == 42
