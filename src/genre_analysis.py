
import sqlite3

connection = sqlite3.connect("page_to_screen.db")

query = """
SELECT
    COALESCE(b.genre, 'Unknown') AS genre,
    COUNT(*) AS adaptation_count
FROM adaptations AS a
JOIN books AS b
    ON a.book_id = b.book_id
GROUP BY COALESCE(b.genre, 'Unknown')
ORDER BY adaptation_count DESC, genre ASC;
"""

results = connection.execute(query).fetchall()

print("Book-to-TV Adaptations by Genre")
print("-" * 45)

for genre, count in results:
    print(f"{genre}: {count}")

connection.close()
