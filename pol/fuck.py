import sys
import random
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog


class ImageChooser(QWidget):
    def __init__(self):
        super().__init__()

        # create the layout
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # create the "Which do you prefer?" label
        self.pref_label = QLabel("Which do you prefer?")
        self.pref_label.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 20px;")
        self.pref_label.setAlignment(Qt.AlignCenter)

        # create the two image displays
        self.image1_display = QHBoxLayout()
        self.image2_display = QHBoxLayout()

        # create the two vote buttons
        self.vote1_button = QPushButton("Vote for House 1")
        self.vote2_button = QPushButton("Vote for House 2")

        # create a layout for the vote buttons
        self.vote_layout = QHBoxLayout()
        self.vote_layout.addWidget(self.vote1_button)
        self.vote_layout.addWidget(self.vote2_button)

        # add the displays and buttons to the layout
        self.layout.addWidget(self.pref_label)
        self.layout.addLayout(self.image1_display)
        self.layout.addLayout(self.image2_display)
        # self.layout.addWidget(self.vote1_button)
        # self.layout.addWidget(self.vote2_button)
        self.layout.addLayout(self.vote_layout)

        # load the images for both arrays
        self.array1_images = self.load_images('array1')
        self.array2_images = self.load_images('array2')

        # set the initial images to be displayed
        self.set_images(self.array1_images, self.image1_display)
        self.set_images(self.array2_images, self.image2_display)

        # connect the button clicks to the voting functions
        self.vote1_button.clicked.connect(self.vote_for_array1)
        self.vote2_button.clicked.connect(self.vote_for_array2)

        # set the style sheet
        self.setStyleSheet("""
            * {
                font-size: 18px;
                font-weight: bold;
            }
            QPushButton {
                background-color: #007aff;
                color: #fff;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                margin: 20px 0;
            }
            QPushButton:hover {
                background-color: #0055ff;
            }
        """)

    def load_images(self, array_name):
        # TODO: replace this with your own code to load the images for the array
        return [QPixmap(f'{array_name}/image{idx}.png') for idx in range(5)]

    def set_images(self, images, display):
        for image in images:
            label = QLabel()
            label.setPixmap(image)
            label.setAlignment(Qt.AlignCenter)
            display.addWidget(label)

    def vote_for_array1(self):
        # TODO: replace this with your own code to handle voting for array 1
        print("Voted for array 1")

    def vote_for_array2(self):
        # TODO: replace this with your own code to handle voting for array 2
        print("Voted for array 2")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ImageChooser()
    window.show()
    sys.exit(app.exec_())
