"""Video I/O abstraction using OpenCV."""

import os
from typing import Generator, Tuple, Optional
import cv2
import numpy as np


class VideoHandler:
    """Abstraction layer for video I/O using OpenCV.

    Provides a consistent interface for reading video files and accessing
    frame data, FPS, dimensions, and other metadata.

    Example:
        with VideoHandler("video.mp4") as handler:
            print(f"FPS: {handler.fps}")
            for frame_num, frame in handler.iter_frames():
                # Process frame
                pass
    """

    def __init__(self, video_path: str):
        """Initialize video handler for a video file.

        Args:
            video_path: Path to the video file.

        Raises:
            FileNotFoundError: If video file does not exist.
        """
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")

        self.path = video_path
        self._cap = cv2.VideoCapture(video_path)

        if not self._cap.isOpened():
            raise ValueError(f"Cannot open video file: {video_path}")

    @property
    def fps(self) -> float:
        """Get frames per second of the video.

        Returns:
            float: Frames per second.
        """
        return float(self._cap.get(cv2.CAP_PROP_FPS))

    @property
    def total_frames(self) -> int:
        """Get total number of frames in the video.

        Returns:
            int: Total frame count.
        """
        return int(self._cap.get(cv2.CAP_PROP_FRAME_COUNT))

    @property
    def width(self) -> int:
        """Get frame width in pixels.

        Returns:
            int: Frame width.
        """
        return int(self._cap.get(cv2.CAP_PROP_FRAME_WIDTH))

    @property
    def height(self) -> int:
        """Get frame height in pixels.

        Returns:
            int: Frame height.
        """
        return int(self._cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    @property
    def duration_seconds(self) -> float:
        """Get total duration of the video in seconds.

        Returns:
            float: Duration in seconds.
        """
        if self.fps == 0:
            return 0.0
        return self.total_frames / self.fps

    def get_frame(self, frame_number: int) -> Tuple[bool, Optional[np.ndarray]]:
        """Get a specific frame from the video.

        Args:
            frame_number: Frame index (0-based).

        Returns:
            Tuple of (success: bool, frame: np.ndarray or None).
            success is True if frame was read successfully, False otherwise.
            frame is BGR numpy array or None if read failed.
        """
        self._cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
        return self._cap.read()

    def iter_frames(self) -> Generator[Tuple[int, np.ndarray], None, None]:
        """Iterate through all frames in the video.

        Yields:
            Tuple of (frame_number: int, frame: np.ndarray).
            frame is in BGR format (OpenCV default).

        Example:
            for frame_num, frame in handler.iter_frames():
                print(f"Processing frame {frame_num}")
        """
        frame_num = 0
        while True:
            ret, frame = self._cap.read()
            if not ret:
                break
            yield frame_num, frame
            frame_num += 1

    def reset(self) -> None:
        """Reset video to first frame for re-iteration."""
        self._cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

    def release(self) -> None:
        """Release video capture resources.

        Should be called when done, or use context manager.
        """
        if self._cap is not None:
            self._cap.release()

    def __enter__(self):
        """Support for context manager (with statement)."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Clean up resources on context manager exit."""
        self.release()

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"VideoHandler({self.path!r}, "
            f"fps={self.fps}, frames={self.total_frames}, "
            f"size={self.width}x{self.height})"
        )
