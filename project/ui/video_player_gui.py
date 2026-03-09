"""Main GUI for Video Analyzer application."""

import os
import subprocess
import cv2
from typing import Optional
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QLineEdit, QSlider, QFileDialog, QStyle, QStatusBar,
    QMessageBox, QScrollArea
)
from PyQt5.QtMultimedia import QMediaPlayer
from PyQt5.QtMultimediaWidgets import QVideoWidget

from project.core.video_handler import VideoHandler
from project.core.file_manager import FileManager
from project.analyzers.base_analyzer import BaseAnalyzer
from project.analyzers.binary_shot_detector import BinaryShotDetector
from project.analyzers.frame_extractor import FrameExtractor
from project.analyzers.luminosity_analyzer import LuminosityAnalyzer


class VideoPlayerGUI(QMainWindow):
    """Main GUI window for Video Analyzer.

    Provides controls for video selection, playback, and analysis.
    Dynamically creates buttons for registered analyzers.
    """

    def __init__(self):
        """Initialize the Video Analyzer GUI."""
        super().__init__()
        self.setWindowTitle("Video Analyzer - Computer Vision Tools")
        self.setGeometry(100, 100, 1000, 700)

        # State variables
        self.video_path: Optional[str] = None
        self.cap: Optional[cv2.VideoCapture] = None
        self.is_playing = False
        self.frame_count = 0
        self.total_frames = 0
        self.last_result = None
        self.playback_timer: Optional[QTimer] = None

        # Core services
        self.file_manager = FileManager()
        self.analyzers: list[BaseAnalyzer] = []

        # Register built-in analyzers
        self._register_builtin_analyzers()

        # Create UI
        self._create_ui()

    def _register_builtin_analyzers(self) -> None:
        """Register default analyzer tools."""
        self.register_analyzer(BinaryShotDetector())
        self.register_analyzer(FrameExtractor())
        self.register_analyzer(LuminosityAnalyzer())

    def register_analyzer(self, analyzer: BaseAnalyzer) -> None:
        """Register an analyzer and create UI button.

        Args:
            analyzer: Analyzer instance to register.
        """
        self.analyzers.append(analyzer)
        # Buttons will be created in _create_analyzer_buttons()

    def _create_ui(self) -> None:
        """Create the user interface."""
        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout()

        # Left panel: Video and Controls
        left_panel = QVBoxLayout()

        # Video display label
        self.video_label = QLabel()
        self.video_label.setMinimumHeight(400)
        self.video_label.setScaledContents(False)
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setStyleSheet("background-color: black; color: white;")
        self.video_label.setText("No video loaded")
        left_panel.addWidget(QLabel("Video Display:"))
        left_panel.addWidget(self.video_label)

        # Playback controls
        controls_layout = QHBoxLayout()
        self.play_button = QPushButton("Play")
        self.play_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.play_button.clicked.connect(self.play_video)
        controls_layout.addWidget(self.play_button)

        self.open_button = QPushButton("Select Video")
        self.open_button.clicked.connect(self.open_file)
        controls_layout.addWidget(self.open_button)

        left_panel.addLayout(controls_layout)

        # Frame counter
        left_panel.addWidget(QLabel("Current Frame:"))
        self.frame_display = QLineEdit()
        self.frame_display.setReadOnly(True)
        self.frame_display.setText("No video loaded")
        left_panel.addWidget(self.frame_display)

        # Analysis results display
        left_panel.addWidget(QLabel("Analysis Results:"))
        self.results_display = QLineEdit()
        self.results_display.setReadOnly(True)
        left_panel.addWidget(self.results_display)

        # Right panel: Analyzers (scrollable)
        right_panel_widget = QWidget()
        right_panel_layout = QVBoxLayout()
        right_panel_layout.addWidget(QLabel("Analysis Tools:"))

        # Create analyzer buttons
        self._create_analyzer_buttons(right_panel_layout)

        right_panel_layout.addStretch()
        right_panel_widget.setLayout(right_panel_layout)

        # Scrollable area for right panel
        scroll = QScrollArea()
        scroll.setWidget(right_panel_widget)
        scroll.setWidgetResizable(True)
        scroll.setMaximumWidth(250)

        # Add panels to main layout
        main_layout.addLayout(left_panel, 3)
        main_layout.addWidget(scroll, 1)

        main_widget.setLayout(main_layout)

        # Status bar
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("Ready")

    def _create_analyzer_buttons(self, layout: QVBoxLayout) -> None:
        """Create buttons for all registered analyzers.

        Args:
            layout: Layout to add buttons to.
        """
        for analyzer in self.analyzers:
            button = QPushButton(analyzer.get_name())

            # Add tooltip if description available
            if analyzer.description:
                button.setToolTip(analyzer.description)

            # Connect button to analysis
            button.clicked.connect(lambda checked=False, a=analyzer: self.run_analysis(a))
            layout.addWidget(button)

    def open_file(self) -> None:
        """Open and validate a video file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Video",
            os.getcwd(),
            "Video Files (*.mp4 *.avi *.mov *.mkv);;All Files (*)"
        )

        if not file_path:
            return

        try:
            # Test if OpenCV can open the video
            with VideoHandler(file_path) as handler:
                self.video_path = file_path
                self.total_frames = handler.total_frames
                self.frame_count = 0
                self.file_manager = FileManager(os.path.dirname(file_path))

                self.statusBar.showMessage(
                    f"Loaded: {os.path.basename(file_path)} "
                    f"({self.total_frames} frames, {handler.fps:.1f} fps)"
                )
                self.frame_display.setText(f"0 / {self.total_frames}")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Cannot open video: {str(e)}")
            self.statusBar.showMessage(f"Error: {str(e)}")

    def play_video(self) -> None:
        """Play or pause video."""
        if not self.video_path:
            QMessageBox.warning(self, "Warning", "No video loaded")
            return

        self.is_playing = not self.is_playing

        if self.is_playing:
            self.play_button.setText("Pause")
            self._start_playback()
        else:
            self.play_button.setText("Play")
            if self.playback_timer:
                self.playback_timer.stop()

    def _start_playback(self) -> None:
        """Start video playback using QTimer."""
        if not self.video_path:
            return

        self.cap = cv2.VideoCapture(self.video_path)
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.frame_count)

        # Create and setup timer for frame updates
        self.playback_timer = QTimer()
        self.playback_timer.timeout.connect(self._update_frame)
        self.playback_timer.start(33)  # ~30fps

    def _update_frame(self) -> None:
        """Update video frame display."""
        if not self.is_playing or not self.cap or not self.cap.isOpened():
            self.is_playing = False
            self.play_button.setText("Play")
            if self.playback_timer:
                self.playback_timer.stop()
            self.statusBar.showMessage("Playback finished")
            return

        ret, frame = self.cap.read()

        if not ret:
            # End of video
            self.is_playing = False
            self.play_button.setText("Play")
            if self.playback_timer:
                self.playback_timer.stop()
            self.cap.release()
            self.statusBar.showMessage("Playback finished")
            return

        # Resize frame for display
        display_width = 800
        display_height = 600
        display_frame = cv2.resize(frame, (display_width, display_height))

        # Convert BGR to RGB for display
        rgb_frame = cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB)

        # Convert to QImage
        h, w, ch = rgb_frame.shape
        q_img = QImage(rgb_frame.data, w, h, ch * w, QImage.Format_RGB888)

        # Convert to QPixmap and display
        pixmap = QPixmap.fromImage(q_img)
        self.video_label.setPixmap(pixmap)

        # Update frame counter
        self.frame_count = int(self.cap.get(cv2.CAP_PROP_POS_FRAMES))
        self.frame_display.setText(f"{self.frame_count} / {self.total_frames}")
        self.statusBar.showMessage(f"Playing: {self.frame_count}/{self.total_frames}")

    def run_analysis(self, analyzer: BaseAnalyzer) -> None:
        """Run an analyzer on the loaded video.

        Args:
            analyzer: Analyzer to run.
        """
        if not self.video_path:
            QMessageBox.warning(self, "Warning", "No video loaded")
            return

        try:
            self.statusBar.showMessage(f"Running {analyzer.get_name()}...")

            # Run analyzer
            result = analyzer.analyze(self.video_path)
            self.last_result = result

            # Save times if available
            if result.timestamps:
                self.file_manager.save_times(result.timestamps, overwrite=True)

            # Update UI
            message = (
                f"{analyzer.get_name()}: {len(result.events)} events detected. "
                f"Transitions at: {[f'{t:.2f}s' for t in result.timestamps[:5]]}"
            )
            if len(result.timestamps) > 5:
                message += f" + {len(result.timestamps) - 5} more"

            # Check if plot was generated
            if result.metadata.get("plot_file"):
                plot_path = result.metadata["plot_file"]
                message += f"\n[PLOT] Saved to: {plot_path}"
                # Auto-open the plot
                self._open_file(plot_path)

            self.results_display.setText(message)

            # Show completion message with metadata
            completion_msg = f"✓ {analyzer.get_name()} completed"
            if "duration_seconds" in result.metadata:
                completion_msg += f" ({result.metadata['duration_seconds']:.1f}s video)"
            self.statusBar.showMessage(completion_msg)

        except Exception as e:
            error_msg = f"Analysis error: {str(e)}"
            QMessageBox.critical(self, "Error", error_msg)
            self.statusBar.showMessage(f"✗ {error_msg}")

    def closeEvent(self, event):
        """Clean up resources on window close."""
        if self.playback_timer:
            self.playback_timer.stop()
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()
        event.accept()

    @staticmethod
    def _open_file(file_path: str) -> None:
        """Open a file with the default system application.

        Args:
            file_path: Path to the file to open.
        """
        try:
            if not os.path.exists(file_path):
                return

            # Platform-specific file opening
            if os.name == 'nt':  # Windows
                os.startfile(file_path)
            elif os.name == 'posix':  # macOS and Linux
                subprocess.Popen(['xdg-open' if os.uname()[0] != 'Darwin' else 'open', file_path])
        except Exception as e:
            # Silently fail - plot was still saved, just couldn't open it
            pass
