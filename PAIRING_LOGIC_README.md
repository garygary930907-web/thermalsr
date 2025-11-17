# Second-Level Grouping Pairing Logic

## Overview

This document explains the new second-level grouping pairing logic implemented in `01_prepare_V6.ipynb` (Cell 12).

## Problem Statement

The previous `direct_timestamp_pairing` function had limitations when handling:
- Variable thermal frame rates per second
- Missing seconds in thermal data
- Excess frames in certain seconds
- Precise RGB-thermal synchronization at the second level

## Solution: Second-Level Grouping

The new `second_level_grouping_pairing()` function implements a second-based grouping strategy:

### Step-by-Step Process

#### 1. Filter Thermal Data
- Filter thermal frames to only include those within RGB video time range
- Skip frames that are too early or too late

#### 2. Group by Second
- Group thermal frames by their integer second value
- This creates buckets like: second 0, second 1, second 2, etc.
- Track statistics: how many frames per second

#### 3. Collect Excess Frames
- For any second with more than 8 frames (target), collect the excess
- Example: Second 10 has 12 frames → keep first 8, collect last 4 for redistribution
- Store these excess frames in a redistribution pool

#### 4. Detect Missing Seconds
- Calculate the full time range (min_second to max_second)
- Identify seconds that have no thermal frames
- These are candidates for receiving redistributed frames

#### 5. Redistribute Frames
- For each missing second, allocate frames from the redistribution pool
- Assign up to 8 frames per missing second
- Frames are assigned in order from the pool

#### 6. Generate Pairs
- For each second with thermal frames:
  - For each frame position (0-7) in that second:
    - Calculate RGB frame index: `second * fps + position * (fps / 8)`
    - Create pair with thermal frame and RGB frame index
    - Calculate pairing error for quality metrics

#### 7. Statistics and Analysis
- Calculate pairing quality metrics:
  - RGB pairing error (ms)
  - RGB frame interval distribution
  - Per-second pairing count
- Generate detailed statistics for validation

## Key Features

### 1. RGB Pre-Extraction Logic
- RGB is conceptually cut every 0.125 seconds (8 frames per second)
- Formula: `rgb_frame_idx = second * fps + position_in_second * (fps / 8)`
- Ensures consistent timing within each second

### 2. Excess Frame Handling
- Automatically caps each second at maximum 8 thermal frames
- Excess frames aren't discarded—they're collected for redistribution
- Prevents data loss while maintaining temporal consistency

### 3. Missing Second Detection
- Identifies gaps in the thermal timeline
- Attempts to fill gaps using redistributed frames
- Reports which seconds were filled and how many frames each received

### 4. Flexible Pairing
- Handles seconds with fewer than 8 thermal frames naturally
- No need for special cases—just pairs what's available
- Example: Second with 5 thermal frames → creates 5 pairs (positions 0-4)

### 5. Comprehensive Visualization
The `visualize_second_level_pairing()` function creates 4 analysis panels:
1. **Per-second pairing count**: Bar chart showing how many pairs per second
2. **RGB error distribution**: Histogram of pairing time errors
3. **RGB interval distribution**: Histogram of frame-to-frame intervals
4. **Position distribution**: Scatter plot showing frame positions within seconds

## Configuration

### Constants (Cell 4)
```python
TARGET_FPS = 8  # Target thermal FPS
NORMAL_FRAMES_PER_SEC = TARGET_FPS  # Expected frames per second
FRAME_INTERVAL_MS = 1000 / TARGET_FPS  # 125ms between frames
```

### Parameters
```python
second_level_grouping_pairing(
    thermal_data,          # List of thermal frames with timestamps
    camera_start_time,     # RGB video start time
    fps,                   # RGB video frame rate
    frame_count,          # Total RGB frames
    target_thermal_fps=8  # Target thermal FPS (default 8)
)
```

## Example Scenarios

### Scenario 1: Normal Operation
- Second 0: 8 thermal frames → 8 pairs
- Second 1: 8 thermal frames → 8 pairs
- Second 2: 8 thermal frames → 8 pairs
- **Result**: Perfect pairing, 8 frames per second

### Scenario 2: Excess Frames
- Second 0: 8 thermal frames → 8 pairs
- Second 1: 12 thermal frames → 8 pairs (4 frames collected for redistribution)
- Second 2: 8 thermal frames → 8 pairs
- **Result**: Excess frames available for filling gaps

### Scenario 3: Missing Second
- Second 0: 8 thermal frames → 8 pairs
- Second 1: 0 thermal frames (missing)
- Second 2: 12 thermal frames → 8 pairs (4 collected)
- **Result**: Second 1 receives 4 redistributed frames from second 2

### Scenario 4: Fewer Frames
- Second 0: 8 thermal frames → 8 pairs
- Second 1: 5 thermal frames → 5 pairs (positions 0-4)
- Second 2: 8 thermal frames → 8 pairs
- **Result**: Second 1 has only 5 pairs, which is acceptable

## Quality Metrics

### RGB Pairing Error
- Measures time difference between expected and actual RGB frame
- Typical values: 5-15ms (good), >20ms (needs investigation)
- Calculated as: `|actual_rgb_time - expected_thermal_time|`

### RGB Frame Interval
- Measures consistency of RGB frame spacing
- Expected: ~3 frames (for 24.67 FPS RGB, 8 FPS thermal)
- Variations of ±1 frame are normal due to rounding

### Per-Second Count
- Shows how many pairs each second has
- Ideal: 8 pairs per second
- Acceptable: 4-8 pairs (depending on thermal data availability)

## Advantages Over Previous Method

1. **Better handling of variable frame rates**: Groups by second before pairing
2. **No frame loss**: Excess frames redistributed instead of discarded
3. **Gap filling**: Missing seconds automatically filled when possible
4. **Clear temporal structure**: Each second has up to 8 well-defined positions
5. **Better diagnostics**: Detailed statistics and visualization
6. **Predictable behavior**: Consistent 125ms intervals within each second

## Troubleshooting

### Issue: Missing seconds not filled
- **Cause**: No excess frames available for redistribution
- **Solution**: Check if any seconds have >8 frames; if not, missing seconds will stay empty

### Issue: High RGB pairing error
- **Cause**: Mismatch between thermal timestamps and RGB frame rate
- **Solution**: Verify `camera_start_time` is correct; check if thermal FPS varies

### Issue: Uneven frame intervals
- **Cause**: Missing seconds create gaps in the sequence
- **Solution**: Normal if data has natural gaps; verify with visualization

## Testing

A test script is available at `/tmp/test_pairing_logic.py` (during development) that:
- Creates mock thermal data with various scenarios
- Tests the pairing function
- Verifies correct behavior for edge cases
- Confirms no second exceeds 8 frames
- Validates missing second redistribution

## Future Enhancements

Possible improvements for future versions:
1. Adaptive redistribution priority (fill earlier seconds first)
2. Interpolation for missing seconds when no redistribution available
3. Quality-based frame selection (prefer better quality frames)
4. Support for variable target FPS
5. Real-time pairing mode for live processing
