import io
import socket
import unittest

from pol.image_loader import ImageLoadError, fetch_image


class FakeResponse:
    def __init__(self, body=b"image", status=200, content_type="image/jpeg"):
        self.body = io.BytesIO(body)
        self.status = status
        self.headers = {"Content-Type": content_type}

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False

    def read(self, size=-1):
        return self.body.read(size)

    def getcode(self):
        return self.status


class ImageLoaderTests(unittest.TestCase):
    def test_fetch_image_uses_timeout_and_accepts_valid_image(self):
        calls = []

        def opener(request, timeout):
            calls.append((request.full_url, timeout))
            return FakeResponse(body=b"jpeg-data")

        result = fetch_image("https://example/house.jpg", opener=opener, timeout=1.5)

        self.assertEqual(result, b"jpeg-data")
        self.assertEqual(calls, [("https://example/house.jpg", 1.5)])

    def test_fetch_image_turns_timeout_into_visible_safe_error(self):
        def opener(request, timeout):
            del request, timeout
            raise socket.timeout("slow server")

        with self.assertRaisesRegex(ImageLoadError, "timed out"):
            fetch_image("https://example/house.jpg", opener=opener, timeout=0.1)

    def test_fetch_image_rejects_non_image_content(self):
        def opener(request, timeout):
            del request, timeout
            return FakeResponse(content_type="text/html")

        with self.assertRaisesRegex(ImageLoadError, "not an image"):
            fetch_image("https://example/house.jpg", opener=opener)

    def test_fetch_image_rejects_unsupported_urls_without_network(self):
        def opener(request, timeout):
            del request, timeout
            self.fail("opener should not be called")

        with self.assertRaisesRegex(ImageLoadError, "HTTP or HTTPS"):
            fetch_image("file:///private/house.jpg", opener=opener)


if __name__ == "__main__":
    unittest.main()