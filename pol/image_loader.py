"""Bounded network image loading kept separate from the GUI and recommender."""

from __future__ import annotations

import socket
from collections.abc import Callable
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen


DEFAULT_TIMEOUT_SECONDS = 4.0
MAX_IMAGE_BYTES = 8 * 1024 * 1024


class ImageLoadError(RuntimeError):
    """Raised when a listing image cannot be downloaded safely."""


def fetch_image(
    url: str,
    *,
    opener: Callable = urlopen,
    timeout: float = DEFAULT_TIMEOUT_SECONDS,
    max_bytes: int = MAX_IMAGE_BYTES,
) -> bytes:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ImageLoadError("image URL must use HTTP or HTTPS")

    request = Request(url, headers={"User-Agent": "hackupc2023-house-demo/1.0"})
    try:
        with opener(request, timeout=timeout) as response:
            status = response.getcode()
            content_type = response.headers.get("Content-Type", "")
            content = response.read(max_bytes + 1)
    except (socket.timeout, TimeoutError) as error:
        raise ImageLoadError("image download timed out") from error
    except HTTPError as error:
        raise ImageLoadError(f"image server returned HTTP {error.code}") from error
    except (URLError, OSError) as error:
        reason = error.reason if isinstance(error, URLError) else error
        raise ImageLoadError(f"image download failed: {reason}") from error

    if status is not None and not 200 <= status < 300:
        raise ImageLoadError(f"image server returned HTTP {status}")
    if not content_type.lower().startswith("image/"):
        raise ImageLoadError("image URL response is not an image")
    if len(content) > max_bytes:
        raise ImageLoadError(f"image exceeds the {max_bytes}-byte safety limit")
    if not content:
        raise ImageLoadError("image response was empty")
    return content