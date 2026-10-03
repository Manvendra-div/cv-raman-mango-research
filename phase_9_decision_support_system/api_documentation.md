# Phase 9 API Documentation

## Start API

```powershell
powershell -ExecutionPolicy Bypass -File phase_9_decision_support_system\run_api.ps1
```

Default base URL:

```text
http://127.0.0.1:8000
```

Interactive OpenAPI page:

```text
http://127.0.0.1:8000/docs
```

## Endpoints

### `GET /health`

Returns API status.

Example response:

```json
{
  "status": "ok",
  "phase": "9"
}
```

### `GET /metadata`

Returns required numeric features, categorical features, feature ranges, categorical options, default input, model champions, and artifact paths.

### `GET /example-input`

Returns a complete sample payload accepted by `/predict`.

### `POST /predict`

Returns predictions, explanation features, recommendations, and reference artifacts.

Payload:

- all selected Phase 6 numeric features
- all selected categorical features
- optional `Sample_ID`
- optional contextual `Fusarium`

Example file:

- `phase_9_decision_support_system/examples/example_input.json`

### `POST /explain`

Returns explanation payload only.

### `POST /recommendations`

Returns triggered recommendation rules only.

### `POST /report`

Returns:

- Markdown report
- full prediction payload

## Example Command

```powershell
$payload = Get-Content phase_9_decision_support_system\examples\example_input.json -Raw
Invoke-RestMethod -Uri http://127.0.0.1:8000/predict -Method Post -Body $payload -ContentType "application/json"
```

## Notes

- The API uses local saved model artifacts.
- No internet connection is required.
- Outputs are prototype decision-support results based on synthetic training data.

