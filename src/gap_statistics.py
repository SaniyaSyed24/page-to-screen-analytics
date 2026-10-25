
import sqlite3

connection = sqlite3.connect("page_to_screen.db")

query = """
SELECT
    COUNT(*) AS total_records,
    ROUND(
        AVG(s.first_release_year - b.publication_year),
        2
    ) AS average_gap_years,
    MIN(s.first_release_year - b.publication_year)
        AS shortest_gap_years,
    MAX(s.first_release_year - b.publication_year)
        AS longest_gap_years,
    SUM(
        CASE
            WHEN s.first_release_year - b.publication_year > 100
            THEN 1
            ELSE 0
        END
    ) AS gaps_over_100_years
FROM adaptations AS a
JOIN books AS b
    ON a.book_id = b.book_id
JOIN tv_shows AS s
    ON a.show_id = s.show_id
WHERE b.publication_year IS NOT NULL
  AND s.first_release_year IS NOT NULL;
"""

result = connection.execute(query).fetchone()

print("Adaptation Gap Statistics")
print("-" * 40)
print(f"Total records: {result[0]}")
print(f"Average gap: {result[1]} years")
print(f"Shortest gap: {result[2]} years")
print(f"Longest gap: {result[3]} years")
print(f"Gaps over 100 years: {result[4]}")

connection.close()
