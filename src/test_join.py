
import sqlite3

# Connect to your existing project database
connection = sqlite3.connect("page_to_screen.db")

query = """
SELECT
    b.title AS book_title,
    s.title AS tv_show_title
FROM adaptations AS a
JOIN books AS b
    ON a.book_id = b.book_id
JOIN tv_shows AS s
    ON a.show_id = s.show_id
LIMIT 10;
"""

results = connection.execute(query).fetchall()

print("Book Title | TV Show Title")
print("-" * 50)

for book_title, tv_show_title in results:
    print(f"{book_title} | {tv_show_title}")

connection.close()
