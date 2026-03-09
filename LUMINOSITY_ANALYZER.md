# Luminosity Analyzer Feature

## Overview

Added a new **Luminosity Analysis** tool to the Video Analyzer. This analyzer measures the brightness (luminosity) of every frame in the video and generates a plot showing how brightness changes over time.

## What It Does

### Analysis
1. **Frame-by-frame brightness measurement** - Converts each frame to grayscale and calculates mean pixel intensity (0-255)
2. **Fade detection** - Automatically detects fade-in and fade-out transitions
3. **Statistics** - Computes min, max, and average luminosity across the entire video
4. **Visualization** - Generates a professional plot showing brightness over time

### Output
- **Plot file**: `plots/luminosity_over_time.png`
- **Metadata**:
  - Minimum/maximum/average brightness
  - Number of fade transitions detected
  - Video duration and frame count

## Files Created

### `project/analyzers/luminosity_analyzer.py`
Main analyzer implementing the `BaseAnalyzer` interface with:
- `LuminosityAnalyzer` class
- `_calculate_luminosity()` - Computes brightness for a single frame
- `_create_plot()` - Generates matplotlib visualization

### Modified Files

**`project/ui/video_player_gui.py`**
- Added import: `from project.analyzers.luminosity_analyzer import LuminosityAnalyzer`
- Registered analyzer in `_register_builtin_analyzers()`
- Enhanced `run_analysis()` to display plot file path

## How to Use

### In GUI
1. Load a video file
2. Click **"Luminosity Analysis"** button
3. Wait for analysis to complete
4. View results message showing:
   - Number of brightness transitions detected
   - Path to saved plot file

### Programmatically
```python
from project.analyzers.luminosity_analyzer import LuminosityAnalyzer

analyzer = LuminosityAnalyzer()
result = analyzer.analyze("video.mp4")

# Access results
print(f"Average brightness: {result.metadata['avg_luminosity']:.1f}")
print(f"Fade transitions: {result.metadata['brightness_changes']}")
print(f"Plot saved to: {result.metadata['plot_file']}")

# Plot data available for further processing
import matplotlib.pyplot as plt
plt.plot(result.time_list, result.score_list)
plt.show()
```

## Luminosity Calculation

### Algorithm
1. Convert BGR frame to grayscale using `cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)`
2. Calculate mean pixel intensity using `np.mean(gray_frame)`
3. Result is a value from 0 (pure black) to 255 (pure white)

### Example Values
- Dark scene: ~30-80
- Normal indoor: ~100-150
- Bright outdoor: ~180-220
- Overexposed: ~240+

## Fade Detection

### How It Works
1. Computes range = max_luminosity - min_luminosity
2. Threshold = 30% of range
3. Frames with >threshold brightness change are marked as fade events
4. Fade-in: brightness increasing
5. Fade-out: brightness decreasing

### Example Output
```json
{
  "type": "fade_out",
  "time": 45.2,
  "frame": 1353,
  "brightness_before": 180.5,
  "brightness_after": 92.3,
  "change": 88.2
}
```

## Plot Features

The generated plot (`luminosity_over_time.png`) shows:
- **Blue line**: Brightness over time
- **Green dashed line**: Average brightness
- **X-axis**: Time in seconds
- **Y-axis**: Brightness (0-255 scale)
- **Grid**: For easy reading

Example appearance:
```
255 |
    |     /‾‾\                /‾‾‾\
200 |    /    \              /     \
    |   /      \            /       \
150 |  /        \          /         \
    | /          ‾‾‾‾‾‾‾‾/           ‾‾‾‾
100 |
    |
 50 |________________________
    +------------------------+
    0                      duration
```

## Use Cases

### Content Analysis
- Detect lighting problems (underexposed, overexposed)
- Find fade transitions automatically
- Identify scene types (indoor vs outdoor)

### Quality Control
- Check for exposure consistency
- Detect sudden brightness changes
- Find lighting glitches

### Video Segmentation
- Combine with shot detection for better scene boundaries
- Fade-outs often indicate scene ending
- Lighting changes correlate with location changes

### Creative Analysis
- Identify color grading consistency
- Detect night vs day scenes
- Find lighting equipment changes

## Technical Details

### Performance
- Processes full video in reasonable time (depends on resolution)
- Memory efficient: processes frame-by-frame
- O(n) complexity where n = number of frames

### Dependencies
- `opencv-python` - Frame reading and grayscale conversion
- `numpy` - Statistical calculations
- `matplotlib` - Plot generation

### Accuracy Notes
- Works well for general brightness measurement
- Fade detection threshold (30% of range) is tunable if needed
- Doesn't account for content distribution (histogram-based might be more robust)
- For perceptually uniform brightness, LAB color space would be more accurate

## Advanced Usage

### Custom Threshold
```python
# More sensitive to small changes
analyzer = LuminosityAnalyzer()  # Use default threshold

# Current implementation uses 30% of range
# To make stricter, you could subclass:
class StrictLuminosityAnalyzer(LuminosityAnalyzer):
    # Would need to modify _create_plot or add parameter
    pass
```

### Batch Processing
```python
from pathlib import Path
from project.analyzers.luminosity_analyzer import LuminosityAnalyzer
import json

analyzer = LuminosityAnalyzer()

for video in Path("videos").glob("*.mp4"):
    result = analyzer.analyze(str(video))

    summary = {
        "file": video.name,
        "avg_brightness": result.metadata['avg_luminosity'],
        "fades": result.metadata['brightness_changes'],
        "plot": result.metadata['plot_file']
    }

    with open(f"analysis_{video.stem}.json", "w") as f:
        json.dump(summary, f, indent=2)
```

## Output Example

### GUI Message
```
Luminosity Analysis: 12 events detected. Transitions at: [5.32s, 12.45s, 18.90s, 25.67s, 31.23s]
📊 Plot saved: /path/to/plots/luminosity_over_time.png
```

### Metadata
```python
{
    'fps': 30.0,
    'total_frames': 3600,
    'duration_seconds': 120.0,
    'min_luminosity': 25.5,
    'max_luminosity': 245.3,
    'avg_luminosity': 128.7,
    'brightness_changes': 12,
    'plot_file': '/path/to/plots/luminosity_over_time.png'
}
```

## Troubleshooting

### Plot doesn't appear
- Check `plots/` folder exists
- Verify disk space available
- Check matplotlib backend compatibility

### Inaccurate brightness readings
- Check video codec (some codecs alter colors)
- Different color spaces may give different results
- HDR videos may not be properly converted

### All frames same brightness
- Video might be corrupted
- Check if cv2 can read frames properly
- Video might have text overlay affecting measurements

## Future Enhancements

Potential improvements:
1. **Histogram-based luminosity** - More sophisticated than mean
2. **LAB color space** - Perceptually uniform brightness
3. **Regional analysis** - Different zones of frame
4. **Configurable threshold** - UI slider for fade detection sensitivity
5. **Contrast analysis** - Standard deviation of pixel values
6. **Color channel analysis** - Separate R, G, B channel analysis
7. **Temporal smoothing** - Moving average to smooth noise

---

**Status**: ✅ Complete and integrated
**Version**: 0.1.0
**Date Added**: 2026-03-09
