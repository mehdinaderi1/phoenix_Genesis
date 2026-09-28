import pytest

from execution.http_client import (
    HttpClient,
    HttpResponse
)


def test_http_response_preserves_values():
    response = HttpResponse(
        status_code=200,
        body='{"rc":0}'
    )

    assert response.status_code == 200
    assert response.body == '{"rc":0}'


def test_http_client_post_is_contract_only():
    client = HttpClient()

    with pytest.raises(
        NotImplementedError
    ):
        client.post(
            endpoint="/test",
            headers={},
            body="{}"
        )
