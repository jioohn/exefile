# Code Conventions and Style Guide

## Python Style

Follow **PEP 8** with these specific guidelines:

### Naming Conventions

| Element | Convention | Example |
|---------|-----------|---------|
| Classes | PascalCase | `BinaryShotDetector`, `VideoHandler` |
| Functions/Methods | snake_case | `analyze()`, `extract_frames()`, `get_name()` |
| Constants | UPPER_SNAKE_CASE | `DEFAULT_THRESHOLD = 6` |
| Private methods | _snake_case | `_process_frame()` |
| Boolean variables | is_ / has_ prefixes | `is_playing`, `has_frames` |

### Type Hints

All functions should have type hints:

```python
# ✓ Good
def analyze(self, video_path: str) -> AnalysisResult:
    pass

def get_frame(self, index: int) -> tuple[bool, np.ndarray]:
    pass

def iter_frames(self) -> Generator[tuple[int, np.ndarray], None, None]:
    pass

# ✗ Bad
def analyze(self, video_path):
    pass
```

### Docstrings

Use Google-style docstrings:

```python
def analyze(self, video_path: str) -> AnalysisResult:
    """Detect scene changes using binary frame comparison.

    Analyzes the video frame-by-frame, comparing binary representations
    to identify shot transitions and dissolves.

    Args:
        video_path: Path to the video file to analyze.

    Returns:
        AnalysisResult containing detected transitions and analysis metadata.

    Raises:
        FileNotFoundError: If video_path does not exist.
        ValueError: If video file is corrupted or unreadable.
    """
    pass
```

### Imports

Organization order:
1. Standard library
2. Third-party packages
3. Local modules

```python
# Standard library
import os
from dataclasses import dataclass
from abc import ABC, abstractmethod

# Third-party
import cv2
import numpy as np
from PyQt5.QtWidgets import QPushButton

# Local
from project.core.file_manager import FileManager
from project.analyzers.base_analyzer import BaseAnalyzer, AnalysisResult
```

---

## Naming Conventions Specific to This Project

### Video Analysis

| Term | Convention | Example |
|------|-----------|---------|
| Shot/scene boundary | Use `shot_change` or `transition` | `events[0]["type"] = "shot_change"` |
| Time in seconds | Suffix `_seconds` or `_time` | `transition_time = 5.2` |
| Frame index | Suffix `_index` or `_number` | `frame_index`, `frame_number` |
| Frame count | `total_frames` or `num_frames` | `video.total_frames` |
| Similarity score | `score`, `similarity`, or `change_value` | `change_score`, `frame_similarity` |

### File Naming

| Content | Pattern | Example |
|---------|---------|---------|
| Extracted frames | `frame_<index>.jpg` | `frame_0.jpg`, `frame_42.jpg` |
| Scene clips | `scene_<number>.mp4` | `scene_1.mp4`, `scene_2.mp4` |
| Plots | `<analysis>_<description>.png` | `binary_score_over_time.png`, `motion_heatmap.png` |
| Output archive | `analysis_<timestamp>.zip` | `analysis_2026_03_09_143022.zip` |

---

## Data Structure Conventions

### AnalysisResult Usage

```python
result = AnalysisResult(
    name="Tool Name",
    timestamps=[t1, t2, t3, ...],           # Key time points
    events=[                                 # Detailed events
        {"type": "shot_change", "time": 2.5, "confidence": 0.95},
        {"type": "dissolve", "time": 7.3, "duration": 0.8},
    ],
    score_list=[s1, s2, s3, ...],           # Continuous scores
    time_list=[t1, t2, t3, ...],            # Corresponding times
    metadata={                               # Tool-specific data
        "total_shots": 5,
        "fps": 30,
        "parameters": {"threshold": 6}
    }
)
```

**Rules:**
- `timestamps`: Critical moments (transitions, key frames)
- `events`: Structured dict with `type` and `time` required
- `score_list/time_list`: Optional, for plotting or detailed analysis
- `metadata`: Any tool-specific data for reproducibility

---

## Analyzer Implementation Template

When creating a new analyzer, follow this template:

```python
"""Module description: what this analyzer does."""

from dataclasses import dataclass
from project.analyzers.base_analyzer import BaseAnalyzer, AnalysisResult
from project.core.video_handler import VideoHandler


class MyNewTool(BaseAnalyzer):
    """Brief description of the tool.

    Longer description of what it does, what algorithms it uses,
    any parameters, etc.
    """

    def __init__(self, param1: float = 0.5, param2: int = 10):
        """Initialize analyzer with parameters.

        Args:
            param1: Description of param1. Defaults to 0.5.
            param2: Description of param2. Defaults to 10.
        """
        self.param1 = param1
        self.param2 = param2

    def get_name(self) -> str:
        """Return display name for GUI button."""
        return "My New Tool"

    @property
    def description(self) -> str:
        """Return tool description for GUI tooltip."""
        return "Detailed description of what this tool analyzes"

    def analyze(self, video_path: str) -> AnalysisResult:
        """Run analysis on video.

        Args:
            video_path: Path to the video file.

        Returns:
            AnalysisResult with detected events and metadata.

        Raises:
            FileNotFoundError: If video not found.
            ValueError: If video is invalid.
        """
        with VideoHandler(video_path) as handler:
            events = []
            scores = []
            times = []

            for frame_index, frame in handler.iter_frames():
                # Your CV logic here
                event = self._process_frame(frame, frame_index)
                if event:
                    events.append(event)

                score = self._compute_score(frame)
                scores.append(score)
                times.append(frame_index / handler.fps)

        return AnalysisResult(
            name=self.get_name(),
            timestamps=[e["time"] for e in events],
            events=events,
            score_list=scores,
            time_list=times,
            metadata={
                "fps": handler.fps,
                "total_frames": handler.total_frames,
                "parameters": {
                    "param1": self.param1,
                    "param2": self.param2,
                }
            }
        )

    def _process_frame(self, frame: np.ndarray, frame_index: int) -> dict:
        """Process single frame and return event if relevant.

        Args:
            frame: The video frame (BGR format from cv2).
            frame_index: Frame number in the video.

        Returns:
            Event dict if something detected, None otherwise.
        """
        # Implementation
        pass

    def _compute_score(self, frame: np.ndarray) -> float:
        """Compute analysis score for the frame.

        Args:
            frame: The video frame.

        Returns:
            Scalar score value.
        """
        # Implementation
        pass
```

---

## Key Principles

### 1. No Magic Numbers
```python
# ✗ Bad
if change > 6:
    # ...

# ✓ Good
SHOT_CHANGE_THRESHOLD = 6
if change > SHOT_CHANGE_THRESHOLD:
    # ...
```

### 2. Context Managers for Resources
```python
# ✗ Bad
handler = VideoHandler(path)
# ... code
handler.release()  # Might not be called if error occurs

# ✓ Good
with VideoHandler(path) as handler:
    # ... code
# Automatically released
```

### 3. Meaningful Variable Names
```python
# ✗ Bad
c = cv2.absdiff(b, p)  # What are b and p?

# ✓ Good
frame_diff = cv2.absdiff(current_binary, previous_binary)
```

### 4. Single Responsibility
```python
# ✗ Bad - Do too much
def analyze_and_save(self, video_path: str):
    # Analysis
    # File I/O
    # UI updates

# ✓ Good - Separate concerns
def analyze(self, video_path: str) -> AnalysisResult:
    # Only analysis
    pass

# FileManager handles saving
# UI handles display
```

### 5. Pure Functions Preferred
```python
# ✗ Bad - Has side effects
def detect_transitions(self):
    result = self._analyze()  # Modifies self.score_list
    self._save_to_file()

# ✓ Good - Returns value
def analyze(self, video_path: str) -> AnalysisResult:
    # Computes and returns, no side effects
    pass
```

---

## Comments and Documentation

### When to Comment

```python
# ✗ Bad - Obvious from code
count = count + 1  # Increment count

# ✓ Good - Explains why, not what
# Skip first frame to avoid comparing identical frames
frame_index = 1

# ✗ Bad - Too vague
# Check threshold
if change > THRESHOLD:

# ✓ Good - Clear reasoning
# Shot changes typically have high difference values.
# We use a threshold to filter noise from compression artifacts.
if change > THRESHOLD:
```

### Use Type Hints Instead of Comments

```python
# ✗ Old style
# Returns tuple of (success: bool, frame: ndarray)
def get_frame(self, idx):

# ✓ Modern style
def get_frame(self, idx: int) -> tuple[bool, np.ndarray]:
```

---

## File Organization

### module.py Structure

```python
1. Module docstring
2. Imports (stdlib, 3rd-party, local)
3. Constants
4. Dataclasses/enums
5. Main class
6. Helper functions/classes (if any)
7. __main__ block (if executable)
```

Example:
```python
"""Binary shot detector using frame difference analysis."""

import cv2
import numpy as np

from project.analyzers.base_analyzer import BaseAnalyzer, AnalysisResult
from project.core.video_handler import VideoHandler

# Constants
SHOT_CHANGE_THRESHOLD = 6
MIN_SHOT_GAP_SECONDS = 0.5

# Dataclasses (if needed)
# ...

# Main class
class BinaryShotDetector(BaseAnalyzer):
    # ...

# Helper functions
def _helper_function():
    pass

# Main block
if __name__ == "__main__":
    # Example usage or tests
    pass
```

---

## Deprecation Handling

When removing/changing APIs:

```python
import warnings

class VideoHandler:
    def old_method(self):
        """Deprecated: Use new_method() instead."""
        warnings.warn(
            "old_method is deprecated, use new_method()",
            DeprecationWarning,
            stacklevel=2
        )
        return self.new_method()
```

---

## Git Commit Messages

Follow this format:

```
<type>: <subject>

<optional detailed description>
```

Types: `feat`, `fix`, `refactor`, `docs`, `test`, `style`

Examples:
- `feat: Add face detection analyzer`
- `fix: Handle corrupted video files gracefully`
- `refactor: Separate UI from analysis logic`
- `docs: Update architecture guide`

---

## Performance Considerations

### OpenCV Operations
```python
# ✓ Good - Efficient
gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
binary = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY)[1]

# ✗ Bad - Multiple conversions
for _ in range(n):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
```

### Avoid Unnecessary Copies
```python
# ✗ Bad
def process(frame):
    frame_copy = frame.copy()
    frame_copy = cv2.cvtColor(frame_copy, ...)

# ✓ Good
def process(frame):
    processed = cv2.cvtColor(frame, ...)
```

---

**Last Updated**: 2026-03-09
