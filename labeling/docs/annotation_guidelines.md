# McDonald's Customer Review — Sentiment Annotation Guidelines

**Version:** 1.0  
**Dataset:** McDonald's Google Maps Customer Reviews (~22,000 reviews)  
**Annotation task:** Assign one of three sentiment labels to each customer review  
**Labels:** `Positive` | `Neutral` | `Negative`

---

## 1. Purpose

These guidelines enable three independent annotators to assign consistent, reproducible sentiment labels to McDonald's customer reviews. The labels will be used to train and evaluate supervised machine-learning models.

> [!IMPORTANT]
> Read this entire document before starting annotation. Do **not** look at other annotators' labels until you have completed your own column.

---

## 2. The Three Labels — Definitions

| Label | Operational Definition |
|-------|----------------------|
| **Positive** | The **overall impression** left by the reviewer is favourable. The reviewer would likely recommend this location or return willingly. |
| **Neutral** | The review expresses a **mixed, ambivalent, or purely factual** impression with no clear overall lean, OR the reviewer explicitly rates the experience as "just okay / average / neither good nor bad." |
| **Negative** | The **overall impression** is unfavourable. The reviewer is dissatisfied, upset, or explicitly warns others away. |

### Key principle
Label the **overall** sentiment of the review, not individual words or sentences.  
A review may contain positive words but still be Negative overall.

---

## 3. Decision Rules

Follow this flowchart for every review:

```
Step 1: Read the full review text.

Step 2: Identify the overall tone.
        • Clearly positive overall → Positive
        • Clearly negative overall → Negative
        • Mixed, ambivalent, or factual with no clear lean → Neutral

Step 3: Check for negation.
        "not bad" → leaning Positive (or Neutral if no other signal)
        "not good" → leaning Negative

Step 4: Check for sarcasm.
        If sarcasm is detected, flip the apparent sentiment.

Step 5: For borderline cases, ask:
        "Would this reviewer come back willingly and recommend the place?"
        Yes → Positive
        Probably not → Negative
        Can't tell / maybe → Neutral
```

---

## 4. Examples with Labels

### 4.1 Clear Positive

> *"The staff here is always friendly and ALWAYS get their orders correct. By far one of the best McDs I have ever been to."*  
> **Label: Positive** — unambiguously favourable overall impression.

> *"With all the new upgrades everything looks great and clean, great staff."*  
> **Label: Positive** — short but unambiguously positive.

> *"Best McDonald's ever. Fast, clean, friendly."*  
> **Label: Positive**

---

### 4.2 Clear Negative

> *"If I could give this location a zero on customer service, I would… don't even bother going to this location again."*  
> **Label: Negative**

> *"I repeat my order 3 times in the drive thru and she still managed to mess it up."*  
> **Label: Negative**

> *"Worst McDonald's."*  
> **Label: Negative** — very short, but the overall sentiment is unambiguous.

> *"I'm not happy at all… waste of money."*  
> **Label: Negative**

---

### 4.3 Clear Neutral

> *"Today I was disappointed that they didn't get me my full order. Luckily this was a hiccup and not a regular thing."*  
> **Label: Neutral** — mixed: a specific complaint balanced by acknowledgement it is unusual.

> *"It's McDonald's. It is what it is."*  
> **Label: Neutral** — explicitly neither positive nor negative.

> *"Went in, got my food, it was fine."*  
> **Label: Neutral** — factual, no strong lean either way.

---

### 4.4 Borderline / Tricky Cases

#### Mixed reviews — "good food but terrible service"

> *"The food was great as always but the service was absolutely terrible. Waited 30 minutes at the counter."*

**Rule:** Weigh which aspect dominates. Service failure combined with a 30-minute wait is a major complaint. Overall impression is likely **Negative**. If both aspects are roughly equal, use **Neutral**.

For this example → **Negative** (service failure is the dominant experience).

---

#### "Not bad"

> *"Not bad for a fast food place."*  
**Label: Neutral** — slightly positive but deliberately non-committal.

---

#### "Not good"

> *"The food was not good and it took forever."*  
**Label: Negative** — negation reverses the apparent positive word.

---

#### "Okay / average"

> *"Just okay. Nothing special."*  
**Label: Neutral**

> *"Average McDonald's experience."*  
**Label: Neutral**

---

#### "Never coming back"

> *"Never coming back to this location."*  
**Label: Negative** — explicit rejection, regardless of other content.

---

#### Sarcasm

> *"Microwaved nuggets, cold fries and a 30-minute wait. What more can you ask for? Don't go here ever!"*

The positive-sounding phrase ("what more can you ask for?") is clearly sarcastic — the reviewer explicitly says "don't go here ever." → **Negative**

---

#### Factual reviews with no opinion

> *"Located on US-183. Open 24 hours."*  
**Label: Neutral** — purely factual, no sentiment expressed.

---

#### Very short reviews

> *"Worst McDonald's."* → **Negative** (clear signal)  
> *"Amazing!"* → **Positive** (clear signal)  
> *"Meh."* → **Neutral**  
> *"Ok"* → **Neutral**  
> *"Fine."* → **Neutral**

**Rule:** If a short review has a recognisable positive or negative signal word, use it. If it is genuinely ambiguous (e.g., a single word with no clear polarity), use **Neutral**.

---

#### Auto-generated rating tags (marked `is_autotag = True`)

These reviews contain only Google's auto-generated word (e.g., *"Excellent"*, *"Good"*, *"Neutral"*, *"Poor"*, *"Terrible"*). They are **NOT free text**. Skip them — they will be handled separately and will not appear in your annotation file.

---

#### Rating conflicts with text

Sometimes a 1-star review contains mostly positive text (or vice versa). Always label based on **review text**, not the star rating.

> Review text: *"Food was hot and fresh, staff was kind!"* — Rating: 2 stars  
> **Label: Positive** (trust the text; the low rating may be an error).

> Review text: *"Disgusting place, rude staff, wrong order."* — Rating: 4 stars  
> **Label: Negative** (the text is unambiguous).

---

## 5. Special Rules Summary

| Phrase / Pattern | Label |
|-----------------|-------|
| "not good" | Negative |
| "not bad" | Neutral (or slightly Positive if no other negative signals) |
| "good food but terrible service" | Negative (if service failure dominates) OR Neutral |
| "okay" / "average" / "fine" | Neutral |
| "never coming back" | Negative |
| "best McDonald's ever" | Positive |
| Sarcasm where tone is negative overall | Negative |
| Factual only, no opinion | Neutral |
| Rating tag only (is_autotag=True) | **Skip** |
| Text contradicts star rating | Label by **text** |
| All three annotators disagree | Coordinator records the three original labels, then the team resolves the final class with a written rationale |

---

## 6. Handling Ambiguous Reviews

If you genuinely cannot decide after re-reading:

1. Apply the majority-lean rule: which class does the text *slightly* lean toward?
2. Still unsure? → Use **Neutral** as the tie-breaker.
3. Add a note in a separate column if your tool allows it (do NOT modify other annotators' columns).

---

## 7. Annotation Procedure

1. Open only your assigned blinded file in `../pilot/`: `annotator_1_sheet.csv`, `annotator_2_sheet.csv`, or `annotator_3_sheet.csv`.
2. Fill **only your assigned column** (`annotator_1`, `annotator_2`, or `annotator_3`). These files intentionally omit star ratings and rating-derived labels.
3. Valid values (copy-paste exactly):
   - `Positive`
   - `Neutral`
   - `Negative`
4. Do NOT add a fourth value such as `Disagreement`, or modify review IDs or text.
5. Do NOT look at other annotators' labels, ratings, or rating-derived labels before completing your own file.
6. Save the file when done and return it to the project lead, who merges its one label column into `../pilot/annotated_reviews.csv`.

---

## 8. What Happens Next

After all three annotators complete their columns:

- The project lead runs `compute_iaa.py` to calculate Fleiss' Kappa.
- Rows with full agreement → label accepted directly.
- Rows with 2/3 agreement → majority label accepted.
- Rows with 0/3 agreement (all three differ) → discussed as a team and resolved.
- The final resolved label is entered in the `final_sentiment` column.

---

*Document version 1.0 — Produced for McDonald's Review Sentiment Capstone Project*
