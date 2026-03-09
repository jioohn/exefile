"""Base class and data structures for all video analyzers."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any


@dataclass
class AnalysisResult:
    """Standardized output from any analyzer.

    All analyzers return results in this format, allowing for consistent
    handling of results by the UI layer and file management utilities.
    """

    name: str
    """Display name of the analyzer tool."""

    timestamps: List[float]
    """Critical time points of interest (in seconds).

    For shot detection: times of transitions.
    For face detection: times when faces appear.
    For motion detection: times of significant motion events.
    """

    events: List[Dict[str, Any]]
    """Structured events with metadata.

    Each event should be a dict containing at minimum:
        - 'type': str - event type (e.g., 'shot_change', 'face_detected')
        - 'time': float - time in seconds

    Example:
        [
            {'type': 'shot_change', 'time': 2.5, 'reason': 'cut'},
            {'type': 'dissolve', 'time': 7.3, 'duration': 0.8},
        ]
    """

    score_list: Optional[List[float]] = None
    """Optional: continuous scores over time (for plotting/analysis).

    Example: difference value for each frame in shot detection.
    Length should match total frames in video.
    """

    time_list: Optional[List[float]] = None
    """Optional: time points corresponding to score_list values.

    Must be same length as score_list if both provided.
    Times in seconds.
    """

    metadata: Dict[str, Any] = field(default_factory=dict)
    """Tool-specific metadata for reproducibility.

    Should include:
        - 'fps': frames per second
        - 'total_frames': total frame count
        - 'parameters': dict of analyzer parameters used

    Example:
        {
            'fps': 30,
            'total_frames': 1500,
            'parameters': {'threshold': 6, 'min_gap_seconds': 0.5}
        }
    """

    def __post_init__(self):
        """Validate result consistency."""
        if self.score_list is not None and self.time_list is not None:
            if len(self.score_list) != len(self.time_list):
                raise ValueError(
                    f"score_list ({len(self.score_list)}) and time_list "
                    f"({len(self.time_list)}) must have same length"
                )

        if not all("time" in e for e in self.events):
            raise ValueError("All events must have 'time' field")

        if not all("type" in e for e in self.events):
            raise ValueError("All events must have 'type' field")


class BaseAnalyzer(ABC):
    """Abstract base class for all video analysis tools.

    Any new analyzer should inherit from this class and implement
    the abstract methods. This ensures compatibility with the GUI
    registration framework and consistent output format.

    Example:
        class MyNewTool(BaseAnalyzer):
            def get_name(self) -> str:
                return "My Tool"

            def analyze(self, video_path: str) -> AnalysisResult:
                # Implementation
                pass
    """

    @abstractmethod
    def get_name(self) -> str:
        """Return the display name of this analyzer tool.

        This name appears as the button text in the GUI.

        Returns:
            str: Display name for the tool.

        Example:
            "Binary Shot Detector"
        """
        pass

    @property
    def description(self) -> str:
        """Return the tool description for GUI tooltip.

        Optional: Override to provide detailed description.
        Default is empty string.

        Returns:
            str: Description of what the tool does.
        """
        return ""

    @abstractmethod
    def analyze(self, video_path: str) -> AnalysisResult:
        """Run analysis on a video file.

        This is the main entry point for analysis. Implement your
        computer vision algorithm here.

        Args:
            video_path: Path to the video file to analyze.

        Returns:
            AnalysisResult: Structured results of the analysis.

        Raises:
            FileNotFoundError: If video file does not exist.
            ValueError: If video is corrupted or invalid.
            Exception: Any other errors during analysis.

        Note:
            - Do not update UI or perform I/O in this method.
            - Keep it pure: same input should always give same output.
            - Return should be comprehensive for reproducibility.
        """
        pass
