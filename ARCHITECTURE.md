# Architecture and Design Decisions

## Core Architecture Pattern

### Three-Layer Architecture

```
┌─────────────────────────────────────────────┐
│         UI Layer (PyQt5)                    │
│  - VideoPlayerGUI class                     │
│  - User interaction and display             │
│  - Delegation to analyzers/file manager     │
└─────────────────────────────────────────────┘
              ↓           ↓
┌──────────────────────┐  ┌──────────────────────┐
│  Analysis Layer      │  │  I/O Layer           │
│  - BaseAnalyzer      │  │  - VideoHandler      │
│  - Concrete analyzers│  │  - FileManager       │
│  - Pure CV logic     │  │  - File operations   │
└──────────────────────┘  └──────────────────────┘
```

### Dependency Direction

```
UI depends on → Analyzers + I/O
Analyzers DO NOT depend on → UI or I/O
I/O depends on → Nothing (independent)
```

This ensures:
- Analyzers can be tested without UI
- UI can be swapped (CLI, web, etc.)
- Components are reusable independently

---

## Layer Responsibilities

### 1. UI Layer (`ui/video_player_gui.py`)

**Responsibilities:**
- PyQt5 window management
- Button creation and layout
- Display video playback
- Show results and messages
- Handle user input (file selection, play/pause)
- Delegate analysis to analyzers

**What it should NOT do:**
- Video I/O (use `VideoHandler`)
- File system operations (use `FileManager`)
- Video analysis logic (use `BaseAnalyzer` subclasses)

**Current violators:**
- Direct `cv2.VideoCapture()` calls → migrate to `VideoHandler`
- `os.makedirs()` and `os.path.join()` → migrate to `FileManager`
- Analysis logic mixed with UI updates → move to analyzers

---

### 2. Analysis Layer (`analyzers/`)

**Responsibilities:**
- Pure computer vision algorithms
- Input: video path, parameters
- Output: `AnalysisResult` object
- No side effects (no file I/O, no UI calls)

**Interface (BaseAnalyzer):**

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass

@dataclass
class AnalysisResult:
    """Standardized output from any analyzer"""
    name: str
    timestamps: list[float]
    events: list[dict]
    score_list: list[float] = None
    time_list: list[float] = None
    metadata: dict = None

class BaseAnalyzer(ABC):
    @abstractmethod
    def analyze(self, video_path: str) -> AnalysisResult:
        """
        Run analysis on video.

        Args:
            video_path: Path to video file

        Returns:
            AnalysisResult with findings
        """
        pass

    @abstractmethod
    def get_name(self) -> str:
        """Return display name for GUI button"""
        pass

    @property
    def description(self) -> str:
        """Optional: Return tool description for tooltips"""
        return ""
```

**Example Implementation:**

```python
class BinaryShotDetector(BaseAnalyzer):
    def get_name(self) -> str:
        return "Binary Shot Detector"

    @property
    def description(self) -> str:
        return "Detect scene cuts and dissolves using binary frame comparison"

    def analyze(self, video_path: str) -> AnalysisResult:
        # No UI updates, no file I/O beyond reading video
        # Only cv2 operations
        # Return AnalysisResult
        pass
```

**Benefits of this pattern:**
```python
# Can test analyzer in isolation
detector = BinaryShotDetector()
result = detector.analyze("test.mp4")
assert len(result.events) > 0

# Can batch process without GUI
for video in glob("*.mp4"):
    result = detector.analyze(video)
    print(result.metadata)
```

---

### 3. I/O Layer (`core/`)

#### VideoHandler (`core/video_handler.py`)

**Responsibilities:**
- Abstraction over `cv2.VideoCapture`
- Video metadata queries
- Frame reading
- FPS, total frames, dimensions, etc.

**Interface:**

```python
class VideoHandler:
    def __init__(self, video_path: str):
        self.path = video_path
        self.cap = cv2.VideoCapture(video_path)

    @property
    def fps(self) -> float:
        return self.cap.get(cv2.CAP_PROP_FPS)

    @property
    def total_frames(self) -> int:
        return int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))

    @property
    def width(self) -> int:
        return int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))

    @property
    def height(self) -> int:
        return int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    def get_frame(self, frame_number: int) -> tuple[bool, np.ndarray]:
        """Get specific frame. Returns (success, frame)"""
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
        return self.cap.read()

    def iter_frames(self) -> Generator[tuple[int, np.ndarray], None, None]:
        """Iterate through all frames"""
        frame_num = 0
        while True:
            ret, frame = self.cap.read()
            if not ret:
                break
            yield frame_num, frame
            frame_num += 1

    def release(self):
        self.cap.release()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.release()
```

**Usage in analyzers:**

```python
def analyze(self, video_path: str) -> AnalysisResult:
    with VideoHandler(video_path) as handler:
        fps = handler.fps
        for frame_num, frame in handler.iter_frames():
            # Your CV logic here
            pass
```

#### FileManager (`core/file_manager.py`)

**Responsibilities:**
- Create output folders (frames, clips, plots)
- Manage times.txt file
- Save extracted frames
- Handle all file I/O

**Interface:**

```python
class FileManager:
    def __init__(self, base_dir: str = "."):
        self.base_dir = base_dir
        self.folders = {
            "frames": os.path.join(base_dir, "frames"),
            "clips": os.path.join(base_dir, "clips"),
            "plots": os.path.join(base_dir, "plots"),
        }

    def ensure_folder(self, folder_type: str):
        """Create folder if doesn't exist"""
        pass

    def save_frame(self, frame: np.ndarray, name: str) -> str:
        """Save frame image, return file path"""
        pass

    def save_times(self, times: list[float], overwrite: bool = False):
        """Save shot transition times to times.txt"""
        pass

    def load_times(self) -> list[float]:
        """Load times from times.txt"""
        pass

    def save_plot(self, fig, name: str) -> str:
        """Save matplotlib figure"""
        pass

    def get_folder_path(self, folder_type: str) -> str:
        """Get path to output folder"""
        pass
```

---

## UI Integration Pattern

### GUI Registration Model

```python
class VideoPlayerGUI(QMainWindow):
    def __init__(self):
        super().__init__()

        # Initialize core services
        self.file_manager = FileManager()

        # Initialize analyzers
        self.analyzers = []
        self.register_analyzer(BinaryShotDetector())
        self.register_analyzer(FrameExtractor())
        # Easy to add: self.register_analyzer(FaceDetector())

        self._create_ui()

    def register_analyzer(self, analyzer: BaseAnalyzer):
        """Dynamically add analyzer and create UI button"""
        self.analyzers.append(analyzer)

        # Create button
        btn = QPushButton(analyzer.get_name())
        if analyzer.description:
            btn.setToolTip(analyzer.description)
        btn.clicked.connect(lambda: self.run_analysis(analyzer))

        self.layout.addWidget(btn)

    def run_analysis(self, analyzer: BaseAnalyzer):
        """Execute analyzer and handle results"""
        try:
            result = analyzer.analyze(self.video_path)
            self.file_manager.save_times(result.timestamps)
            self._display_results(result)
        except Exception as e:
            self.messagebox.setText(f"Error: {str(e)}")
```

### Benefits of this pattern:
- Adding new tool = 1 line: `self.register_analyzer(NewTool())`
- No UI modification needed
- Tools are completely independent
- Can reorder, disable, or conditionally load tools

---

## Error Handling Strategy

### In Analyzers (Pure CV logic)
```python
def analyze(self, video_path: str) -> AnalysisResult:
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video not found: {video_path}")

    with VideoHandler(video_path) as handler:
        if handler.fps == 0:
            raise ValueError("Invalid video: fps = 0")
        # ... analysis
```

### In UI (Catch and display)
```python
def run_analysis(self, analyzer: BaseAnalyzer):
    try:
        result = analyzer.analyze(self.video_path)
        # Success handling
    except FileNotFoundError as e:
        self.messagebox.setText(f"File error: {e}")
    except ValueError as e:
        self.messagebox.setText(f"Invalid video: {e}")
    except Exception as e:
        logger.exception("Unexpected error")
        self.messagebox.setText("Analysis failed unexpectedly")
```

---

## Testing Strategy

### Unit Tests (Analyzers)
```python
def test_binary_shot_detector():
    detector = BinaryShotDetector()
    result = detector.analyze("test_video.mp4")

    assert isinstance(result, AnalysisResult)
    assert result.name == "Binary Shot Detector"
    assert len(result.events) > 0
    assert all("type" in e for e in result.events)
```

### Integration Tests (with FileManager)
```python
def test_analysis_workflow():
    analyzer = BinaryShotDetector()
    file_mgr = FileManager("test_output")

    result = analyzer.analyze("test.mp4")
    file_mgr.save_times(result.timestamps)

    loaded = file_mgr.load_times()
    assert loaded == result.timestamps
```

### No GUI Tests Needed
- Analyzers work without GUI
- FileManager works independently
- UI is thin, minimal logic to test

---

## Configuration & Parameters

Each analyzer can have configurable parameters:

```python
class BinaryShotDetector(BaseAnalyzer):
    def __init__(self,
                 threshold: int = 6,
                 min_gap_seconds: float = 0.5):
        self.threshold = threshold
        self.min_gap_seconds = min_gap_seconds

    def analyze(self, video_path: str) -> AnalysisResult:
        # Use self.threshold, self.min_gap_seconds
        pass
```

Future: Use configuration files or UI parameter widgets for runtime adjustment.

---

## Migration Checklist

When migrating existing code:

- [x] Document which layer each component belongs to
- [ ] Extract `VideoHandler` from `VideoPlayer`
- [ ] Extract `FileManager` from `VideoPlayer`
- [ ] Create `BaseAnalyzer` and `AnalysisResult`
- [ ] Refactor `binary_analysis()` to `BinaryShotDetector.analyze()`
- [ ] Refactor `extract_frames()` to `FrameExtractor.analyze()`
- [ ] Update `VideoPlayer` to use registration pattern
- [ ] Add unit tests for analyzers
- [ ] Remove dead code (commented face detection)

---

**Design Principles Applied:**
- Single Responsibility: Each class has one reason to change
- Dependency Inversion: Depend on abstractions (BaseAnalyzer), not implementations
- Open/Closed: New features don't modify existing code
- Interface Segregation: Analyzers have minimal interface
