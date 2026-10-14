# Academic Reports & Capstone Documentation

This directory contains the final academic deliverables, technical audit reports, and methodology documentation for the **McDonald's Customer Review Sentiment Analysis & Intelligence Platform**.

---

## 📁 Document Catalog

| Document | Format | Description |
| :--- | :--- | :--- |
| **`22CDS0412.docx`** | Microsoft Word Document | Capstone Final Academic Thesis & Project Report (*Candidate ID: 22CDS0412*). |
| **`McDonalds_Review_Sentiment_Analysis_Capstone_Final_Audit_Report.pdf`** | PDF Document | Technical evaluation audit summarizing model benchmarks, error analysis, robustness testing, and class balancing formulations. |
| **`McDonalds_Sentiment_Analysis_Data_Pipeline_Methodology_Report.pdf`** | PDF Document | Exhaustive 7-page technical methodology report covering the 10-stage data cleaning pipeline, 3-annotator pilot agreement (Fleiss' κ = 0.6287), sublinear TF-IDF mathematics, and viva defense Q&A. |
| **`generate_pipeline_pdf.py`** | Python Script | Self-contained, zero-dependency PDF generator that programmatically builds the methodology report. |

---

## 🚀 Re-Generating Methodology PDF

To re-compile the technical PDF report directly:

```powershell
python reports/generate_pipeline_pdf.py
```
This generates the publication-ready `McDonalds_Sentiment_Analysis_Data_Pipeline_Methodology_Report.pdf` in the `reports/` folder.
