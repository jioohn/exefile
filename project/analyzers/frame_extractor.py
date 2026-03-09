"""Frame extraction tool for saving video frames as images."""

import cv2

from project.analyzers.base_analyzer import BaseAnalyzer, AnalysisResult
from project.core.video_handler import VideoHandler
from project.core.file_manager import FileManager


class FrameExtractor(BaseAnalyzer):
    """Extract and save all video frames as image files.

    Each frame is saved as a numbered JPEG image in the frames folder.
    Useful for frame-by-frame analysis, manual inspection, or as input
    for other image processing pipelines.
    """

    def get_name(self) -> str:
        """Return display name for GUI button."""
        return "Extract Frames"

    @property
    def description(self) -> str:
        """Return tool description for GUI tooltip."""
        return "Save all video frames as JPEG images"

    def analyze(self, video_path: str) -> AnalysisResult:
        """Extract and save all frames from video.

        Args:
            video_path: Path to the video file.

        Returns:
            AnalysisResult with frame extraction metadata.

        Raises:
            FileNotFoundError: If video not found.
            ValueError: If video is invalid or cannot be saved.
        """
        with VideoHandler(video_path) as handler:
            fps = handler.fps
            file_manager = FileManager()

            # Ensure frames folder exists
            file_manager.ensure_folder("frames")

            frame_files = []
            for frame_index, frame in handler.iter_frames():
                # Create filename with zero-padded index
                filename = f"frame_{frame_index:06d}.jpg"

                try:
                    output_path = file_manager.save_frame(frame, filename)
                    frame_files.append(output_path)
                except IOError as e:
                    raise ValueError(f"Failed to save frame {frame_index}: {e}")

            # Return result with metadata about extraction
            return AnalysisResult(
                name=self.get_name(),
                timestamps=[],
                events=[
                    {
                        "type": "frames_extracted",
                        "count": len(frame_files),
                        "location": file_manager.get_folder_path("frames")
                    }
                ],
                metadata={
                    "fps": fps,
                    "total_frames": handler.total_frames,
                    "frames_saved": len(frame_files),
                    "output_folder": file_manager.get_folder_path("frames")
                }
            )
