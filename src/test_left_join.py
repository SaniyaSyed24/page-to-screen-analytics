
import sqlite3

connection = sqlite3.connect("page_to_screen.db")

query = """
SELECT
    b.title AS book_title
FROM books AS b
LEFT JOIN adaptations AS a
    ON b.book_id = a.book_id
WHERE a.book_id IS NULL;
"""

results = connection.execute(query).fetchall()

print("Books without recorded adaptations:")
print("-" * 45)

if results:
    for (book_title,) in results:
        print(book_title)
else:
    print("No books found without recorded adaptations.")

print(f"\nTotal books without recorded adaptations: {len(results)}")

connection.close()
