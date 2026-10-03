# Phase 9 User Guide

## Start the DSS

From the project root, run:

```powershell
powershell -ExecutionPolicy Bypass -File phase_9_decision_support_system\run_api.ps1
powershell -ExecutionPolicy Bypass -File phase_9_decision_support_system\run_dashboard.ps1
```

Open:

```text
http://127.0.0.1:8501
```

## Use the Dashboard

1. Enter a sample ID in the sidebar.
2. Adjust soil, microbiome, climate, orchard, and management inputs.
3. Select village, mango variety, soil depth, sampling season, and management.
4. Run prediction.
5. Review:
   - mango yield prediction
   - disease-risk class and confidence
   - nutrient status and confidence
   - feature contribution table
   - triggered recommendations
6. Download Markdown or JSON output if needed.

## Interpret Outputs

| Output | Meaning |
|---|---|
| Mango Yield | Predicted kg/tree from the regression champion |
| Disease Risk | Predicted `Low`, `Medium`, or `High` disease-risk class |
| Nutrient Status | Predicted `Optimal` or `High` nutrient-availability class |
| Feature Contributions | Phase 8 SHAP-supported feature importance context |
| Recommendations | Threshold rules triggered by the current input |

## Caveat

This DSS is a research prototype using synthetic data. Use the output as a modeling and thesis demonstration, not as a substitute for real soil testing or field diagnosis.

