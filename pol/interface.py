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


# Add nested values as columns
def data_to_table():
    df = pd.read_json('../restbai/hackupc2023_restbai__dataset_sample.json')
    df = df.transpose()

    val_property = []
    val_kitchen = []
    val_bathroom = []
    val_interior = []
    val_style = []

    for row in df['image_data']:
        # print(row['r1r6']['property'])
        val_property.append(row['r1r6']['property'])
        val_kitchen.append(row['r1r6']['kitchen'])
        val_bathroom.append(row['r1r6']['bathroom'])
        val_interior.append(row['r1r6']['interior'])
        val_style.append(row['style']['label'])

    df['r1r6_property'] = val_property
    df['r1r6_kitchen'] = val_kitchen
    df['r1r6_bathroom'] = val_bathroom
    df['r1r6_interior'] = val_interior
    df['style'] = val_style


    df.to_csv('database.csv', index=False)

    return df

def format_table():
    # Add all relevant colums into the table
    df = data_to_table()

    #Edit None to be string
    df['r1r6_property'] = df['r1r6_property'].fillna(0)
    df['r1r6_kitchen'] = df['r1r6_kitchen'].fillna(0)
    df['r1r6_bathroom'] = df['r1r6_bathroom'].fillna(0)
    df['r1r6_interior'] = df['r1r6_interior'].fillna(0)
    df['style'] = df['style'].fillna("Not set")

    #Get just the columns we need
    clean_df = df[['city', 'neighborhood', 'region', 'style', 'property_type', 'price', 'square_meters', 'bedrooms', 'bathrooms', 'r1r6_property', 'r1r6_kitchen', 'r1r6_bathroom', 'r1r6_interior', 'images']]

    return clean_df


class ImageChooser(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedSize(670, 500)

        df = pd.read_json('../restbai/hackupc2023_restbai__dataset/hackupc2023_restbai__dataset_sample.json', encoding='utf-8')
        self.data = format_table()
        self.userMatrix = [[]]
        self.centroid = []

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
        self.array1_layout.addWidget(self.array1_prev_button)
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

        # set the initial images to be displayed
        self.current_array1_idx = 0
        self.current_array2_idx = 0
        self.set_image(self.array1_images[self.current_array1_idx], self.array1_label)
        self.set_image(self.array2_images[self.current_array2_idx], self.array2_label)

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
            border-radius: 5px;
            padding: 5px;
            """)
        self.array2_label.setStyleSheet("""
            border: 2px solid #3D9970;
            border-radius: 5px;
            padding: 5px;
            """)

    def extract_features(house):
        feat_list = []
        feat_list.append(house['city'])
        feat_list.append(house['neighborhood'])
        feat_list.append(house['region'])
        feat_list.append(house['price'])
        feat_list.append(house['square_meters'])
        feat_list.append(house['bedrooms'])
        feat_list.append(house['bathrooms'])

        #R1R6
        feat_list.append(house['image_data']['r1r6']['property'])
        feat_list.append(house['image_data']['r1r6']['kitchen'])
        feat_list.append(house['image_data']['r1r6']['bathroom'])
        feat_list.append(house['image_data']['r1r6']['interior'])

        #Style
        feat_list.append(house['image_data']['style']['label'])
        feat_list.append(house['property_type'])

        print(feat_list)
    def vote_for_array1(self):
        self.userMatrix.append(self.house1)

        # Create a Gower distance matrix
        gower_dist = gower.gower_matrix(self.data)
        self.centroid = np.mean(gower_dist, axis=0)
        print("Centroid")
        print(self.centroid)
        print("User Matrix")
        print(self.userMatrix)
        #Me pasa los datos de la casa
        #Sacar urls
        #Cargar img
        self.load_images_op1()
        # TODO: replace this with your own code to handle voting for array 1
        print("Voted for array 1")

    def vote_for_array2(self):
        self.userMatrix.append(self.house2)
        # Create a Gower distance matrix
        gower_dist = gower.gower_matrix(self.data)
        self.centroid = np.mean(gower_dist, axis=0)
        # self.load_images()
        self.load_images_op2()
        # TODO: replace this with your own code to handle voting for array 2
        print("Voted for array 2")

    def load_images_op1(self):
        # TODO: replace this with your own code to load the images for both arrays
        #self.array1_images = [QPixmap(f'cats/cat.{i}.jpg')]
        self.array1_images = []

        for i, url in enumerate(self.house1['images']):
            # Realiza una solicitud a la URL y obtiene los datos de la imagen
            response = requests.get(url)
            image_data = response.content

            # Crea un QPixmap desde los datos de la imagen
            pixmap = QPixmap()
            pixmap.loadFromData(image_data)
            self.array1_images.append(pixmap)

    def load_images_op2(self):
        self.array2_images = []

        for i, url in enumerate(self.house2['images']):
            # Realiza una solicitud a la URL y obtiene los datos de la imagen
            response = requests.get(url)
            image_data = response.content

            # Crea un QPixmap desde los datos de la imagen
            pixmap = QPixmap()
            pixmap.loadFromData(image_data)
            self.array2_images.append(pixmap)

    def set_image(self, pixmap, label):
        # set the image in the given label and scale it to fit the label size
        label.setPixmap(pixmap.scaled(label.size(), Qt.KeepAspectRatio))

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

