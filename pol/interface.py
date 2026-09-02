"""PyQt5 desktop interface for pairwise house-preference voting."""

from __future__ import annotations

import sys
from dataclasses import dataclass

from PyQt5.QtCore import QObject, QRunnable, QSize, Qt, QThreadPool, pyqtSignal
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from pol.image_loader import ImageLoadError, fetch_image
from Tati.HouseMatch import (
    DatasetError,
    RecommendationEngine,
    listing_details,
    load_listings,
)


IMAGE_SIZE = QSize(440, 300)


class ImageSignals(QObject):
    loaded = pyqtSignal(int, str, bytes)
    failed = pyqtSignal(int, str, str)


class ImageTask(QRunnable):
    def __init__(self, side: int, url: str, image_fetcher=fetch_image):
        super().__init__()
        self.side = side
        self.url = url
        self.image_fetcher = image_fetcher
        self.signals = ImageSignals()

    def run(self):
        try:
            content = self.image_fetcher(self.url)
        except ImageLoadError as error:
            self._emit("failed", self.side, self.url, str(error))
        else:
            self._emit("loaded", self.side, self.url, content)

    def _emit(self, signal_name: str, *arguments):
        try:
            getattr(self.signals, signal_name).emit(*arguments)
        except RuntimeError:
            pass


@dataclass
class HousePanel:
    image: QLabel
    details: QLabel
    previous: QPushButton
    next: QPushButton
    vote: QPushButton
    image_index: int = 0


class ImageChooser(QWidget):
    def __init__(
        self,
        engine: RecommendationEngine,
        *,
        image_fetcher=fetch_image,
        thread_pool=None,
    ):
        super().__init__()
        self.engine = engine
        self.image_fetcher = image_fetcher
        self.thread_pool = thread_pool or QThreadPool.globalInstance()
        self.setWindowTitle("House Match")
        self.resize(980, 560)

        title = QLabel("Which house do you prefer?")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignCenter)

        self.status = QLabel("Choose a house to improve the next comparison.")
        self.status.setAlignment(Qt.AlignCenter)

        self.panels = (self._build_panel(0), self._build_panel(1))
        comparisons = QHBoxLayout()
        comparisons.setSpacing(18)
        for panel in self.panels:
            column = QVBoxLayout()
            column.addWidget(panel.image)
            image_navigation = QHBoxLayout()
            image_navigation.addWidget(panel.previous)
            image_navigation.addWidget(panel.next)
            column.addLayout(image_navigation)
            column.addWidget(panel.details)
            column.addWidget(panel.vote)
            comparisons.addLayout(column)

        layout = QVBoxLayout(self)
        layout.addWidget(title)
        layout.addLayout(comparisons)
        layout.addWidget(self.status)

        self.setStyleSheet(
            """
            QWidget { background: #eef5ed; color: #17251d; }
            QLabel#title { font-size: 28px; font-weight: 700; padding: 10px; }
            QLabel#image { background: #ffffff; border: 2px solid #3d8060; }
            QLabel#details { background: #ffffff; padding: 10px; }
            QPushButton { background: #2f7655; color: white; border: 0; padding: 9px; }
            QPushButton:disabled { background: #9baba2; }
            QPushButton:hover { background: #245c43; }
            """
        )
        self.show_pair()

    def _build_panel(self, side: int) -> HousePanel:
        image = QLabel("Loading image...")
        image.setObjectName("image")
        image.setAlignment(Qt.AlignCenter)
        image.setMinimumSize(IMAGE_SIZE)
        image.setWordWrap(True)

        details = QLabel()
        details.setObjectName("details")
        details.setWordWrap(True)
        previous = QPushButton("Previous image")
        next_button = QPushButton("Next image")
        vote = QPushButton(f"Vote for house {side + 1}")
        previous.clicked.connect(lambda: self.change_image(side, -1))
        next_button.clicked.connect(lambda: self.change_image(side, 1))
        vote.clicked.connect(lambda: self.vote(side))
        return HousePanel(image, details, previous, next_button, vote)

    def show_pair(self):
        for side, listing in enumerate(self.engine.current_pair):
            panel = self.panels[side]
            panel.image_index = 0
            panel.details.setText(listing_details(listing))
            navigation_enabled = len(listing.images) > 1
            panel.previous.setEnabled(navigation_enabled)
            panel.next.setEnabled(navigation_enabled)
            self.load_current_image(side)

    def vote(self, side: int):
        selected = self.engine.current_pair[side]
        try:
            self.engine.vote(side)
        except RuntimeError as error:
            QMessageBox.information(self, "No more comparisons", str(error))
            return
        self.status.setText(
            f"Vote {self.engine.preference_revision}: house {selected.listing_id} selected."
        )
        self.show_pair()

    def change_image(self, side: int, offset: int):
        listing = self.engine.current_pair[side]
        if not listing.images:
            return
        panel = self.panels[side]
        panel.image_index = (panel.image_index + offset) % len(listing.images)
        self.load_current_image(side)

    def load_current_image(self, side: int):
        listing = self.engine.current_pair[side]
        panel = self.panels[side]
        panel.image.clear()
        if not listing.images:
            panel.image.setText("No listing image available")
            return

        url = listing.images[panel.image_index]
        panel.image.setText("Loading image...")
        task = ImageTask(side, url, self.image_fetcher)
        task.signals.loaded.connect(self.image_loaded)
        task.signals.failed.connect(self.image_failed)
        self.thread_pool.start(task)

    def image_loaded(self, side: int, url: str, content: bytes):
        if url != self._current_url(side):
            return
        pixmap = QPixmap()
        if not pixmap.loadFromData(content):
            self.image_failed(side, url, "downloaded data is not a supported image")
            return
        self.panels[side].image.setPixmap(
            pixmap.scaled(IMAGE_SIZE, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        )

    def image_failed(self, side: int, url: str, reason: str):
        if url != self._current_url(side):
            return
        self.panels[side].image.setText(f"Image unavailable\n{reason}")

    def _current_url(self, side: int) -> str | None:
        listing = self.engine.current_pair[side]
        if not listing.images:
            return None
        return listing.images[self.panels[side].image_index]


def main() -> int:
    app = QApplication(sys.argv)
    try:
        listings = load_listings()
        chooser = ImageChooser(RecommendationEngine(listings))
    except (DatasetError, ValueError) as error:
        QMessageBox.critical(None, "House Match cannot start", str(error))
        return 2
    chooser.show()
    return app.exec_()


if __name__ == "__main__":
    raise SystemExit(main())
