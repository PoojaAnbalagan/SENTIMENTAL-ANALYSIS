# Labeling workflow

## Folder structure

| Folder | Contents |
|---|---|
| `docs/` | Annotation guidelines and capstone methodology. |
| `pilot/` | The 1,000-review sample, completed annotator sheets, and annotation master file. |
| `reports/` | Agreement, disagreement, and pseudo-labeling evaluation outputs. |
| `scripts/` | Re-runnable workflow scripts. |
| `decisions/` | Documented labeling decisions. |
| `archive/` | Superseded rating-proxy dataset; do not use for preprocessing. |

## Preprocessing-ready dataset

Use `../data/final_pseudo_labeled_dataset.csv`. Its target column is `sentiment`.
It contains 1,000 human labels and 21,448 model pseudo-labels. Keep rows where
`split_role = gold_test` out of model fitting and retain `label_source` and
`needs_human_review` for reporting and quality control.

## Commands

Run these from the project root.

```powershell
# Regenerate the hybrid pseudo-labeled preprocessing dataset
python labeling\scripts\create_pseudo_labeled_dataset.py

# Recalculate pilot agreement after editing the pilot master
python labeling\scripts\compute_iaa.py

# Regenerate the original pilot sample (overwrites pilot CSVs)
python labeling\scripts\generate_pilot_sample.py
```

Do not run `build_final_dataset.py` for the hybrid workflow; it produces the
archived rating-proxy baseline instead.
