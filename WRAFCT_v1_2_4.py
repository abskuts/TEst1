"""
WRAFCT v1.2.4 - Warm-up Removal And File Combining Tool
Processes time-series CSV files: removes warm-up rows, combines files,
and exports file-summary, outlier, and negative-value reports.
"""

import os
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import pandas as pd


# ---------------------------------------------------------------------------
# Configuration constants
# ---------------------------------------------------------------------------
WARM_UP_ROWS = 10          # Number of leading rows to discard as warm-up
OUTLIER_ZSCORE = 3.0       # Z-score threshold for outlier detection
APP_TITLE = "WRAFCT v1.2.4"


# ---------------------------------------------------------------------------
# Core processing functions
# ---------------------------------------------------------------------------

def remove_warmup(df: pd.DataFrame, n_rows: int = WARM_UP_ROWS) -> pd.DataFrame:
    """Return *df* with the first *n_rows* warm-up rows removed."""
    return df.iloc[n_rows:].reset_index(drop=True)


def combine_csv_files(file_paths: list[str]) -> pd.DataFrame:
    """
    Load and concatenate multiple time-series CSV files.
    Adds a *source_file* column recording each row's origin.
    """
    frames = []
    for path in file_paths:
        try:
            df = pd.read_csv(path)
            df = remove_warmup(df)
            df.insert(0, "source_file", os.path.basename(path))
            frames.append(df)
        except Exception as exc:
            raise RuntimeError(f"Error reading '{path}': {exc}") from exc
    if not frames:
        raise ValueError("No valid CSV data was loaded.")
    return pd.concat(frames, ignore_index=True)


def build_file_summary(combined: pd.DataFrame) -> pd.DataFrame:
    """
    Return a per-file summary (row count and numeric column statistics)
    derived from the combined data frame.
    """
    numeric_cols = combined.select_dtypes(include="number").columns.tolist()
    rows = []
    for fname, group in combined.groupby("source_file"):
        entry = {"source_file": fname, "row_count": len(group)}
        for col in numeric_cols:
            entry[f"{col}_mean"] = group[col].mean()
            entry[f"{col}_min"] = group[col].min()
            entry[f"{col}_max"] = group[col].max()
        rows.append(entry)
    return pd.DataFrame(rows)


def find_outliers(combined: pd.DataFrame, threshold: float = OUTLIER_ZSCORE) -> pd.DataFrame:
    """
    Return rows that contain at least one numeric value whose
    absolute z-score exceeds *threshold*.
    """
    numeric_cols = combined.select_dtypes(include="number").columns.tolist()
    if not numeric_cols:
        return pd.DataFrame(columns=combined.columns)
    means = combined[numeric_cols].mean()
    stds = combined[numeric_cols].std(ddof=0).replace(0, 1)
    zscores = ((combined[numeric_cols] - means) / stds).abs()
    mask = (zscores > threshold).any(axis=1)
    return combined[mask].copy()


def find_negatives(combined: pd.DataFrame) -> pd.DataFrame:
    """Return rows that contain at least one negative numeric value."""
    numeric_cols = combined.select_dtypes(include="number").columns.tolist()
    if not numeric_cols:
        return pd.DataFrame(columns=combined.columns)
    mask = (combined[numeric_cols] < 0).any(axis=1)
    return combined[mask].copy()


def run_processing(file_paths: list[str], output_dir: str) -> dict:
    """
    Full pipeline:
      1. Combine CSV files (with warm-up removal)
      2. Export combined data
      3. Export file summary
      4. Export outlier report
      5. Export negative-value report
    Returns a dict of result paths and row counts.
    """
    combined = combine_csv_files(file_paths)

    combined_path = os.path.join(output_dir, "combined_data.csv")
    combined.to_csv(combined_path, index=False)

    summary = build_file_summary(combined)
    summary_path = os.path.join(output_dir, "file_summary.csv")
    summary.to_csv(summary_path, index=False)

    outliers = find_outliers(combined)
    outliers_path = os.path.join(output_dir, "outliers.csv")
    outliers.to_csv(outliers_path, index=False)

    negatives = find_negatives(combined)
    negatives_path = os.path.join(output_dir, "negatives.csv")
    negatives.to_csv(negatives_path, index=False)

    return {
        "combined_rows": len(combined),
        "summary_rows": len(summary),
        "outlier_rows": len(outliers),
        "negative_rows": len(negatives),
        "combined_path": combined_path,
        "summary_path": summary_path,
        "outliers_path": outliers_path,
        "negatives_path": negatives_path,
    }


# ---------------------------------------------------------------------------
# GUI
# ---------------------------------------------------------------------------

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.resizable(False, False)
        self.selected_files: list[str] = []
        self._build_ui()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_ui(self):
        pad = {"padx": 10, "pady": 6}

        # Title label
        tk.Label(
            self,
            text=APP_TITLE,
            font=("Helvetica", 14, "bold"),
        ).grid(row=0, column=0, columnspan=3, pady=(14, 4))

        # Buttons row
        tk.Button(self, text="Instructions", width=14, command=self._show_instructions).grid(
            row=1, column=0, **pad
        )
        tk.Button(self, text="Select Files", width=14, command=self._select_files).grid(
            row=1, column=1, **pad
        )
        tk.Button(self, text="Run", width=14, command=self._run, bg="#4CAF50", fg="white").grid(
            row=1, column=2, **pad
        )

        # File list
        tk.Label(self, text="Selected CSV files:").grid(
            row=2, column=0, columnspan=3, sticky="w", padx=10
        )
        self.file_listbox = tk.Listbox(self, width=80, height=8, selectmode=tk.EXTENDED)
        self.file_listbox.grid(row=3, column=0, columnspan=3, padx=10, pady=(0, 4))

        sb = tk.Scrollbar(self, orient=tk.VERTICAL, command=self.file_listbox.yview)
        sb.grid(row=3, column=3, sticky="ns", pady=(0, 4))
        self.file_listbox.configure(yscrollcommand=sb.set)

        # Remove selected / Clear all
        tk.Button(
            self, text="Remove Selected", width=14, command=self._remove_selected
        ).grid(row=4, column=0, **pad)
        tk.Button(
            self, text="Clear All", width=14, command=self._clear_all
        ).grid(row=4, column=1, **pad)

        # Output directory
        tk.Label(self, text="Output folder:").grid(
            row=5, column=0, sticky="e", padx=(10, 4)
        )
        self.output_var = tk.StringVar()
        tk.Entry(self, textvariable=self.output_var, width=48).grid(
            row=5, column=1, columnspan=2, sticky="w", pady=6
        )
        tk.Button(self, text="Browse…", command=self._browse_output).grid(
            row=5, column=3, padx=(4, 10)
        )

        # Log area
        tk.Label(self, text="Log:").grid(row=6, column=0, sticky="w", padx=10)
        self.log_box = scrolledtext.ScrolledText(
            self, width=80, height=10, state="disabled", wrap="word"
        )
        self.log_box.grid(row=7, column=0, columnspan=4, padx=10, pady=(0, 10))

    # ------------------------------------------------------------------
    # Event handlers
    # ------------------------------------------------------------------

    def _show_instructions(self):
        msg = (
            "WRAFCT - Warm-up Removal And File Combining Tool\n"
            "=================================================\n\n"
            "Instructions:\n\n"
            "i.  Use the Select Files button to choose the CSV files you want to process.\n\n"
            "ii. You can run this application from any folder and select the required "
            "CSV files using the Select Files button.\n\n"
            "iii. Choose an output folder using the Browse button (defaults to the "
            "folder of the first selected file).\n\n"
            "iv. Click Run to process the files.\n\n"
            "Output files produced:\n"
            "  • combined_data.csv  – all input rows combined (warm-up removed)\n"
            "  • file_summary.csv   – per-file row counts and column statistics\n"
            "  • outliers.csv       – rows with numeric z-score > 3\n"
            "  • negatives.csv      – rows containing negative numeric values\n\n"
            f"Note: The first {WARM_UP_ROWS} rows of each file are treated as "
            "warm-up data and are excluded from the outputs."
        )
        messagebox.showinfo("Instructions", msg)

    def _select_files(self):
        paths = filedialog.askopenfilenames(
            title="Select CSV files",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
        )
        for p in paths:
            if p not in self.selected_files:
                self.selected_files.append(p)
                self.file_listbox.insert(tk.END, p)
        if paths and not self.output_var.get():
            self.output_var.set(os.path.dirname(paths[0]))

    def _remove_selected(self):
        indices = list(self.file_listbox.curselection())
        for i in reversed(indices):
            self.file_listbox.delete(i)
            del self.selected_files[i]

    def _clear_all(self):
        self.file_listbox.delete(0, tk.END)
        self.selected_files.clear()

    def _browse_output(self):
        folder = filedialog.askdirectory(title="Select output folder")
        if folder:
            self.output_var.set(folder)

    def _run(self):
        if not self.selected_files:
            messagebox.showwarning("No files", "Please select at least one CSV file first.")
            return

        output_dir = self.output_var.get().strip()
        if not output_dir:
            messagebox.showwarning("No output folder", "Please choose an output folder.")
            return

        os.makedirs(output_dir, exist_ok=True)
        self._log(f"Starting processing of {len(self.selected_files)} file(s)…")
        self.update_idletasks()

        try:
            results = run_processing(self.selected_files, output_dir)
        except Exception as exc:
            self._log(f"ERROR: {exc}")
            messagebox.showerror("Processing error", str(exc))
            return

        self._log(f"Combined rows      : {results['combined_rows']}")
        self._log(f"Files summarised   : {results['summary_rows']}")
        self._log(f"Outlier rows       : {results['outlier_rows']}")
        self._log(f"Negative rows      : {results['negative_rows']}")
        self._log(f"Outputs saved to   : {output_dir}")
        self._log("Done.")
        messagebox.showinfo(
            "Complete",
            f"Processing complete.\n\nOutputs saved to:\n{output_dir}",
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _log(self, message: str):
        self.log_box.configure(state="normal")
        self.log_box.insert(tk.END, message + "\n")
        self.log_box.see(tk.END)
        self.log_box.configure(state="disabled")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    app = App()
    app.mainloop()
