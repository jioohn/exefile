"""Luminosity analyzer for measuring frame brightness over time."""

import cv2
import numpy as np
import matplotlib.pyplot as plt

from project.analyzers.base_analyzer import BaseAnalyzer, AnalysisResult
from project.core.video_handler import VideoHandler
from project.core.file_manager import FileManager


class LuminosityAnalyzer(BaseAnalyzer):
    """Analyze brightness/luminosity of video frames over time.

    Measures the average brightness (luminosity) of each frame in the video
    and generates a plot showing how brightness changes throughout the video.

    Useful for:
    - Detecting lighting changes
    - Identifying fade-in/fade-out effects
    - Analyzing scene lighting consistency
    - Detecting exposure issues

    Luminosity is calculated as the mean intensity of the frame after
    converting to grayscale (range 0-255, where 0 is black, 255 is white).
    """

    def get_name(self) -> str:
        """Return display name for GUI button."""
        return "Brightness Analysis"

    @property
    def description(self) -> str:
        """Return tool description for GUI tooltip."""
        return "Measure and plot frame brightness over time"

    def analyze(self, video_path: str) -> AnalysisResult:
        """Analyze luminosity (brightness) of all frames.

        Args:
            video_path: Path to the video file.

        Returns:
            AnalysisResult containing brightness scores and plot.

        Raises:
            FileNotFoundError: If video not found.
            ValueError: If video is invalid.
        """
        with VideoHandler(video_path) as handler:
            fps = handler.fps
            if fps == 0:
                raise ValueError("Invalid video: fps = 0")

            luminosity_scores = []
            times = []
            brightness_events = []

            # Find min and max luminosity for event detection
            min_luminosity = 255
            max_luminosity = 0

            # First pass: collect all luminosity values
            for frame_index, frame in handler.iter_frames():
                luminosity = self._calculate_luminosity(frame)
                luminosity_scores.append(luminosity)
                times.append(frame_index / fps)

                min_luminosity = min(min_luminosity, luminosity)
                max_luminosity = max(max_luminosity, luminosity)

            # Second pass: detect significant brightness transitions
            threshold = (max_luminosity - min_luminosity) * 0.3  # 30% of range

            for i in range(1, len(luminosity_scores)):
                change = abs(luminosity_scores[i] - luminosity_scores[i - 1])

                if change > threshold:
                    event_type = (
                        "fade_in" if luminosity_scores[i] > luminosity_scores[i - 1]
                        else "fade_out"
                    )

                    brightness_events.append({
                        "type": event_type,
                        "time": times[i],
                        "frame": i,
                        "brightness_before": float(luminosity_scores[i - 1]),
                        "brightness_after": float(luminosity_scores[i]),
                        "change": float(change)
                    })

            # Create plot
            plot_path = self._create_plot(
                times,
                luminosity_scores,
                video_path,
                min_luminosity,
                max_luminosity
            )

            # Extract timestamps for significant events
            event_times = [e["time"] for e in brightness_events]

            return AnalysisResult(
                name=self.get_name(),
                timestamps=event_times,
                events=brightness_events,
                score_list=luminosity_scores,
                time_list=times,
                metadata={
                    "fps": fps,
                    "total_frames": handler.total_frames,
                    "duration_seconds": handler.total_frames / fps,
                    "min_luminosity": float(min_luminosity),
                    "max_luminosity": float(max_luminosity),
                    "avg_luminosity": float(np.mean(luminosity_scores)),
                    "brightness_changes": len(brightness_events),
                    "plot_file": plot_path
                }
            )

    @staticmethod
    def _calculate_luminosity(frame: np.ndarray) -> float:
        """Calculate average luminosity (brightness) of a frame.

        Converts frame to grayscale and returns the mean pixel intensity.

        Args:
            frame: BGR frame from OpenCV.

        Returns:
            Luminosity value (0-255, where 0 is black, 255 is white).
        """
        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Return mean intensity
        return float(np.mean(gray))

    @staticmethod
    def _create_plot(
        times: list,
        luminosity_scores: list,
        video_path: str,
        min_lum: float,
        max_lum: float
    ) -> str:
        """Create and save luminosity plot.

        Args:
            times: List of time points (seconds).
            luminosity_scores: List of luminosity values.
            video_path: Original video path (for reference).
            min_lum: Minimum luminosity for y-axis.
            max_lum: Maximum luminosity for y-axis.

        Returns:
            Path to saved plot file.
        """
        fig, ax = plt.subplots(figsize=(14, 6))

        # Plot luminosity over time
        ax.plot(times, luminosity_scores, linewidth=2, color='#3498db', label='Luminosity')

        # Add reference lines
        ax.axhline(y=np.mean(luminosity_scores), color='green', linestyle='--',
                   linewidth=1, alpha=0.7, label='Average')

        # Styling
        ax.set_xlabel('Time (seconds)', fontsize=12)
        ax.set_ylabel('Brightness (0-255)', fontsize=12)
        ax.set_title('Video Luminosity Over Time', fontsize=14, fontweight='bold')
        ax.set_ylim(-10, 265)
        ax.grid(True, alpha=0.3)
        ax.legend(loc='upper right', fontsize=10)

        # Tight layout
        plt.tight_layout()

        # Save plot
        file_manager = FileManager()
        plot_path = file_manager.save_plot(fig, "luminosity_over_time.png")

        plt.close(fig)

        return plot_path
