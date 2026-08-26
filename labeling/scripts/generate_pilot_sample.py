"""Create a reproducible, rating-stratified and blinded annotation pilot."""
from pathlib import Path
import pandas as pd

BASE = Path(__file__).parent.parent
CLEANED_CSV = BASE.parent / "data" / "cleaned_reviews.csv"
PILOT_DIR = BASE / "pilot"
SAMPLE_CSV = PILOT_DIR / "annotation_sample_1000.csv"
MASTER_CSV = PILOT_DIR / "annotated_reviews.csv"
SEED = 42
SAMPLE_SIZE = 1000


def allocate_counts(counts: pd.Series, size: int) -> pd.Series:
    """Proportionally allocate an exact sample size using largest remainders."""
    ideal = counts / counts.sum() * size
    allocated = ideal.astype(int)
    remainder = (ideal - allocated).sort_values(ascending=False)
    for rating in remainder.index[: size - allocated.sum()]:
        allocated.loc[rating] += 1
    return allocated


def main() -> None:
    PILOT_DIR.mkdir(exist_ok=True)
    df = pd.read_csv(CLEANED_CSV, encoding="utf-8", low_memory=False)
    required = {"reviewer_id", "review_clean", "rating_num", "is_autotag"}
    missing = required.difference(df.columns)
    if missing:
        raise ValueError(f"Cleaned dataset is missing required columns: {sorted(missing)}")
    pool = df.loc[~df["is_autotag"].astype(bool)].copy()
    if len(pool) < SAMPLE_SIZE:
        raise ValueError(f"Only {len(pool)} eligible free-text reviews; need {SAMPLE_SIZE}.")

    allocation = allocate_counts(pool["rating_num"].value_counts().sort_index(), SAMPLE_SIZE)
    parts = []
    for offset, (rating, n) in enumerate(allocation.items()):
        group = pool.loc[pool["rating_num"] == rating]
        parts.append(group.sample(n=n, random_state=SEED + offset))
    sample = pd.concat(parts, ignore_index=True).sample(frac=1, random_state=SEED).reset_index(drop=True)
    reference = sample[["reviewer_id", "review_clean", "rating_num"]].rename(columns={
        "reviewer_id": "review_id", "review_clean": "review", "rating_num": "rating"
    })
    reference["rating_derived_label"] = reference["rating"].map(
        lambda r: "Negative" if r <= 2 else "Neutral" if r == 3 else "Positive"
    )
    reference.to_csv(SAMPLE_CSV, index=False, encoding="utf-8")

    master = reference.copy()
    for col in ("annotator_1", "annotator_2", "annotator_3", "final_sentiment"):
        master[col] = ""
    master.to_csv(MASTER_CSV, index=False, encoding="utf-8")
    for number in range(1, 4):
        sheet = reference[["review_id", "review"]].copy()
        sheet[f"annotator_{number}"] = ""
        sheet.to_csv(PILOT_DIR / f"annotator_{number}_sheet.csv", index=False, encoding="utf-8")

    print(f"Created {len(reference)}-review pilot with seed {SEED}.")
    print("Rating allocation:", allocation.to_dict())
    print("Distribute only the three annotator sheets; they deliberately omit ratings.")


if __name__ == "__main__":
    main()
