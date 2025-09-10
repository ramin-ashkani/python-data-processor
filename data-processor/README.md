# 📊 Data Processor

A **lightweight Python tool** for **data cleaning, transformation, and reporting**. It automates processing of CSV and
Excel files and generates clean datasets, summaries, and visual insights.

---

## ✨ Key Features

- ✅ **Multi-format support** — CSV and Excel files
- ✅ **Automated cleaning** — trims and standardizes column names, fills missing values
- ✅ **Smart handling of nulls** — drop columns exceeding missing value threshold
- ✅ **Duplicate detection** — remove redundant rows by all columns or specific subset
- ✅ **Reporting** — outputs JSON summary, HTML report, and histogram charts
- ✅ **Organized output** — all results saved in a dedicated `output/` folder

---

## 📂 Project Structure

```
data-processor-upwork/
├─ processor.py           # Main Python script
├─ requirements.txt       # Dependencies
├─ README.md              # Documentation
├─ sample_data/
│  └─ sample_data_full.csv # Demo dataset
├─ LICENSE
└─ .gitignore
```

---

## 🚀 Quick Start

### 1. Setup Environment

```bash
python -m venv venv
source venv/bin/activate    # macOS / Linux
venv\Scripts\activate     # Windows
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run Example

```bash
python processor.py sample_data/sample_data_full.csv -o output
```

---

## 📑 Output Files

- `cleaned.csv` → cleaned and deduplicated dataset
- `summary.json` → metadata summary of dataset
- `report.html` → human-readable report
- `hist_*.png` → histogram plots for numeric columns
- `meta.json` → detailed processing metadata

---

## ⚙️ CLI Options

| Option             | Description                                              | Default     |
|--------------------|----------------------------------------------------------|-------------|
| `input`            | Input CSV or Excel file                                  | required    |
| `-o, --output`     | Output directory                                         | `output`    |
| `--drop-threshold` | Threshold for dropping columns with missing values (0–1) | `0.6`       |
| `--fill-method`    | Fill method for missing values: `ffill` or `zero`        | `ffill`     |
| `--dedup-cols`     | Columns to consider for removing duplicates              | all columns |

---

## 💡 Why Use This Tool?

- Efficient **data cleaning and preprocessing** for small to medium datasets
- Generates **structured outputs** for reporting or further analysis
- Provides **visual insights** with histograms of numeric columns
- Fully **configurable via CLI**

---

## 🔮 Extensions & Improvements

- Integrate **web interface** (Flask/Django) for file upload and instant reporting
- Add **advanced profiling** with `ydata-profiling`
- Implement **unit tests and CI/CD** pipelines
- Deploy as a **cloud service** for online use

---

## 📜 License

This project is released under the **MIT License**. You are free to use, copy, modify, merge, publish, distribute,
sublicense, and/or sell copies of the software. See the full license text in the [LICENSE](LICENSE) file.