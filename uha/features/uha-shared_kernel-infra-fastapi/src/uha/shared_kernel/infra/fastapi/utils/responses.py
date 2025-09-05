from typing import Any

import msgspec
from fastapi.responses import Response


class MsgSpecJSONResponse(Response):
    """Custom JSON response using msgspec for faster serialization."""

    media_type = "application/json"

    def render(self, content: Any) -> bytes:
        if content is None:
            return b""
        return msgspec.json.encode(content)
