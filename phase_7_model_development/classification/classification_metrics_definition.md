# Classification Metrics Definition

## Model-Level Metrics

| Metric | Meaning |
|---|---|
| Accuracy | Fraction of samples classified correctly |
| Balanced accuracy | Mean recall across classes |
| Precision macro | Mean per-class precision with equal class weighting |
| Recall macro | Mean per-class recall with equal class weighting |
| Macro F1-score | Mean per-class F1-score with equal class weighting |
| ROC-AUC | One-vs-rest area under the ROC curve, averaged across classes where suitable |
| Multiclass Brier | Mean squared difference between predicted probabilities and one-hot actual labels |

Model-level metrics are saved in:

- `outputs/metrics/classification/classification_model_metrics.csv`

## Class-Level Metrics

Class-level precision, recall, F1-score, and support are saved in:

- `outputs/metrics/classification/classification_class_metrics.csv`

## Confusion Matrix

Confusion-matrix rows include:

- target
- model
- split
- actual class
- predicted class
- count
- actual-class total
- row percent

Saved in:

- `outputs/metrics/classification/classification_confusion_matrix.csv`

## Calibration Curve

Calibration is computed as one-vs-rest probability bins for each target, model, split, and class.

Saved columns include:

- mean predicted probability
- observed class rate
- bin count

Saved in:

- `outputs/metrics/classification/classification_calibration_curve.csv`

## Champion Selection Metric

The champion model is selected independently for each target by:

```text
maximum validation macro F1-score
```

Current champions:

- `Disease_Risk`: `Gradient_Boosting`
- `Nutrient_Availability`: `Random_Forest`

## Important Caveat

The current dataset is synthetic prototype data. Metrics validate the modeling workflow and reproducibility artifacts, but they should not be interpreted as final field performance.

