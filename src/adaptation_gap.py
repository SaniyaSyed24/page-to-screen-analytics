
import sqlite3

connection = sqlite3.connect("page_to_screen.db")

query = """
SELECT
    b.title AS book_title,
    s.title AS tv_show_title,
    b.publication_year,
    s.first_release_year,
    s.first_release_year - b.publication_year AS years_to_adaptation
FROM adaptations AS a
JOIN books AS b
    ON a.book_id = b.book_id
JOIN tv_shows AS s
    ON a.show_id = s.show_id
WHERE b.publication_year IS NOT NULL
  AND s.first_release_year IS NOT NULL
ORDER BY years_to_adaptation DESC
LIMIT 20;
"""

results = connection.execute(query).fetchall()

print("Book-to-TV Adaptation Time Gap")
print("-" * 85)

for book, show, pub_year, release_year, gap in results:
    print(
        f"{book} | {show} | "
        f"Book: {pub_year} | TV: {release_year} | "
        f"Gap: {gap} years"
    )

connection.close()
