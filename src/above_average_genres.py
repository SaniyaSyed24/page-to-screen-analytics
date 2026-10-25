
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
    b.title AS book_title,
    gc.genre,
    s.title AS tv_show_title,
    gc.adaptation_count
FROM adaptations AS a
JOIN books AS b
    ON a.book_id = b.book_id
JOIN tv_shows AS s
    ON a.show_id = s.show_id
JOIN genre_counts AS gc
    ON gc.genre = COALESCE(b.genre, 'Unknown')
WHERE gc.adaptation_count > (
    SELECT AVG(adaptation_count)
    FROM genre_counts
)
ORDER BY
    gc.adaptation_count DESC,
    gc.genre ASC,
    b.title ASC
LIMIT 10;
"""

results = connection.execute(query).fetchall()

print("Books in above-average adaptation genres")
print("-" * 75)

for book, genre, show, count in results:
    print(f"{book} | {genre} | {show} | Genre count: {count}")

connection.close()
