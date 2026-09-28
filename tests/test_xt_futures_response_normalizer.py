import pytest

from execution.http_client import HttpResponse
from execution.xt_futures_response_normalizer import (
    XTFuturesResponseNormalizer
)


@pytest.fixture
def normalizer():
    return XTFuturesResponseNormalizer()


def test_success_json_response(normalizer):
    response = HttpResponse(
        status_code=200,
        body='{"rc":0,"result":{"orderId":"123"}}'
    )

    result = normalizer.normalize(response)

    assert result.status_code == 200
    assert result.ok is True
    assert result.body == {
        "rc": 0,
        "result": {
            "orderId": "123"
        }
    }
    assert result.error is None


def test_http_error_response(normalizer):
    response = HttpResponse(
        status_code=400,
        body='{"rc":1001,"msg":"bad request"}'
    )

    result = normalizer.normalize(response)

    assert result.status_code == 400
    assert result.ok is False
    assert result.body == {
        "rc": 1001,
        "msg": "bad request"
    }
    assert result.error == "HTTP 400"


def test_invalid_json_response(normalizer):
    response = HttpResponse(
        status_code=200,
        body="not-json"
    )

    result = normalizer.normalize(response)

    assert result.ok is False
    assert result.body is None
    assert result.raw_body == "not-json"
    assert result.error == "Invalid JSON response"


def test_json_array_is_rejected(normalizer):
    response = HttpResponse(
        status_code=200,
        body='[{"orderId":"123"}]'
    )

    result = normalizer.normalize(response)

    assert result.ok is False
    assert result.body is None
    assert result.error == (
        "Response JSON must be an object"
    )


def test_response_object_is_not_mutated(normalizer):
    response = HttpResponse(
        status_code=200,
        body='{"rc":0,"result":{}}'
    )

    result = normalizer.normalize(response)

    assert result.raw_body == (
        '{"rc":0,"result":{}}'
    )


def test_invalid_response_type_is_rejected(normalizer):
    with pytest.raises(
        TypeError,
        match="response must be HttpResponse"
    ):
        normalizer.normalize(
            {"status_code": 200}
        )
