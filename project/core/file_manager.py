"""File management and output folder handling."""

import os
from pathlib import Path
from typing import List
import cv2
import matplotlib.pyplot as plt
import numpy as np


class FileManager:
    """Manages output folders and files for analysis results.

    Handles creation of output directories, saving frames, clips,
    plots, and time files in an organized manner.

    Example:
        fm = FileManager("./output")
        fm.ensure_folder("frames")
        fm.save_frame(frame, "frame_001.jpg")
        fm.save_times([1.5, 3.2, 5.8])
    """

    def __init__(self, base_dir: str = "."):
        """Initialize FileManager with base directory.

        Args:
            base_dir: Base directory for all output. Defaults to current dir.
        """
        self.base_dir = os.path.abspath(base_dir)
        self.folders = {
            "frames": os.path.join(self.base_dir, "frames"),
            "clips": os.path.join(self.base_dir, "clips"),
            "plots": os.path.join(self.base_dir, "plots"),
        }

    def ensure_folder(self, folder_type: str) -> str:
        """Create folder if it doesn't exist.

        Args:
            folder_type: Type of folder ('frames', 'clips', 'plots').

        Returns:
            str: Path to the folder.

        Raises:
            KeyError: If folder_type is not recognized.
            OSError: If folder cannot be created.
        """
        if folder_type not in self.folders:
            raise KeyError(
                f"Unknown folder type: {folder_type}. "
                f"Must be one of: {list(self.folders.keys())}"
            )

        folder_path = self.folders[folder_type]
        os.makedirs(folder_path, exist_ok=True)
        return folder_path

    def get_folder_path(self, folder_type: str) -> str:
        """Get path to output folder (creates if needed).

        Args:
            folder_type: Type of folder ('frames', 'clips', 'plots').

        Returns:
            str: Absolute path to the folder.
        """
        return self.ensure_folder(folder_type)

    def save_frame(
        self,
        frame: np.ndarray,
        filename: str,
        folder: str = "frames"
    ) -> str:
        """Save a frame as an image file.

        Args:
            frame: BGR numpy array from OpenCV.
            filename: Filename (e.g., 'frame_001.jpg').
            folder: Output folder type. Defaults to 'frames'.

        Returns:
            str: Full path to saved file.

        Raises:
            ValueError: If frame is invalid.
        """
        if frame is None or frame.size == 0:
            raise ValueError("Invalid frame: empty or None")

        folder_path = self.ensure_folder(folder)
        output_path = os.path.join(folder_path, filename)

        success = cv2.imwrite(output_path, frame)
        if not success:
            raise IOError(f"Failed to write frame to {output_path}")

        return output_path

    def save_times(
        self,
        times: List[float],
        filename: str = "times.txt",
        overwrite: bool = False
    ) -> str:
        """Save shot transition times to file.

        Each time on a new line, formatted as float.

        Args:
            times: List of times in seconds.
            filename: Output filename. Defaults to 'times.txt'.
            overwrite: If False, append to existing file. If True, replace.

        Returns:
            str: Full path to times file.
        """
        times_path = os.path.join(self.base_dir, filename)

        mode = "w" if overwrite else "a"
        with open(times_path, mode) as f:
            for t in times:
                f.write(f"{float(t)}\n")

        return times_path

    def load_times(self, filename: str = "times.txt") -> List[float]:
        """Load shot transition times from file.

        Args:
            filename: Input filename. Defaults to 'times.txt'.

        Returns:
            List of times in seconds.

        Raises:
            FileNotFoundError: If file does not exist.
        """
        times_path = os.path.join(self.base_dir, filename)

        if not os.path.exists(times_path):
            raise FileNotFoundError(f"Times file not found: {times_path}")

        times = []
        with open(times_path, "r") as f:
            for line in f:
                try:
                    times.append(float(line.strip()))
                except ValueError:
                    continue  # Skip invalid lines

        return sorted(times)

    def save_plot(
        self,
        fig: plt.Figure,
        filename: str,
        folder: str = "plots",
        dpi: int = 100
    ) -> str:
        """Save matplotlib figure to file.

        Args:
            fig: Matplotlib figure object.
            filename: Filename (e.g., 'analysis.png').
            folder: Output folder type. Defaults to 'plots'.
            dpi: Resolution in dots per inch. Defaults to 100.

        Returns:
            str: Full path to saved plot.
        """
        folder_path = self.ensure_folder(folder)
        output_path = os.path.join(folder_path, filename)

        fig.savefig(output_path, dpi=dpi, bbox_inches="tight")
        return output_path

    def clear_folder(self, folder_type: str) -> None:
        """Clear all files from a folder.

        Args:
            folder_type: Type of folder to clear.

        Warning:
            This deletes all files in the folder. Use with caution.
        """
        folder_path = self.folders.get(folder_type)
        if not folder_path or not os.path.exists(folder_path):
            return

        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            try:
                if os.path.isfile(file_path):
                    os.remove(file_path)
            except Exception as e:
                print(f"Failed to delete {file_path}: {e}")

    def get_frames_list(self, extension: str = "*.jpg") -> List[str]:
        """Get list of extracted frame files.

        Args:
            extension: File extension to filter (e.g., '*.jpg').

        Returns:
            List of frame file paths, sorted.
        """
        frames_path = self.get_folder_path("frames")
        frame_files = list(Path(frames_path).glob(extension))
        return sorted([str(f) for f in frame_files])

    def __repr__(self) -> str:
        """String representation."""
        return f"FileManager(base_dir={self.base_dir!r})"
