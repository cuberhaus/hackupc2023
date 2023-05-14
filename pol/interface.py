import sys
import random
import json

import gower

import numpy as np
import pandas as pd
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog

import gower
import requests

from Tati.HouseMatch import *

class ImageChooser(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedSize(670, 500)
        self.userMatrix = []

        self.data = format_table()

        # Choose two random rows
        idx1, idx2 = np.random.choice(self.data.shape[0], size=2, replace=False)
        self.house1 = self.data.iloc[idx1, :]
        self.house2 = self.data.iloc[idx2, :]

        # create the layout
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # create the "Which do you prefer?" label
        self.pref_label = QLabel("Which do you prefer?")
        # self.pref_label.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 20px;")
        self.pref_label.setStyleSheet("background: #CCFFCC; font-size: 32px; font-weight: bold; color: #333; "
                                      "margin-bottom: 20px;"
                                      "text-align: center; letter-spacing: 2px;")
        self.pref_label.setAlignment(Qt.AlignCenter)

        # create the image displays and navigation buttons for array 1
        self.array1_label = QLabel()
        self.array1_label.setAlignment(Qt.AlignCenter)
        self.array1_prev_button = QPushButton("Previous")
        self.array1_next_button = QPushButton("Next")

        # create a layout for the array 1 display and navigation buttons
        self.array1_layout = QVBoxLayout()
        self.array1_layout.addWidget(self.array1_label)
        self.array1_layout.addWidget(self.array1_prev_button, alignment=Qt.AlignVCenter)
        self.array1_layout.addWidget(self.array1_next_button)

        # create the image displays and navigation buttons for array 2
        self.array2_label = QLabel()
        self.array2_label.setAlignment(Qt.AlignCenter)
        self.array2_prev_button = QPushButton("Previous")
        self.array2_next_button = QPushButton("Next")

        # create a layout for the array 2 display and navigation buttons
        self.array2_layout = QVBoxLayout()
        self.array2_layout.addWidget(self.array2_label)
        self.array2_layout.addWidget(self.array2_prev_button)
        self.array2_layout.addWidget(self.array2_next_button)

        # create a layout to display the two array layouts side by side
        self.viewer_layout = QHBoxLayout()
        self.viewer_layout.addLayout(self.array1_layout)
        self.viewer_layout.addLayout(self.array2_layout)

        # add the viewers and "Which do you prefer?" label to the main layout
        self.layout.addWidget(self.pref_label)
        self.layout.addLayout(self.viewer_layout)

        # load the initial images for both arrays
        self.load_images_op1()
        self.load_images_op2()

        # set the initial preferences
        self.favorite_attributes = init_features_rand(self.data)

        # set the initial images to be displayed
        ''''
        self.current_array1_idx = 0
        self.current_array2_idx = 0
        self.set_image(self.array1_images[self.current_array1_idx], self.array1_label)
        self.set_image(self.array2_images[self.current_array2_idx], self.array2_label)
        '''

        # connect the button clicks to the navigation functions
        self.array1_prev_button.clicked.connect(self.prev_array1)
        self.array1_next_button.clicked.connect(self.next_array1)
        self.array2_prev_button.clicked.connect(self.prev_array2)
        self.array2_next_button.clicked.connect(self.next_array2)

        # create the two vote buttons
        self.vote1_button = QPushButton("Vote for House 1")
        self.vote2_button = QPushButton("Vote for House 2")

        # create a layout for the vote buttons
        self.vote_layout = QHBoxLayout()
        self.vote_layout.addWidget(self.vote1_button)
        self.vote_layout.addWidget(self.vote2_button)

        self.layout.addLayout(self.vote_layout)

        # connect the button clicks to the voting functions
        self.vote1_button.clicked.connect(self.vote_for_array1)
        self.vote2_button.clicked.connect(self.vote_for_array2)

        # Set stylesheet for the main window
        self.setStyleSheet("""
            QWidget {
                background-color: #CCFFCC;
            }
            QMainWindow {
                background-color: #CCFFCC;
            }

            QLabel {
                background-color: white;
            }

            QPushButton {
                background-color: #3D9970;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 5px 10px;
                font-size: 16px;
            }

            QPushButton:hover {
                background-color: #2E8B57;
            }

            QPushButton:pressed {
                background-color: #135632;
            }
        """)

        # Set the border properties for the image viewers
        self.array1_label.setStyleSheet("""
            border: 2px solid #3D9970;
            """)
        self.array2_label.setStyleSheet("""
            border: 2px solid #3D9970;
            """)


    def vote_for_array1(self):
        self.favorite_attributes = ponderate_attributes(self.favorite_attributes, self.house1)
        self.house1 = find_nearest_numerical_only(self.favorite_attributes, self.data)
        self.load_images_op1()
        print("Voted for array 1")

    def vote_for_array2(self):
        self.favorite_attributes = ponderate_attributes(self.favorite_attributes, self.house2)
        self.house2 = find_nearest_numerical_only(self.favorite_attributes, self.data)
        self.load_images_op2()
        print("Voted for array 2")

    def load_images_op1(self):

        self.current_array1_idx = 1
        self.array1_images = []

        for i, url in enumerate(self.house1['images']):
            # Realiza una solicitud a la URL y obtiene los datos de la imagen
            response = requests.get(url)
            image_data = response.content

            # Crea un QPixmap desde los datos de la imagen
            pixmap = QPixmap()
            pixmap.loadFromData(image_data)
            self.array1_images.append(pixmap)

        self.set_image(self.array1_images[0], self.array1_label)



    def load_images_op2(self):
        self.array2_images = []
        self.current_array2_idx = 1

        for i, url in enumerate(self.house2['images']):
            # Realiza una solicitud a la URL y obtiene los datos de la imagen
            response = requests.get(url)
            image_data = response.content

            # Crea un QPixmap desde los datos de la imagen
            pixmap = QPixmap()
            pixmap.loadFromData(image_data)
            self.array2_images.append(pixmap)

        self.set_image(self.array2_images[0], self.array2_label)

    def set_image(self, pixmap, label):
        # set the image in the given label and scale it to fit the label size
        label.setPixmap(pixmap.scaled(label.size()))

    def prev_array1(self):
        # go to the previous image in array 1
        self.current_array1_idx = (self.current_array1_idx - 1) % len(self.array1_images)
        self.set_image(self.array1_images[self.current_array1_idx], self.array1_label)

    def next_array1(self):
        # go to the next image in array 1
        self.current_array1_idx = (self.current_array1_idx + 1) % len(self.array1_images)
        self.set_image(self.array1_images[self.current_array1_idx], self.array1_label)

    def prev_array2(self):
        # go to the previous image in array 2
        self.current_array2_idx = (self.current_array2_idx - 1) % len(self.array2_images)
        self.set_image(self.array2_images[self.current_array2_idx], self.array2_label)

    def next_array2(self):
        # go to the next image in array 2
        self.current_array2_idx = (self.current_array2_idx + 1) % len(self.array2_images)
        self.set_image(self.array2_images[self.current_array2_idx], self.array2_label)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    chooser = ImageChooser()
    chooser.show()
    sys.exit(app.exec_())

