# Testing how to test

import pytest
from united_power.usage import UnitedPowerUsage


def test_create_object():
    united_power = UnitedPowerUsage('http://foo.com', 'username', 'password')

