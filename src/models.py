"""
models.py
=========
Model definitions, training wrappers, and inference engines for:
1. Logistic Regression (balanced)
2. Linear SVM (LinearSVC, balanced)
3. Multinomial Naive Bayes
4. SGDClassifier (Logistic loss / balanced)
5. RidgeClassifier (balanced)
6. VADER Rule-Based Baseline
7. Fine-Tuned DistilBERT (Transformer)
"""

import os
import inspect
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from sklearn.linear_model import LogisticRegression, SGDClassifier, RidgeClassifier
from sklearn.svm import LinearSVC
from sklearn.naive_bayes import MultinomialNB
from sklearn.utils.class_weight import compute_class_weight
from sklearn.calibration import CalibratedClassifierCV
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

try:
    from transformers import (
        AutoTokenizer,
        AutoModelForSequenceClassification,
        Trainer,
        TrainingArguments
    )
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

CLASSES = ["Negative", "Neutral", "Positive"]
LABEL_MAP = {"Negative": 0, "Neutral": 1, "Positive": 2}
REV_LABEL_MAP = {0: "Negative", 1: "Neutral", 2: "Positive"}
SEED = 42

def get_classical_models(seed: int = SEED) -> dict:
    """
    Returns the benchmark dictionary of classical supervised machine learning classifiers.
    """
    models = {
        "Logistic Regression": LogisticRegression(
            max_iter=2000,
            class_weight="balanced",
            C=1.0,
            random_state=seed
        ),
        "Linear SVM": LinearSVC(
            class_weight="balanced",
            C=1.0,
            random_state=seed,
            dual="auto" if "dual" in inspect.signature(LinearSVC.__init__).parameters else True
        ),
        "Multinomial Naive Bayes": MultinomialNB(
            alpha=1.0
        ),
        "SGDClassifier": SGDClassifier(
            loss="log_loss",
            penalty="l2",
            alpha=1e-4,
            class_weight="balanced",
            random_state=seed,
            max_iter=2000
        ),
        "RidgeClassifier": RidgeClassifier(
            alpha=1.0,
            class_weight="balanced",
            random_state=seed
        )
    }
    return models


class VaderSentimentBaseline:
    """
    VADER Rule-Based Lexicon Baseline Wrapper.
    """
    def __init__(self, pos_thresh: float = 0.05, neg_thresh: float = -0.05):
        self.analyzer = SentimentIntensityAnalyzer()
        self.pos_thresh = pos_thresh
        self.neg_thresh = neg_thresh
        self.classes_ = np.array(CLASSES)

    def predict(self, texts: pd.Series | list[str]) -> np.ndarray:
        preds = []
        for text in texts:
            score = self.analyzer.polarity_scores(str(text))["compound"]
            if score >= self.pos_thresh:
                preds.append("Positive")
            elif score <= self.neg_thresh:
                preds.append("Negative")
            else:
                preds.append("Neutral")
        return np.array(preds)

    def predict_proba(self, texts: pd.Series | list[str]) -> np.ndarray:
        probas = []
        for text in texts:
            scores = self.analyzer.polarity_scores(str(text))
            pos = scores.get("pos", 0.0)
            neu = scores.get("neu", 0.0)
            neg = scores.get("neg", 0.0)
            total = pos + neu + neg
            if total == 0:
                probas.append([1/3, 1/3, 1/3])
            else:
                probas.append([neg / total, neu / total, pos / total])
        return np.array(probas)


class PyTorchSentimentDataset(torch.utils.data.Dataset):
    def __init__(self, encodings, labels=None):
        self.encodings = encodings
        self.labels = labels

    def __getitem__(self, idx):
        item = {key: torch.tensor(val[idx]) for key, val in self.encodings.items()}
        if self.labels is not None:
            item["labels"] = torch.tensor(self.labels[idx], dtype=torch.long)
        return item

    def __len__(self):
        return len(self.encodings["input_ids"])


class CustomWeightedTrainer(Trainer):
    def __init__(self, *args, class_weights=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.class_weights = class_weights

    def compute_loss(self, model, inputs, return_outputs=False, **kwargs):
        labels = inputs.get("labels")
        outputs = model(**inputs)
        logits = outputs.get("logits")
        if self.class_weights is not None:
            loss_fct = nn.CrossEntropyLoss(weight=self.class_weights.to(logits.device))
        else:
            loss_fct = nn.CrossEntropyLoss()
        loss = loss_fct(logits.view(-1, self.model.config.num_labels), labels.view(-1))
        return (loss, outputs) if return_outputs else loss


class DistilBERTPipeline:
    """
    Fine-tuned DistilBERT Sequence Classification Pipeline.
    """
    def __init__(
        self,
        model_path: str = "distilbert-base-uncased",
        device: str = None
    ):
        if not TRANSFORMERS_AVAILABLE:
            raise ImportError("HuggingFace transformers is required for DistilBERT.")
        self.model_path = model_path
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.model = AutoModelForSequenceClassification.from_pretrained(
            model_path,
            num_labels=3,
            id2label=REV_LABEL_MAP,
            label2id=LABEL_MAP
        ).to(self.device)
        self.classes_ = np.array(CLASSES)

    def predict_proba(self, texts: list[str], batch_size: int = 64) -> np.ndarray:
        self.model.eval()
        all_probas = []
        with torch.no_grad():
            for i in range(0, len(texts), batch_size):
                batch_texts = texts[i:i + batch_size]
                encodings = self.tokenizer(
                    batch_texts,
                    padding=True,
                    truncation=True,
                    max_length=128,
                    return_tensors="pt"
                ).to(self.device)
                outputs = self.model(**encodings)
                logits = outputs.logits
                probas = torch.softmax(logits, dim=-1).cpu().numpy()
                all_probas.append(probas)
        return np.vstack(all_probas)

    def predict(self, texts: list[str], batch_size: int = 64) -> np.ndarray:
        probas = self.predict_proba(texts, batch_size=batch_size)
        pred_ids = np.argmax(probas, axis=-1)
        return np.array([REV_LABEL_MAP[i] for i in pred_ids])
