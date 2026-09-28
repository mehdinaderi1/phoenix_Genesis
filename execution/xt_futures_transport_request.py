from dataclasses import dataclass


@dataclass(frozen=True)
class XTFuturesTransportRequest:
    """Authenticated XT Futures HTTP request contract."""

    endpoint: str
    body: str
    timestamp: str
    appkey: str
    signature: str

    def headers(self):
        return {
            "Content-Type": "application/json",
            "validate-appkey": self.appkey,
            "validate-timestamp": self.timestamp,
            "validate-signature": self.signature,
        }
