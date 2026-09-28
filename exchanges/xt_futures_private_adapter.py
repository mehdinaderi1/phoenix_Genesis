"""XT USDT-M Futures private API adapter primitives."""

import hashlib
import hmac
from urllib.parse import urlencode


class XTFuturesPrivateAdapter:
    """Private XT Futures adapter with signature generation primitives."""

    def __init__(self, appkey, secret_key):
        self.appkey = appkey
        self.secret_key = secret_key

    @staticmethod
    def build_query_string(params=None):
        """Build a deterministic query string from request parameters."""
        if not params:
            return ""

        sorted_params = sorted(params.items())
        return urlencode(sorted_params)

    def generate_signature(
        self,
        timestamp,
        endpoint,
        query_string=""
    ):
        """Generate the XT Futures query-string signature."""
        fixed_header = (
            f"validate-appkey={self.appkey}"
            f"&validate-timestamp={timestamp}"
        )

        unencrypted_string = (
            f"{fixed_header}#{endpoint}#{query_string}"
        )

        return hmac.new(
            self.secret_key.encode("utf-8"),
            unencrypted_string.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

    def generate_body_signature(
        self,
        timestamp,
        endpoint,
        request_body=""
    ):
        """Generate the XT Futures request-body signature."""
        fixed_header = (
            f"validate-appkey={self.appkey}"
            f"&validate-timestamp={timestamp}"
        )

        unencrypted_string = (
            f"{fixed_header}#{endpoint}#{request_body}"
        )

        return hmac.new(
            self.secret_key.encode("utf-8"),
            unencrypted_string.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
