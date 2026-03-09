# Video Analyzer - Project Documentation

## Project Overview

**Video Analyzer** is a computer vision toolkit for analyzing video content. It provides a PyQt5-based GUI for progressively adding video analysis tools, starting with shot detection and frame extraction.

### Current Features
- Binary frame comparison for shot change detection (scene cuts, dissolves)
- Frame extraction to image sequences
- Temporal analysis and visualization
- Scene decomposition into video clips
- Plot generation for analysis results

### Vision
Extensible framework for adding new CV analysis tools:
- Face/object detection and tracking
- Motion detection and analysis
- Activity/action recognition
- Scene classification
- Color/lighting analysis
- Any future computer vision task

## Technology Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| GUI Framework | PyQt5 | 5.x |
| Video I/O | OpenCV (cv2) | 4.x |
| Scientific Computing | NumPy | Latest |
| Plotting | Matplotlib | Latest |
| Python | 3.8+ | - |

## Project Structure

```
exefile/
├── project/
│   ├── __init__.py
│   ├── main.py                          # Application entry point
│   │
│   ├── ui/
│   │   ├── __init__.py
│   │   └── video_player_gui.py          # PyQt5 GUI (no analysis logic)
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── video_handler.py             # Video I/O abstraction
│   │   └── file_manager.py              # Output folder and file handling
│   │
│   └── analyzers/
│       ├── __init__.py
│       ├── base_analyzer.py             # Abstract base class for all analyzers
│       ├── binary_shot_detector.py      # Shot change detection
│       └── frame_extractor.py           # Frame extraction tool
│
├── PROJECT.md                           # This file
├── ARCHITECTURE.md                      # Design decisions and patterns
├── CONVENTIONS.md                       # Code style and naming conventions
├── requirements.txt                     # Python dependencies
└── my_functions.py                      # Utility functions (to be reviewed)
```

## Key Design Goals

### 1. Separation of Concerns
- **UI** (PyQt5): Only handles display and user interaction
- **Analysis** (OpenCV): Pure computation, no UI dependencies
- **I/O** (File operations): Isolated module, composable
- **Coordination** (main.py): Orchestrates components

### 2. Plugin Architecture
New CV tools follow a simple pattern:
1. Inherit from `BaseAnalyzer`
2. Implement `analyze()` method
3. Register in main GUI
4. Button is automatically created

### 3. Testability
Each analyzer is independently testable without GUI or I/O side effects.

### 4. Incremental Development
Add new tools without modifying existing code. Framework handles all integration.

## Data Flow

```
User Input (GUI)
    ↓
VideoPlayerGUI.run_analysis(analyzer)
    ↓
Analyzer.analyze(video_path) → AnalysisResult
    ↓
FileManager.save_results(result)
    ↓
Update UI with results
```

## Analysis Result Format

All analyzers return a standardized `AnalysisResult`:

```python
@dataclass
class AnalysisResult:
    name: str                   # Tool name
    timestamps: list[float]     # Time points of interest (seconds)
    events: list[dict]          # Structured events with metadata
    score_list: list[float]     # Optional: continuous scores over time
    time_list: list[float]      # Optional: time points for scores
    metadata: dict              # Tool-specific data
```

Example for shot detection:
```python
AnalysisResult(
    name="Binary Shot Detector",
    timestamps=[2.5, 7.3, 12.1],
    events=[
        {"type": "shot_change", "time": 2.5, "reason": "cut"},
        {"type": "dissolve", "time": 7.3},
        {"type": "shot_change", "time": 12.1, "reason": "cut"},
    ],
    score_list=[...],
    time_list=[...],
    metadata={"total_shots": 3, "fps": 30}
)
```

## Output Structure

Analysis generates organized outputs:

```
project_root/
├── frames/              # Extracted frames (frame_0.jpg, frame_1.jpg, ...)
├── clips/               # Video clips split by shot (clip_1.mp4, clip_2.mp4, ...)
├── plots/               # Analysis visualizations (score_nointerpolation.png, ...)
└── times.txt            # Shot transition times (one per line)
```

## Dependencies

See `requirements.txt`. Key packages:
- `PyQt5` - GUI framework
- `opencv-python` - Computer vision
- `numpy` - Numerical computing
- `matplotlib` - Plotting

## Future Roadmap

### Phase 1 (Current)
- [x] Binary shot detection
- [x] Frame extraction
- [x] Basic visualization

### Phase 2
- [ ] Face detection and tracking
- [ ] Motion flow visualization
- [ ] Scene classification

### Phase 3
- [ ] Action/activity recognition
- [ ] Advanced filtering and post-processing
- [ ] Real-time preview support

### Phase 4
- [ ] Machine learning model integration
- [ ] Batch processing
- [ ] Export multiple formats

## Running the Application

```bash
pip install -r requirements.txt
python project/main.py
```

## Contributing New Analysis Tools

See `CONVENTIONS.md` and `ARCHITECTURE.md` for detailed patterns.

Quick start:
1. Create `project/analyzers/my_tool.py`
2. Inherit from `BaseAnalyzer`
3. Implement `analyze()` and `get_name()`
4. Import in `project/ui/video_player_gui.py`
5. Register in `VideoPlayerGUI.__init__()`

---

**Last Updated**: 2026-03-09
**Python Version**: 3.8+
