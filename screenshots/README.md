# Screenshots Documentation

This directory contains all screenshots documenting the MLOps pipeline implementation.

## Directory Structure

```
screenshots/
├── airflow/               # Apache Airflow DAG execution (68 screenshots)
├── storage_versioning/    # MinIO & DVC setup (27 screenshots)  
├── mlflow/                # MLflow experiment tracking
├── data_quality/          # Data quality validation reports
└── README.md              # This file
```

## Guidelines

### Naming Convention
- Use numbered prefixes: `01_`, `02_`, `03_`, etc.
- Use descriptive names: `minio_bucket_created.png`
- Keep names lowercase with underscores

### Quality Standards
- **Resolution**: Minimum 1920x1080 pixels
- **Format**: PNG (for clarity and annotations)
- **File Size**: Compress to keep under 2MB per image
- **Annotations**: Add red boxes/arrows to highlight key elements

### Tools for Capturing Screenshots

#### macOS
- **Full Screen**: `Cmd + Shift + 3`
- **Selected Area**: `Cmd + Shift + 4`
- **Screenshot Tool**: `Cmd + Shift + 5`
- **Annotation**: Use Preview.app or Skitch

#### Recommended Tools
- **Skitch**: For annotations and arrows
- **Monosnap**: Advanced screenshot tool
- **CleanShot X**: Professional screenshots with annotations

## Screenshot Categories

### 1. Airflow Pipeline (68 screenshots)
Location: `screenshots/airflow/`

Covers:
- Environment setup (8)
- Airflow configuration (12)
- DAG execution and monitoring (20)
- Quality gates and validation (8)
- Data profiling with MLflow (9)
- Storage and versioning (8)
- Git integration (3)

See: [`AIRFLOW_COMMANDS_SCREENSHOTS.md`](../AIRFLOW_COMMANDS_SCREENSHOTS.md)

### 2. Storage & Versioning (27 screenshots)
Location: `screenshots/storage_versioning/`

Covers:
- MinIO setup and configuration (5)
- DVC initialization (5)
- File upload and versioning (8)
- Integration testing (9)

### 3. MLflow Tracking
Location: `screenshots/mlflow/`

Covers:
- Experiment creation
- Run tracking
- Artifact logging
- Metrics visualization

### 4. Data Quality
Location: `screenshots/data_quality/`

Covers:
- Quality check reports
- Profiling reports
- Validation results
- Failure scenarios

## Best Practices

### Before Taking Screenshots

1. **Clean Your Environment**
   - Close unnecessary tabs/windows
   - Hide sensitive information
   - Use consistent theme (light/dark)

2. **Prepare the View**
   - Zoom to appropriate level
   - Ensure text is readable
   - Show relevant context

3. **Mask Sensitive Data**
   - API keys
   - Passwords
   - Personal tokens
   - Real database credentials

### After Taking Screenshots

1. **Review Quality**
   - Check readability
   - Verify key elements are visible
   - Ensure proper focus

2. **Add Annotations**
   - Highlight important sections with red boxes
   - Add arrows pointing to key features
   - Use text callouts sparingly

3. **Optimize Size**
   - Compress without losing quality
   - Use tools like ImageOptim (macOS)
   - Target < 2MB per image

## Screenshot Checklist

Use this checklist for each screenshot session:

- [ ] All services running (Airflow, MinIO, MLflow)
- [ ] Browser/terminal theme consistent
- [ ] Sensitive data masked
- [ ] High resolution (1920x1080+)
- [ ] Proper naming convention
- [ ] Annotations added where needed
- [ ] Screenshots organized in correct folder
- [ ] Cross-referenced in documentation

## Reference Documents

- **Main Guide**: [`AIRFLOW_COMMANDS_SCREENSHOTS.md`](../AIRFLOW_COMMANDS_SCREENSHOTS.md)
- **Setup Instructions**: [`SETUP_AND_RUN.md`](../SETUP_AND_RUN.md)
- **Commands Reference**: [`COMMANDS_REFERENCE.md`](../COMMANDS_REFERENCE.md)

## Contributing

When adding new screenshots:

1. Follow the naming convention
2. Add description to relevant markdown doc
3. Update screenshot count in this README
4. Compress images before committing
5. Verify images render correctly in GitHub

## Total Screenshots Required

| Category | Count | Status |
|----------|-------|--------|
| Airflow Pipeline | 68 | 📋 Planned |
| Storage & Versioning | 27 | 📋 Planned |
| MLflow Tracking | TBD | 📋 Planned |
| Data Quality | TBD | 📋 Planned |
| **Total** | **95+** | **In Progress** |

## Notes

- All screenshots support the MLOps Phase 1 implementation
- Screenshots demonstrate mandatory quality gates
- Each screenshot corresponds to specific command in documentation
- Keep this README updated as you add screenshots
