# Quick Start Guide

## Prerequisites

Python 3.8+ with the required packages:

```bash
pip install -r requirements.txt
```

## Running the Application

### Option 1: From Project Directory
```bash
cd project
python main.py
```

### Option 2: From Root Directory
```bash
python -m project.main
```

### Option 3: Direct Import (For Testing)
```python
from project.ui.video_player_gui import VideoPlayerGUI
from PyQt5.QtWidgets import QApplication
import sys

app = QApplication(sys.argv)
window = VideoPlayerGUI()
window.show()
sys.exit(app.exec_())
```

## Usage

1. **Click "Select Video"** - Choose a video file (MP4, AVI, MOV, MKV)
2. **Click "Play"** - Preview video in external window
3. **Run Analysis:**
   - **Binary Shot Detector** - Find scene transitions
   - **Extract Frames** - Save all frames as JPEGs
4. **Check Output:**
   - `frames/` - Extracted frame images
   - `times.txt` - Shot transition times
   - `plots/` - Analysis visualizations

## Analyzing Individual Components

### Test Binary Shot Detector
```python
from project.analyzers.binary_shot_detector import BinaryShotDetector

tool = BinaryShotDetector(threshold=6, min_gap_seconds=0.5)
result = tool.analyze("your_video.mp4")

print(f"Detected {len(result.events)} transitions")
for event in result.events:
    print(f"  {event['type']} at {event['time']:.2f}s")
```

### Run Frame Extractor Standalone
```python
from project.analyzers.frame_extractor import FrameExtractor

extractor = FrameExtractor()
result = extractor.analyze("your_video.mp4")
print(f"Saved {result.metadata['frames_saved']} frames")
```

### List Extracted Frames
```python
from project.core.file_manager import FileManager

fm = FileManager()
frames = fm.get_frames_list()
print(f"Found {len(frames)} frames:")
for frame_path in frames[:5]:
    print(f"  {frame_path}")
```

## Common Tasks

### Change Shot Detection Sensitivity
```python
# Stricter detection (fewer false positives)
tool = BinaryShotDetector(threshold=10, min_gap_seconds=1.0)

# Looser detection (catch more transitions)
tool = BinaryShotDetector(threshold=3, min_gap_seconds=0.2)
```

### Save Analysis Results as JSON
```python
import json
from project.analyzers.binary_shot_detector import BinaryShotDetector

detector = BinaryShotDetector()
result = detector.analyze("video.mp4")

results_dict = {
    "name": result.name,
    "transitions": result.timestamps,
    "events": result.events,
    "metadata": result.metadata
}

with open("analysis_results.json", "w") as f:
    json.dump(results_dict, f, indent=2)
```

### Batch Process Multiple Videos
```python
from pathlib import Path
from project.analyzers.binary_shot_detector import BinaryShotDetector
import json

detector = BinaryShotDetector()
video_dir = Path("videos")

for video_file in video_dir.glob("*.mp4"):
    result = detector.analyze(str(video_file))

    with open(f"{video_file.stem}_analysis.json", "w") as f:
        json.dump({
            "file": video_file.name,
            "transitions": result.timestamps,
            "shot_count": result.metadata["shot_changes"]
        }, f)

    print(f"✓ Analyzed {video_file.name}")
```

## Troubleshooting

### ModuleNotFoundError: No module named 'project'
Make sure you're running from the correct directory:
```bash
# From exefile directory
python -m project.main

# Or from project subdirectory
cd project
python main.py
```

### Video Won't Load
- Check file format (MP4, AVI, MOV, MKV supported)
- Verify OpenCV has codec support
- Try with a different video file

### Analyzer Fails
- Check console for error messages
- Ensure video file is not corrupted
- Verify sufficient disk space for output

### GUI Doesn't Appear
- Install PyQt5: `pip install PyQt5`
- Ensure X11 forwarding if using SSH
- Check python version: `python --version` (should be 3.8+)

## Next Steps

1. **Test each analyzer** with sample videos
2. **Create custom analyzer** following template in CONVENTIONS.md
3. **Add new features** using the plugin framework
4. **Batch process** videos programmatically

See `PROJECT.md` and `ARCHITECTURE.md` for detailed documentation.
