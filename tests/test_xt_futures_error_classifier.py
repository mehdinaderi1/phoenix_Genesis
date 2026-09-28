import pytest

from execution.http_client import HttpResponse
from execution.xt_futures_error_classifier import (
    XTFuturesErrorClassifier,
    XTFuturesErrorType
)
from execution.xt_futures_response_normalizer import (
    XTFuturesResponseNormalizer
)


@pytest.fixture
def classifier():
    return XTFuturesErrorClassifier()


@pytest.fixture
def normalizer():
    return XTFuturesResponseNormalizer()


def test_successful_http_response_is_none(
    classifier,
    normalizer
):
    response = normalizer.normalize(
        HttpResponse(
            status_code=200,
            body='{"result":{"orderId":"123"}}'
        )
    )

    assert classifier.classify(response) == (
        XTFuturesErrorType.NONE
    )


def test_http_400_is_http_error(
    classifier,
    normalizer
):
    response = normalizer.normalize(
        HttpResponse(
            status_code=400,
            body='{"error":"bad request"}'
        )
    )

    assert classifier.classify(response) == (
        XTFuturesErrorType.HTTP
    )


def test_http_500_is_http_error(
    classifier,
    normalizer
):
    response = normalizer.normalize(
        HttpResponse(
            status_code=500,
            body='{"error":"server error"}'
        )
    )

    assert classifier.classify(response) == (
        XTFuturesErrorType.HTTP
    )


def test_invalid_json_is_parse_error(
    classifier,
    normalizer
):
    response = normalizer.normalize(
        HttpResponse(
            status_code=200,
            body="not-json"
        )
    )

    assert classifier.classify(response) == (
        XTFuturesErrorType.PARSE
    )


def test_json_array_is_parse_error(
    classifier,
    normalizer
):
    response = normalizer.normalize(
        HttpResponse(
            status_code=200,
            body="[]"
        )
    )

    assert classifier.classify(response) == (
        XTFuturesErrorType.PARSE
    )


def test_classifier_rejects_invalid_type(
    classifier
):
    with pytest.raises(
        TypeError,
        match="response must be XTFuturesResponse"
    ):
        classifier.classify(
            {"status_code": 200}
        )
