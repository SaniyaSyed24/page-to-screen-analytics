
import sqlite3

connection = sqlite3.connect("page_to_screen.db")

query = """
SELECT
    b.title AS book_title,
    s.title AS tv_show_title,
    b.publication_year,
    s.first_release_year,
    CASE
        WHEN b.publication_year IS NULL
          OR s.first_release_year IS NULL
            THEN NULL
        ELSE s.first_release_year - b.publication_year
    END AS years_to_adaptation,
    CASE
        WHEN b.publication_year IS NULL
          OR s.first_release_year IS NULL
            THEN 'Missing year'
        WHEN s.first_release_year < b.publication_year
            THEN 'Review: TV release before publication'
        WHEN s.first_release_year - b.publication_year > 100
            THEN 'Review: gap over 100 years'
        ELSE 'No year-based flag'
    END AS review_status
FROM adaptations AS a
JOIN books AS b
    ON a.book_id = b.book_id
JOIN tv_shows AS s
    ON a.show_id = s.show_id
WHERE
    b.publication_year IS NULL
    OR s.first_release_year IS NULL
    OR s.first_release_year < b.publication_year
    OR s.first_release_year - b.publication_year > 100
ORDER BY
    review_status,
    years_to_adaptation DESC;
"""

results = connection.execute(query).fetchall()

print("Adaptation Data-Quality Review")
print("=" * 80)

for book, show, pub_year, release_year, gap, status in results:
    print(
        f"Book: {book} | Show: {show} | "
        f"Publication: {pub_year} | TV: {release_year} | "
        f"Gap: {gap} | Status: {status}"
    )

print(f"\nRecords flagged for review: {len(results)}")

connection.close()
