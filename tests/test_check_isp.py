from http import HTTPStatus
from unittest.mock import MagicMock

import pytest

from bucket_of_utils.check_isp.main import check_isp


def mock_response(org_value: str):
    class MockResponse(MagicMock):
        @property
        def status_code(self):
            return HTTPStatus.OK

        def json(self):
            return {"org": org_value}

    return MockResponse()


def test_check_isp(mocker):
    mocker.patch("requests.get", return_value=mock_response("AS5617 Orange Polska Spolka Akcyjna"))
    is_it = check_isp(include_in_name="Orange")
    assert is_it is True


def test_check_isp_returns_false_when_include_in_name_is_not_in_org(mocker):
    mocker.patch("requests.get", return_value=mock_response("Orange Mobile Polska Spolka Akcyjna"))
    is_it = check_isp(include_in_name="Orange", exclude_in_name="Mobile")
    assert is_it is False


def test_check_isp_returns_false_when_exclude_in_name_is_in_org(mocker):
    mocker.patch("requests.get", return_value=mock_response("AS5617 Orange Polska Spolka Akcyjna"))
    is_it = check_isp(exclude_in_name="Orange")
    assert is_it is False


def test_check_isp_raises_value_error_when_both_parameters_are_none():
    with pytest.raises(ValueError):
        check_isp()
