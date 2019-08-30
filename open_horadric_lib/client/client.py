from __future__ import annotations

import logging

from grpc import Channel
from grpc import ChannelCredentials


class BaseClient:
    """
    Abstract base class for gRPC clients.
    """

    __slots__ = ("channel", "_credentials")

    logger = logging.getLogger("open_horadric_lib.client")

    def __init__(self, channel: Channel, credentials: ChannelCredentials = None):
        self.channel = channel
        self._credentials = credentials

    @property
    def credentials(self):
        return self._credentials
