"""Application entry point for Video Analyzer."""

import sys
from project.ui.video_player_gui import VideoPlayerGUI
from PyQt5.QtWidgets import QApplication


def main():
    """Run the Video Analyzer application."""
    app = QApplication(sys.argv)
    window = VideoPlayerGUI()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
