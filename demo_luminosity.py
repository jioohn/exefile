#!/usr/bin/env python3
"""Demo script showing Luminosity Analyzer usage."""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from project.analyzers.luminosity_analyzer import LuminosityAnalyzer


def demo_luminosity_analysis():
    """Demonstrate luminosity analysis on a video file.

    This script shows how to use the LuminosityAnalyzer programmatically,
    without the GUI.
    """
    print("=" * 60)
    print("Luminosity Analyzer - Demo")
    print("=" * 60)

    # Look for video file
    video_files = list(Path(".").glob("*.mp4"))
    if not video_files:
        video_files = list(Path(".").glob("*.avi"))
    if not video_files:
        video_files = list(Path(".").glob("*.mov"))

    if not video_files:
        print("\nNo video file found in current directory.")
        print("Supported formats: MP4, AVI, MOV, MKV")
        print("\nUsage: place a video file in the project directory and run this script.")
        return

    video_path = str(video_files[0])
    print(f"\nAnalyzing: {video_path}")
    print("-" * 60)

    try:
        # Create analyzer
        analyzer = LuminosityAnalyzer()

        # Run analysis
        print("Running analysis...")
        result = analyzer.analyze(video_path)

        # Display results
        print(f"\n✓ Analysis Complete!")
        print(f"\nTool: {result.name}")
        print(f"Video Duration: {result.metadata['duration_seconds']:.1f} seconds")
        print(f"Total Frames: {result.metadata['total_frames']}")
        print(f"FPS: {result.metadata['fps']:.1f}")

        print(f"\nBrightness Statistics:")
        print(f"  Minimum:  {result.metadata['min_luminosity']:.1f} (0=black)")
        print(f"  Maximum:  {result.metadata['max_luminosity']:.1f} (255=white)")
        print(f"  Average:  {result.metadata['avg_luminosity']:.1f}")

        print(f"\nFade Transitions Detected: {result.metadata['brightness_changes']}")

        if result.events:
            print("\nTop 5 Brightness Changes:")
            for i, event in enumerate(result.events[:5], 1):
                print(f"  {i}. {event['type']:12} at {event['time']:7.2f}s "
                      f"(change: {event.get('change', 0):5.1f})")

        print(f"\nPlot saved to: {result.metadata['plot_file']}")
        print("\n" + "=" * 60)
        print("Analysis results available at:")
        print(f"  - Plot: plots/luminosity_over_time.png")
        print(f"  - Data: Can be accessed programmatically via result object")
        print("=" * 60)

    except Exception as e:
        print(f"\n✗ Analysis Failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    demo_luminosity_analysis()
