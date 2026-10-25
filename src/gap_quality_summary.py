
import sqlite3

connection = sqlite3.connect("page_to_screen.db")

query = """
WITH reviewed_records AS (
    SELECT
        CASE
            WHEN b.publication_year IS NULL
              OR s.first_release_year IS NULL
                THEN 'Missing year'
            WHEN s.first_release_year < b.publication_year
                THEN 'TV release before publication'
            WHEN s.first_release_year - b.publication_year > 100
                THEN 'Gap over 100 years'
            ELSE 'No year-based flag'
        END AS review_status
    FROM adaptations AS a
    JOIN books AS b
        ON a.book_id = b.book_id
    JOIN tv_shows AS s
        ON a.show_id = s.show_id
)
SELECT
    review_status,
    COUNT(*) AS record_count
FROM reviewed_records
GROUP BY review_status
ORDER BY record_count DESC, review_status ASC;
"""

results = connection.execute(query).fetchall()

print("Data Quality Summary")
print("-" * 50)

for status, count in results:
    print(f"{status}: {count}")

print(f"\nTotal records checked: {sum(count for _, count in results)}")

connection.close()
