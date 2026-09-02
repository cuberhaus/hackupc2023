import os
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt5.QtGui import QImage
from PyQt5.QtWidgets import QApplication
from PyQt5.sip import delete

from house_match.image_loader import ImageLoadError
from house_match.interface import ImageChooser, ImageTask
from house_match.recommender import RecommendationEngine
from test_house_match import make_house


class ImmediateThreadPool:
    def start(self, task):
        task.run()


class InterfaceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_widget_shows_fallback_and_advances_pair_after_vote(self):
        houses = [
            make_house(f"house-{index}", price=float(index * 100))
            for index in range(6)
        ]

        def failing_fetcher(url):
            raise ImageLoadError(f"offline: {url}")

        chooser = ImageChooser(
            RecommendationEngine(houses, seed=4),
            image_fetcher=failing_fetcher,
            thread_pool=ImmediateThreadPool(),
        )
        first_pair = tuple(house.listing_id for house in chooser.engine.current_pair)

        self.assertIn("Image unavailable", chooser.panels[0].image.text())
        self.assertIn("Image unavailable", chooser.panels[1].image.text())
        chooser.change_image(0, 1)
        chooser.vote(0)
        second_pair = tuple(house.listing_id for house in chooser.engine.current_pair)

        self.assertTrue(set(first_pair).isdisjoint(second_pair))
        self.assertEqual(chooser.engine.preference_revision, 1)
        self.assertIn("Vote 1", chooser.status.text())
        chooser.close()

    def test_widget_displays_downloaded_image(self):
        image = QImage(2, 2, QImage.Format_RGB32)
        image.fill(0x336699)
        from PyQt5.QtCore import QBuffer, QIODevice

        buffer = QBuffer()
        buffer.open(QIODevice.WriteOnly)
        image.save(buffer, "PNG")
        content = bytes(buffer.data())
        houses = [make_house(f"house-{index}", price=float(index)) for index in range(4)]

        chooser = ImageChooser(
            RecommendationEngine(houses, seed=2),
            image_fetcher=lambda url: content,
            thread_pool=ImmediateThreadPool(),
        )

        self.assertIsNotNone(chooser.panels[0].image.pixmap())
        self.assertIsNotNone(chooser.panels[1].image.pixmap())
        chooser.close()

    def test_image_task_ignores_completion_after_signal_owner_is_destroyed(self):
        task = ImageTask(0, "https://example/house.jpg", lambda url: b"image")
        delete(task.signals)

        task.run()


if __name__ == "__main__":
    unittest.main()