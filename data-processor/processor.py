import argparse
import sys
from pathlib import Path
import json
import tempfile

try:
    import pandas as pd
    import matplotlib.pyplot as plt
except Exception as e:
    print("Missing required Python packages. Install with: pip install -r requirements.txt")
    raise


def detect_file_type(path: Path):
    suffix = path.suffix.lower()
    if suffix in (".csv", ".txt"):
        return "csv"
    if suffix in (".xls", ".xlsx"):
        return "excel"
    raise ValueError(f"Unsupported file type: {suffix}")


def read_data(path: Path, **kwargs):
    ftype = detect_file_type(path)
    if ftype == "csv":
        return pd.read_csv(path, **kwargs)
    else:
        return pd.read_excel(path, **kwargs)


def infer_types(df: pd.DataFrame):
    return df.dtypes.apply(lambda x: str(x)).to_dict()


def basic_clean(df: pd.DataFrame, drop_threshold: float = 0.6, fill_method: str = "ffill"):
    # Strip column names and trim strings
    df = df.copy()
    df.rename(columns=lambda c: c.strip() if isinstance(c, str) else c, inplace=True)
    for col in df.select_dtypes(include=["object"]).columns:
        df[col] = df[col].astype(str).str.strip().replace({"nan": "", "None": ""})
    # Drop columns with too many missing values
    na_frac = df.isna().mean()
    drop_cols = na_frac[na_frac > drop_threshold].index.tolist()
    if drop_cols:
        df.drop(columns=drop_cols, inplace=True)
    # Fill remaining missing values
    if fill_method == "ffill":
        df.fillna(method="ffill", inplace=True)
        df.fillna(method="bfill", inplace=True)
    elif fill_method == "zero":
        df.fillna(0, inplace=True)
    else:
        df.fillna(method="ffill", inplace=True)
    return df, drop_cols


def deduplicate(df: pd.DataFrame, subset=None):
    before = len(df)
    df2 = df.drop_duplicates(subset=subset)
    after = len(df2)
    return df2, before - after


def generate_summary(df: pd.DataFrame, outdir: Path, sample_rows: int = 5):
    outdir.mkdir(parents=True, exist_ok=True)
    summary = {}
    summary["rows"] = len(df)
    summary["columns"] = len(df.columns)
    summary["column_types"] = infer_types(df)
    summary["missing_per_column"] = df.isna().sum().to_dict()
    summary["duplicates"] = int(df.duplicated().sum())
    summary["sample"] = df.head(sample_rows).to_dict(orient="records")
    # Save JSON summary
    (outdir / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False))
    # Create a simple HTML report
    html = ["<html><head><meta charset='utf-8'><title>Data Processor Report</title></head><body>"]
    html.append(f"<h1>Data Processor Report</h1>")
    html.append(f"<p><strong>Rows:</strong> {summary['rows']}, <strong>Columns:</strong> {summary['columns']}</p>")
    html.append("<h2>Column types</h2><ul>")
    for c, t in summary["column_types"].items():
        html.append(f"<li><strong>{c}</strong>: {t}</li>")
    html.append("</ul>")
    html.append("<h2>Missing values per column</h2><ul>")
    for c, v in summary["missing_per_column"].items():
        html.append(f"<li>{c}: {v}</li>")
    html.append("</ul>")
    html.append("<h2>Sample rows</h2>")
    html.append("<pre>" + json.dumps(summary["sample"], indent=2, ensure_ascii=False) + "</pre>")
    html.append("</body></html>")
    (outdir / "report.html").write_text("\n".join(html), encoding="utf-8")
    return summary


def save_plots(df: pd.DataFrame, outdir: Path, max_plots=3):
    outdir.mkdir(parents=True, exist_ok=True)
    numeric = df.select_dtypes(include=["number"])
    plots = []
    for i, col in enumerate(numeric.columns[:max_plots]):
        plt.figure()
        numeric[col].hist()
        plt.title(f"Histogram: {col}")
        p = outdir / f"hist_{i + 1}_{col}.png"
        plt.savefig(p)
        plt.close()
        plots.append(str(p.name))
    return plots


def main(argv=None):
    p = argparse.ArgumentParser(prog="processor.py", description="Data Processor - clean + analyze CSV/Excel files")
    p.add_argument("input", help="Path to CSV or Excel file to process")
    p.add_argument("-o", "--output", default="output", help="Output directory (created if missing)")
    p.add_argument("--encoding", default=None, help="Encoding for CSV (auto if omitted)")
    p.add_argument("--drop-threshold", type=float, default=0.6,
                   help="Drop columns with > threshold missing fraction (0-1)")
    p.add_argument("--fill-method", choices=["ffill", "zero"], default="ffill", help="Method to fill missing values")
    p.add_argument("--dedup-cols", nargs="*", default=None,
                   help="Columns to consider for deduplication (default: all columns)")
    args = p.parse_args(argv)

    inp = Path(args.input)
    outdir = Path(args.output)
    outdir.mkdir(parents=True, exist_ok=True)

    if not inp.exists():
        print(f"Input file not found: {inp}")
        sys.exit(2)

    # read
    read_kwargs = {}
    if args.encoding:
        read_kwargs["encoding"] = args.encoding
    try:
        df = read_data(inp, **read_kwargs)
    except Exception as e:
        print("Error reading input file:", e)
        sys.exit(3)

    # basic clean
    cleaned, dropped = basic_clean(df, drop_threshold=args.drop_threshold, fill_method=args.fill_method)

    # deduplicate
    deduped, removed = deduplicate(cleaned, subset=args.dedup_cols)

    # save cleaned CSV
    cleaned_path = outdir / "cleaned.csv"
    deduped.to_csv(cleaned_path, index=False)

    # summary
    summary = generate_summary(deduped, outdir)

    # plots
    plots = save_plots(deduped, outdir)

    # final metadata
    meta = {
        "input": str(inp),
        "output_dir": str(outdir),
        "dropped_columns": dropped,
        "duplicates_removed": removed,
        "plots": plots,
        "summary": summary
    }
    (outdir / "meta.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False))
    print("Processing complete. Output saved to:", outdir)


if __name__ == "__main__":
    main()
