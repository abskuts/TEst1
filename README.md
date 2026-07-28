# WRAFCT – Warm-up Removal And File Combining Tool

A desktop application for processing time-series CSV files.  
It removes warm-up rows, combines multiple files, and exports four reports:

| Output file | Description |
|---|---|
| `combined_data.csv` | All input rows combined after warm-up removal |
| `file_summary.csv` | Per-file row counts and numeric column statistics |
| `outliers.csv` | Rows containing numeric values with z-score > 3 |
| `negatives.csv` | Rows containing negative numeric values |

---

## Running the Windows executable (no Python required)

1. Download **`WRAFCT_v1_4.exe`** from the [latest release](../../releases/latest) or the [Actions artifacts](../../actions).
2. Double-click the `.exe` to launch — no Python or pandas installation needed.
3. Click **Select Files** to choose the CSV files you want to process.
4. Click **Browse…** to choose where the output files should be saved.
5. Click **Run**.

> **Windows security note:** Windows may show a SmartScreen warning the first time you run the executable.  
> Click *More info → Run anyway* to proceed.

---

## Building locally (developers)

> **Important:** Windows executables must be built on Windows.  
> You cannot cross-compile a `.exe` from macOS or Linux.

### Prerequisites

- Python 3.9 or later on the system `PATH`
- All other dependencies are installed automatically by the build script

### Steps

```bat
git clone https://github.com/abskuts/TEst1.git
cd TEst1
build_windows_app.bat
```

The script will:
1. Create a clean virtual environment (`.venv`)
2. Install runtime dependencies from `requirements.txt`
3. Install PyInstaller
4. Build a single-file windowed executable using `WRAFCT_v1_4.spec`

Output: `dist\WRAFCT_v1_4.exe`

### Manual PyInstaller command

If you prefer to run PyInstaller directly (with the virtual environment active):

```bat
pyinstaller WRAFCT_v1_4.spec --noconfirm
```

---

## GitHub Actions (automated build)

The workflow [`.github/workflows/build-windows-app.yml`](.github/workflows/build-windows-app.yml) runs automatically on:

- A manual trigger (**Actions → Build Windows App → Run workflow**)
- A push to `main` that modifies the script, packaging files, requirements, or workflow

The built executable is uploaded as the **`WRAFCT_v1_4-windows`** artifact and can be downloaded from the workflow run page.

---

## Repository structure

```
WRAFCT_v1_2_4.py          – Python source (Tkinter application)
requirements.txt           – Runtime dependencies
WRAFCT_v1_4.spec           – PyInstaller build specification
build_windows_app.bat      – Windows build helper script
.github/workflows/
  build-windows-app.yml    – GitHub Actions CI workflow
```