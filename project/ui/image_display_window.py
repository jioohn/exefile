"""Reusable window for displaying processed images and video frames."""

import cv2
import numpy as np
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtWidgets import QMainWindow, QLabel, QHBoxLayout, QWidget


class ImageDisplayWindow(QMainWindow):
    """Window for displaying processed images or video frames.

    Useful for visualization of CV analysis results like:
    - Binary thresholding
    - Motion maps
    - Detected features
    - Side-by-side frame comparisons

    Example:
        window = ImageDisplayWindow("Binary Analysis")
        window.display_image(binary_frame)
        window.show()
    """

    def __init__(self, title: str = "Image Display"):
        """Initialize the image display window.

        Args:
            title: Window title.
        """
        super().__init__()
        self.setWindowTitle(title)
        self.setGeometry(100, 100, 1200, 700)

        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.layout = QHBoxLayout()
        central_widget.setLayout(self.layout)

        # Image labels (for side-by-side display)
        self.label1 = QLabel()
        self.label1.setAlignment(Qt.AlignCenter)
        self.label1.setStyleSheet("background-color: black;")
        self.layout.addWidget(self.label1)

        self.label2 = QLabel()
        self.label2.setAlignment(Qt.AlignCenter)
        self.label2.setStyleSheet("background-color: black;")
        self.label2.setVisible(False)
        self.layout.addWidget(self.label2)

    def display_image(self, image: np.ndarray, position: int = 1) -> None:
        """Display a single image.

        Args:
            image: Image as numpy array (BGR or grayscale).
            position: Position to display (1=left, 2=right). Defaults to 1.
        """
        if image is None:
            return

        # Convert grayscale to RGB if needed
        if len(image.shape) == 2:
            image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
        elif image.shape[2] == 3:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Convert to QImage
        h, w = image.shape[:2]
        bytes_per_line = 3 * w
        q_img = QImage(image.data, w, h, bytes_per_line, QImage.Format_RGB888)

        # Convert to QPixmap
        pixmap = QPixmap.fromImage(q_img)

        # Display in appropriate label
        if position == 1:
            self.label1.setPixmap(pixmap)
        elif position == 2:
            self.label2.setPixmap(pixmap)
            self.label2.setVisible(True)

    def display_side_by_side(self, image1: np.ndarray, image2: np.ndarray) -> None:
        """Display two images side-by-side.

        Args:
            image1: Left image as numpy array.
            image2: Right image as numpy array.
        """
        self.display_image(image1, position=1)
        self.display_image(image2, position=2)

    def display_images_grid(self, images: list, cols: int = 2) -> None:
        """Display multiple images in a grid layout.

        Note: Current implementation shows first two images side-by-side.
        For more images, extend this method.

        Args:
            images: List of numpy arrays (images).
            cols: Number of columns in grid.
        """
        if len(images) >= 1:
            self.display_image(images[0], position=1)
        if len(images) >= 2:
            self.display_image(images[1], position=2)
