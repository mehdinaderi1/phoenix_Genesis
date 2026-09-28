from enum import Enum

from execution.xt_futures_response import XTFuturesResponse


class XTFuturesErrorType(str, Enum):
    NONE = "NONE"
    NETWORK = "NETWORK"
    HTTP = "HTTP"
    PARSE = "PARSE"
    BUSINESS = "BUSINESS"


class XTFuturesErrorClassifier:
    """
    Classifies normalized XT Futures responses and
    transport exceptions.

    This class does not decide retryability.
    """

    def classify(
        self,
        response: XTFuturesResponse
    ) -> XTFuturesErrorType:

        if not isinstance(
            response,
            XTFuturesResponse
        ):
            raise TypeError(
                "response must be XTFuturesResponse"
            )

        if response.error == "Invalid JSON response":
            return XTFuturesErrorType.PARSE

        if response.error == (
            "Response JSON must be an object"
        ):
            return XTFuturesErrorType.PARSE

        if response.status_code < 200:
            return XTFuturesErrorType.HTTP

        if response.status_code >= 300:
            return XTFuturesErrorType.HTTP

        return XTFuturesErrorType.NONE

    @staticmethod
    def classify_exception(
        exception
    ) -> XTFuturesErrorType:

        if isinstance(
            exception,
            (TimeoutError, OSError)
        ):
            return XTFuturesErrorType.NETWORK

        raise TypeError(
            "unsupported transport exception"
        )
