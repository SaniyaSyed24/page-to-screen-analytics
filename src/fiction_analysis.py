
import sqlite3

connection = sqlite3.connect("page_to_screen.db")

query = """
SELECT
    b.genre,
    COUNT(*) AS adaptation_count
FROM adaptations AS a
JOIN books AS b
    ON a.book_id = b.book_id
WHERE LOWER(COALESCE(b.genre, '')) LIKE '%fiction%'
GROUP BY b.genre
HAVING COUNT(*) >= 2
ORDER BY adaptation_count DESC, b.genre ASC;
"""

results = connection.execute(query).fetchall()

print("Fiction genres with at least 2 adaptation records")
print("-" * 50)

for genre, count in results:
    print(f"{genre}: {count}")

print(f"\nTotal qualifying genres: {len(results)}")

connection.close()
