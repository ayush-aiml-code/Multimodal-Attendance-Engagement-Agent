# Activity 6.3 — Validation Report

## Tests Performed

| Test | Result | Observation |
|---|---|---|
| Webcam attendance | PASS | Attendance record generated successfully. |
| Recorded video attendance | PASS | Multiple face IDs were processed. |
| Short appearance | PASS | A 4.38-second appearance was marked Absent against the 10-second threshold. |
| Low-light detection | PASS (visual check) | Face box and ID remained visible during the test. |
| Partial face occlusion | NEEDS IMPROVEMENT | Face box disappeared and reappeared; face IDs changed repeatedly. |
| Audio silence detection | PASS | The 5-second silent segment had RMS 0.0 and was classified as silence or very low sound. |

## Audio Test Details

- Test audio duration: 15 seconds.
- Expected segments: 3.
- Detected silence segments: 1.
- Active sound segments: 2 expected test segments.
- Note: An additional old segment appeared in the analysis output, indicating that stale files in the output folder may affect results.

## Limitations

- Face tracking may become unstable during partial face occlusion.
- Low-light validation was a visual check, not a comprehensive robustness test.
- Active sound detection indicates sound energy and does not independently confirm speech or engagement.

## Conclusion

Core attendance and silence-detection tests passed. Partial-face tracking needs further improvement, and the audio test should be repeated after cleaning stale output files. Further validation is recommended before claiming full real-world robustness.
