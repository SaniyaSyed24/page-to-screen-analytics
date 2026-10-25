
import sqlite3

connection = sqlite3.connect("page_to_screen.db")

query = """
SELECT
    b.title AS book_title,
    s.title AS tv_show_title,
    b.publication_year,
    s.first_release_year,
    s.first_release_year - b.publication_year AS years_to_adaptation,
    b.book_source_url,
    s.tv_source_url
FROM adaptations AS a
JOIN books AS b
    ON a.book_id = b.book_id
JOIN tv_shows AS s
    ON a.show_id = s.show_id
WHERE b.publication_year IS NOT NULL
  AND s.first_release_year IS NOT NULL
  AND s.first_release_year - b.publication_year > 100
ORDER BY years_to_adaptation DESC;
"""

results = connection.execute(query).fetchall()

print("Flagged Adaptations — Source Review")
print("=" * 80)

for row in results:
    book, show, pub_year, release_year, gap, book_url, show_url = row

    print(f"\nBook: {book}")
    print(f"TV show: {show}")
    print(f"Publication year: {pub_year}")
    print(f"TV release year: {release_year}")
    print(f"Calculated gap: {gap} years")
    print(f"Book source: {book_url}")
    print(f"TV source: {show_url}")

print(f"\nTotal records to review: {len(results)}")

connection.close()
