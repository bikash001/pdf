# PDF Reader Utility

Python utility to:
- Open normal or password-protected PDFs
- Read metadata and page count
- Extract text
- Save an unlocked (password-free) copy of a protected PDF

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Usage

Show file info:

```bash
python pdf_reader.py /path/to/file.pdf info --password "your-password"
```

Extract text to terminal:

```bash
python pdf_reader.py /path/to/file.pdf extract-text --password "your-password"
```

Extract text to file:

```bash
python pdf_reader.py /path/to/file.pdf extract-text --password "your-password" --out output.txt
```

Save unlocked copy:

```bash
python pdf_reader.py /path/to/file.pdf unlock --password "your-password" --out unlocked.pdf
```

For non-encrypted files, omit `--password`.
