
import sqlite3

connection = sqlite3.connect("page_to_screen.db")

query = """
WITH genre_counts AS (
    SELECT
        COALESCE(b.genre, 'Unknown') AS genre,
        COUNT(*) AS adaptation_count
    FROM adaptations AS a
    JOIN books AS b
        ON a.book_id = b.book_id
    GROUP BY COALESCE(b.genre, 'Unknown')
)
SELECT
    genre,
    adaptation_count,
    ROUND(
        adaptation_count * 100.0
        / SUM(adaptation_count) OVER (),
        2
    ) AS percentage
FROM genre_counts
ORDER BY adaptation_count DESC, genre ASC;
"""

results = connection.execute(query).fetchall()

print(f"{'Genre':35} {'Count':>7} {'Percentage':>12}")
print("-" * 57)

for genre, count, percentage in results:
    print(f"{genre:35} {count:>7} {percentage:>11.2f}%")

connection.close()
