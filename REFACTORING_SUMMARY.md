# Refactoring Complete: New Project Structure

## Summary

The Video Analyzer project has been successfully restructured into a clean, modular architecture. This document summarizes what was changed and how to use the new structure.

## What Was Created

### Directory Structure
```
project/
├── __init__.py
├── main.py                          # New: Application entry point
├── ui/
│   ├── __init__.py
│   └── video_player_gui.py          # Refactored: Clean GUI-only code
├── core/
│   ├── __init__.py
│   ├── video_handler.py             # New: Video I/O abstraction
│   └── file_manager.py              # New: Output file management
└── analyzers/
    ├── __init__.py
    ├── base_analyzer.py             # New: Abstract base class framework
    ├── binary_shot_detector.py       # Refactored: Pure analysis logic
    └── frame_extractor.py            # Refactored: Pure analysis logic
```

### New Modules Explained

#### 1. **base_analyzer.py** - The Plugin Framework
- `BaseAnalyzer`: Abstract base class for all analysis tools
- `AnalysisResult`: Standardized data class for all analyzer outputs

**Why it matters:**
- Ensures all analyzers have consistent interface
- Makes GUI registration automatic
- Enables testing without GUI

#### 2. **video_handler.py** - Video I/O Abstraction
Replaces scattered `cv2.VideoCapture()` calls with:
```python
with VideoHandler(video_path) as handler:
    for frame_num, frame in handler.iter_frames():
        # Process frame
```

**Benefits:**
- Cleaner resource management (automatic release)
- Consistent error handling
- Easy to mock for tests

#### 3. **file_manager.py** - Output Management
Replaces scattered `os.makedirs()` and file operations with:
```python
fm = FileManager()
fm.save_frame(frame, "frame_001.jpg")
fm.save_times([1.5, 3.2, 5.8])
```

**Benefits:**
- Centralized folder management
- Organized output structure
- Easy to change output location

#### 4. **binary_shot_detector.py** - Refactored Analysis
Before:
```python
def binary_analysis(self):  # Mixed UI + analysis
    # 100+ lines of messy code
    # Direct cv2 calls
    # Manual file I/O
    # self.messagebox.setText() everywhere
```

After:
```python
class BinaryShotDetector(BaseAnalyzer):
    def analyze(self, video_path: str) -> AnalysisResult:
        # Clean, testable analysis code
        # Returns structured result
        # No UI calls, no I/O side effects
```

#### 5. **frame_extractor.py** - New Standalone Tool
Extracted from original `extract_frames()` method as independent analyzer.

#### 6. **video_player_gui.py** - Refactored GUI
Before:
```python
# 630+ lines mixing UI, analysis, file I/O
self.binaryButton = QPushButton("Analyze binary images", self)
self.binaryButton.clicked.connect(self.binary_analysis)
```

After:
```python
# ~230 lines, clean separation of concerns
def __init__(self):
    self.register_analyzer(BinaryShotDetector())
    self.register_analyzer(FrameExtractor())
    # Buttons created automatically
```

---

## How to Run

### Using New Structure
```bash
cd project
python main.py
```

### Key Changes for Users
1. Same GUI functionality
2. Same buttons and controls
3. Better error handling
4. More organized output
5. Faster to add new tools

---

## How to Add New Analyzer Tools

### Step 1: Create Analyzer File
Create `project/analyzers/my_cool_tool.py`:

```python
"""My new CV analysis tool."""

from project.analyzers.base_analyzer import BaseAnalyzer, AnalysisResult
from project.core.video_handler import VideoHandler

class MyCoolTool(BaseAnalyzer):
    def get_name(self) -> str:
        return "My Cool Tool"

    def analyze(self, video_path: str) -> AnalysisResult:
        with VideoHandler(video_path) as handler:
            events = []
            # Your CV logic here

            return AnalysisResult(
                name=self.get_name(),
                timestamps=[],
                events=events,
                metadata={"fps": handler.fps}
            )
```

### Step 2: Register in GUI
Edit `project/ui/video_player_gui.py`:

```python
def _register_builtin_analyzers(self) -> None:
    self.register_analyzer(BinaryShotDetector())
    self.register_analyzer(FrameExtractor())
    self.register_analyzer(MyCoolTool())  # Add this line
```

That's it! Button appears automatically.

---

## Migration Notes

### What Changed in Imports
| Old | New |
|-----|-----|
| `from Video_player_v2 import VideoPlayer` | `from project.ui.video_player_gui import VideoPlayerGUI` |
| N/A | `from project.analyzers.base_analyzer import BaseAnalyzer` |
| N/A | `from project.core.video_handler import VideoHandler` |
| N/A | `from project.core.file_manager import FileManager` |

### Old Code (Video_player_v2.py)
- Still exists for reference
- No longer used
- Can be archived or deleted
- All functionality migrated to new structure

### Output Folders
Remains same:
- `frames/` - Extracted frames
- `clips/` - Split video clips
- `plots/` - Analysis visualizations
- `times.txt` - Shot detection times

---

## Testing Individual Components

### Test Analyzer in Isolation
```python
from project.analyzers.binary_shot_detector import BinaryShotDetector

detector = BinaryShotDetector()
result = detector.analyze("test_video.mp4")

print(f"Found {len(result.events)} transitions")
print(f"Shots: {result.metadata['shot_changes']}")
```

### Test FileManager
```python
from project.core.file_manager import FileManager

fm = FileManager("./test_output")
fm.save_times([1.5, 3.2, 5.8])
loaded = fm.load_times()
assert loaded == [1.5, 3.2, 5.8]
```

### Test VideoHandler
```python
from project.core.video_handler import VideoHandler

with VideoHandler("video.mp4") as handler:
    print(f"FPS: {handler.fps}")
    print(f"Total frames: {handler.total_frames}")

    for frame_num, frame in handler.iter_frames():
        if frame_num > 10:
            break  # First 10 frames only
```

---

## Architecture Compliance Check

✓ **Separation of Concerns:**
- UI layer: `ui/video_player_gui.py`
- Analysis layer: `analyzers/*`
- I/O layer: `core/`

✓ **Testability:**
- All analyzers can run without GUI
- Pure functions without side effects
- Easy to mock and test

✓ **Extensibility:**
- New tools = 1 new file + 1 registration line
- No modifications to existing code
- Framework handles all integration

✓ **Reproducibility:**
- Metadata captured in results
- Parameters recorded
- Same result every run

---

## Next Steps (Optional Enhancements)

### Short Term
- [ ] Add unit tests for each analyzer
- [ ] Create CLI interface (same analyzers, no GUI)
- [ ] Add batch processing for multiple videos

### Medium Term
- [ ] Add configuration/parameter UI sliders
- [ ] Implement results export (JSON, CSV)
- [ ] Add progress bars for long operations

### Long Term
- [ ] Integrate ML models (faster object detection)
- [ ] Add real-time preview of analysis
- [ ] Multi-GPU support

---

## File Sizes (Comparison)

| Component | Old | New | Change |
|-----------|-----|-----|--------|
| GUI + Analysis | 630 lines | 230 lines (GUI) + 150 (Analyzer) | Cleaner split |
| Video I/O | Scattered | ~150 lines | Centralized |
| File Management | Scattered | ~200 lines | Centralized |
| Framework | N/A | ~100 lines | New |

**Total:** Same code, much better organized!

---

**Created:** 2026-03-09
**Next Phase:** Start adding new CV analysis tools easily!
