class XTFuturesOrderDetailClient:
    """Fetches XT Futures order detail through the verified transport."""

    def __init__(self, transport, request_builder):
        self.transport = transport
        self.request_builder = request_builder

    def fetch(self, order_id):
        return self.transport.fetch(
            order_id=order_id,
            request_builder=self.request_builder,
        )
