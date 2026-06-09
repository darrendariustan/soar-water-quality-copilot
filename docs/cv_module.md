# CV Module — Computer Vision for Water Test Analysis

Member 2 contribution. Reads water test strip images and water sample images, returning structured JSON for downstream agents.

## Setup

Requires Python 3.11+ and [uv](https://github.com/astral-sh/uv).

```bash
cd backend
uv sync --extra dev
```

If uv is not installed:
```bash
pip install uv
```

## Running tests

```bash
uv run pytest tests/cv/ -v
```

## Usage

### Analyse a test strip

```python
from backend.src.cv.engine import load_image, analyse_test_strip

img = load_image("path/to/test_strip.jpg")
result = analyse_test_strip(img)
print(result.model_dump_json(indent=2))
```

To use a custom reference chart:
```python
result = analyse_test_strip(img, chart_path="path/to/my_chart.json")
```

### Classify a water sample image

```python
from backend.src.cv.classifier import classify_water_sample
from backend.src.cv.engine import load_image

img = load_image("path/to/water_sample.jpg")
result = classify_water_sample(img)
print(result.model_dump_json(indent=2))
```

## Output formats

### Test strip result

```json
{
  "image_type": "test_strip",
  "parameters": [
    {
      "name": "pH",
      "estimated_value": "7.0",
      "unit": "",
      "matched_colour": {
        "rgb": [255, 180, 80],
        "hsv": [30, 175, 255]
      },
      "confidence": 0.82
    }
  ],
  "overall_confidence": 0.78,
  "image_quality": {
    "brightness": "acceptable",
    "blur": "low",
    "lighting_warning": false
  },
  "warnings": [
    "This is an estimated reading from image analysis and does not replace laboratory testing."
  ]
}
```

### Water sample result

```json
{
  "image_type": "water_sample",
  "appearance": {
    "clarity": "cloudy",
    "colour": "slightly_brown",
    "visible_particles": true
  },
  "overall_confidence": 0.74,
  "warnings": [
    "Visual appearance alone cannot confirm whether water is safe to drink."
  ]
}
```

## Reference chart format

Charts are stored in `backend/src/cv/reference_charts/`. Each chart is a JSON file:

```json
{
  "strip_name": "My Strip",
  "parameters": [
    {
      "name": "pH",
      "unit": "",
      "entries": [
        {"value": "7.0", "rgb": [255, 180, 80], "hsv": [30, 175, 255]}
      ]
    }
  ]
}
```

Pass the path to `analyse_test_strip(img, chart_path=...)` to switch charts.

## Safety note

This module outputs estimated readings only. The final water safety decision is handled by the Water Quality Agent and Treatment Guidance Agent. Never surface raw CV output as a safety verdict to the user.
