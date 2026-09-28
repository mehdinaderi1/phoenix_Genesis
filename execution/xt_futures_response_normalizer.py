import json

from execution.http_client import HttpResponse
from execution.xt_futures_response import XTFuturesResponse


class XTFuturesResponseNormalizer:
    """
    Converts raw HTTP responses into a safe Phoenix response contract.

    This class does not decide whether an order should be retried,
    rejected, or executed.
    """

    def normalize(
        self,
        response: HttpResponse
    ) -> XTFuturesResponse:

        if not isinstance(response, HttpResponse):
            raise TypeError(
                "response must be HttpResponse"
            )

        try:
            body = json.loads(response.body)
        except (TypeError, json.JSONDecodeError):
            return XTFuturesResponse(
                status_code=response.status_code,
                ok=False,
                body=None,
                raw_body=response.body,
                error="Invalid JSON response"
            )

        if not isinstance(body, dict):
            return XTFuturesResponse(
                status_code=response.status_code,
                ok=False,
                body=None,
                raw_body=response.body,
                error="Response JSON must be an object"
            )

        return XTFuturesResponse(
            status_code=response.status_code,
            ok=200 <= response.status_code < 300,
            body=body,
            raw_body=response.body,
            error=None
            if 200 <= response.status_code < 300
            else f"HTTP {response.status_code}"
        )
