# Page to Screen — Book-to-TV Adaptation Analytics

A portfolio project for practicing data cleaning, exploratory analysis, relational data modeling, SQL, and Streamlit.

**No adaptation records are fabricated in this starter.** `data/adaptations.csv` contains headers only. Add sourced records before interpreting results or quoting metrics on a resume.

## Setup (Windows / VS Code)

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python src/load_data.py
streamlit run app.py
```

If PowerShell blocks activation, use Command Prompt and run `.venv\Scripts\activate.bat`.

## Add verified records

Fill `data/adaptations.csv`. Each row represents one book-to-TV adaptation relationship.

Columns: `book_title`, `author`, `publication_year`, `genre`, `tv_title`, `first_release_year`, `end_year`, `episode_count`, `platform`, `book_source_url`, `tv_source_url`, `relationship_source_url`.

Use URLs that support the book details, TV details, and the adaptation relationship. Do not infer a relationship from similar titles. Leave unknown optional values blank instead of guessing.

Research starting points:
- Open Library API documentation: https://openlibrary.org/developers/api
- Publisher or library catalogue pages for book metadata
- Official network/streaming pages and reputable reference sources that explicitly confirm the adaptation

Check data-source terms before redistributing records. Keep source URLs and, as the project grows, record access dates and methodology.

## Data model

- `books`: one row per source book
- `tv_shows`: one row per TV show
- `adaptations`: link table between books and shows
- `platforms`: platform lookup
- `show_platforms`: bridge table for shows with multiple platforms

The loader validates required fields, URLs, years, and duplicate relationships. It creates/rebuilds only this project's `page_to_screen.db`; it does not modify the source CSV.

## SQL practice

Run the queries in `sql/queries.sql` using a SQLite extension in VS Code or a SQLite client. With the initial empty CSV, queries correctly return no analytical results.

## Resume integrity

Only describe work you actually completed. Do not claim row counts, findings, model scores, or business impact until they can be reproduced from sourced data and code.
