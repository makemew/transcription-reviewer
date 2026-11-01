# Audio Transcription Reviewer

`review.py` is a PyQt6 desktop interface for navigating call records. It displays each record's UUID, transcript, status, and progress, and plays the matching WAV file. The team's working Google Sheet is separate from this program; the local interface was used alongside it for reference and navigation.

The original code is included without changes. It **does not modify `data.xlsx`**. On startup, it reads that workbook and creates or overwrites a local `data.csv`. Actions in the interface write transcript text and status to `data.csv`, and the current position to `progress.txt`. These local files are not synchronized with Google Sheets.

## Input files

Run the program from a folder containing:

```text
transcription-reviewer/
├── review.py
├── data.xlsx
└── adresses/
    ├── <call_uuid>.wav
    └── ...
```

The first row of `data.xlsx` must contain the headers `call_uuid` and `transcript`. A `status` column is optional. The folder name `adresses` is preserved from the original code. Audio files are looked up as `<call_uuid>.wav`.

## Setup

From this folder, run:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python review.py
```

On Windows, activate the environment with `.venv\Scripts\activate`. The application requires a graphical desktop environment and Qt support for WAV playback.

## Controls

`Previous` returns to the previous record; `Open Audio` plays the file; `OK`, `FIXED`, and `SKIP` set a local status; and `Find UUID` jumps to a record. `Ctrl+S` saves the current text to the local CSV. `Enter` sets `OK`, `Backspace` goes back, and `Space` opens the audio. The `+` and `-` buttons adjust playback speed.

## Diagnostic scripts

- `check.py` prints the first 10 rows of `data.xlsx` without treating the first row as headers. It helps inspect the workbook structure.
- `detect.py` detects the likely encoding of the first 100 KB of local `data.csv`. Run it after `review.py` has created the CSV, or when a CSV already exists.

Both scripts use files in the current working directory. Real spreadsheets, WAV recordings, `data.csv`, and `progress.txt` are excluded from the repository.

## Known behavior of the original code

- Every new launch recreates `data.csv` from `data.xlsx`, so edits made only in the local CSV can be lost. Keep the working sheet separately.
- After the final record, automatic navigation may try to open audio beyond the table and raise an error. Restart the program if this happens.
- The position is restored from `progress.txt`; if you replace the workbook, you may need to remove the old progress file.
