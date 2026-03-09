"""Binary shot detector using frame difference analysis."""

import cv2
import numpy as np
import os

from project.analyzers.base_analyzer import BaseAnalyzer, AnalysisResult
from project.core.video_handler import VideoHandler
from project.core.file_manager import FileManager
from project.ui.image_display_window import ImageDisplayWindow


# Configuration constants
SHOT_CHANGE_THRESHOLD = 6
MIN_SHOT_GAP_SECONDS = 0.5


class BinaryShotDetector(BaseAnalyzer):
    """Detect scene changes using binary frame comparison.

    Analyzes the video frame-by-frame, comparing binary representations
    to identify shot transitions and dissolves. This detector works by:

    1. Converting each frame to grayscale
    2. Applying binary thresholding
    3. Computing frame-to-frame difference
    4. Detecting significant changes as shot transitions

    Attributes:
        threshold: Difference threshold for detecting shot changes.
        min_gap_seconds: Minimum time between detected transitions
                        (to filter noise and rapid flickers).
    """

    def __init__(
        self,
        threshold: int = SHOT_CHANGE_THRESHOLD,
        min_gap_seconds: float = MIN_SHOT_GAP_SECONDS,
        show_visualization: bool = True
    ):
        """Initialize Binary Shot Detector.

        Args:
            threshold: Difference threshold for shot detection. Defaults to 6.
            min_gap_seconds: Minimum gap between shot changes in seconds.
                            Defaults to 0.5.
            show_visualization: Show original/binary frames during analysis.
                               Defaults to True.
        """
        self.threshold = threshold
        self.min_gap_seconds = min_gap_seconds
        self.show_visualization = show_visualization
        self.display_window = None

    def get_name(self) -> str:
        """Return display name for GUI button."""
        return "Binary Shot Detector"

    @property
    def description(self) -> str:
        """Return tool description for GUI tooltip."""
        return "Detect scene cuts and dissolves using binary frame comparison"

    def analyze(self, video_path: str) -> AnalysisResult:
        """Detect shot changes in video using binary frame analysis.

        Args:
            video_path: Path to the video file.

        Returns:
            AnalysisResult containing detected transitions and analysis data.

        Raises:
            FileNotFoundError: If video not found.
            ValueError: If video is invalid (fps=0, etc.).
        """
        # Create display window if visualization enabled
        if self.show_visualization:
            self.display_window = ImageDisplayWindow("Binary Shot Detector - Analysis")
            self.display_window.show()

        with VideoHandler(video_path) as handler:
            fps = handler.fps
            if fps == 0:
                raise ValueError(f"Invalid video: fps = 0")

            # Initialize tracking variables
            shot_changes = []
            dissolves = []
            all_changes = []
            scores = []
            times = []
            last_change_time = 0.0

            # Read first frame for comparison
            _, previous_frame = handler.get_frame(0)
            if previous_frame is None:
                raise ValueError("Cannot read first frame from video")

            previous_binary = self._frame_to_binary(previous_frame)

            # Process remaining frames
            for frame_index, frame in handler.iter_frames():
                if frame_index == 0:
                    continue  # Already processed first frame

                # Convert frame to binary
                current_binary = self._frame_to_binary(frame)

                # Display current frame and binary in separate window
                if self.show_visualization and self.display_window:
                    self.display_window.display_side_by_side(frame, current_binary)
                    # Process Qt events to keep window responsive
                    from PyQt5.QtWidgets import QApplication
                    QApplication.processEvents()

                # Compute frame difference
                difference = cv2.absdiff(current_binary, previous_binary)
                change_score = np.mean(difference)

                # Record score and time for plotting
                scores.append(change_score)
                times.append(frame_index / fps)

                # Check if this is a significant change
                if change_score > self.threshold:
                    current_time = frame_index / fps

                    # Respect minimum gap between detections
                    if current_time - last_change_time >= self.min_gap_seconds:
                        binary_mean = np.mean(current_binary)

                        # Classify as dissolve or cut
                        if binary_mean > 50:
                            event = {
                                "type": "dissolve",
                                "time": current_time,
                                "frame": frame_index,
                                "score": float(change_score)
                            }
                            dissolves.append(current_time)
                        else:
                            event = {
                                "type": "shot_change",
                                "time": current_time,
                                "frame": frame_index,
                                "score": float(change_score)
                            }
                            shot_changes.append(current_time)

                        all_changes.append(event)
                        last_change_time = current_time

                # Move to next frame
                previous_binary = current_binary

            # Compile final events and metadata
            final_time = handler.total_frames / fps
            all_changes.append({
                "type": "end",
                "time": final_time,
                "frame": handler.total_frames
            })

            events = all_changes
            timestamps = shot_changes + dissolves
            timestamps.sort()

            # Create video clips from detected shots
            clips_info = self._create_clips(video_path, timestamps, fps)

            return AnalysisResult(
                name=self.get_name(),
                timestamps=timestamps,
                events=events,
                score_list=scores,
                time_list=times,
                metadata={
                    "fps": fps,
                    "total_frames": handler.total_frames,
                    "duration_seconds": final_time,
                    "shot_changes": len(shot_changes),
                    "dissolves": len(dissolves),
                    "clips_created": clips_info["count"],
                    "clips_folder": clips_info["folder"],
                    "parameters": {
                        "threshold": self.threshold,
                        "min_gap_seconds": self.min_gap_seconds
                    }
                }
            )

    @staticmethod
    def _frame_to_binary(frame: np.ndarray) -> np.ndarray:
        """Convert frame to binary image for comparison.

        Args:
            frame: BGR frame from OpenCV.

        Returns:
            Binary image (0s and 255s).
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        _, binary = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY)
        return binary

    @staticmethod
    def _create_clips(video_path: str, timestamps: list, fps: float) -> dict:
        """Split video into clips based on shot transition times.

        Args:
            video_path: Path to the video file.
            timestamps: List of transition times in seconds.
            fps: Frames per second of the video.

        Returns:
            Dict with clip creation info (count, folder).
        """
        # Ensure clips folder exists
        file_manager = FileManager()
        clips_folder = file_manager.ensure_folder("clips")

        # Open video for reading
        cap = cv2.VideoCapture(video_path)
        frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')

        # Sort timestamps and add 0 at start for first clip
        times = [0.0] + sorted(timestamps)

        clip_count = 0

        # Create clips between each timestamp
        for i in range(len(times) - 1):
            start_time = times[i]
            end_time = times[i + 1]

            # Create output filename
            clip_number = i + 1
            clip_filename = os.path.join(clips_folder, f"clip_{clip_number:03d}.mp4")

            # Create video writer
            out = cv2.VideoWriter(clip_filename, fourcc, fps, (frame_width, frame_height))

            if not out.isOpened():
                continue

            # Set start frame
            start_frame = int(start_time * fps)
            end_frame = int(end_time * fps)

            cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)

            # Write frames for this clip
            frame_count = 0
            while frame_count < (end_frame - start_frame):
                ret, frame = cap.read()
                if not ret:
                    break

                out.write(frame)
                frame_count += 1

            out.release()
            clip_count += 1

        cap.release()

        return {
            "count": clip_count,
            "folder": clips_folder
        }
