-- 1. Adaptation counts by genre
SELECT b.genre, COUNT(DISTINCT a.adaptation_id) AS adaptation_count
FROM books b
JOIN adaptations a ON a.book_id = b.book_id
WHERE b.genre IS NOT NULL AND TRIM(b.genre) <> ''
GROUP BY b.genre
ORDER BY adaptation_count DESC, b.genre;

-- 2. CTE + window function: rank genres by adaptation count
WITH genre_counts AS (
    SELECT b.genre, COUNT(DISTINCT a.adaptation_id) AS adaptation_count
    FROM books b
    JOIN adaptations a ON a.book_id = b.book_id
    WHERE b.genre IS NOT NULL AND TRIM(b.genre) <> ''
    GROUP BY b.genre
)
SELECT genre, adaptation_count,
       RANK() OVER (ORDER BY adaptation_count DESC) AS genre_rank
FROM genre_counts
ORDER BY genre_rank, genre;

-- 3. Publication-to-adaptation gap (only where both years are known)
SELECT b.title AS book_title, s.title AS tv_title,
       b.publication_year, s.first_release_year,
       s.first_release_year - b.publication_year AS years_to_adaptation
FROM adaptations a
JOIN books b ON b.book_id = a.book_id
JOIN tv_shows s ON s.show_id = a.show_id
WHERE b.publication_year IS NOT NULL
  AND s.first_release_year IS NOT NULL
  AND s.first_release_year >= b.publication_year
ORDER BY years_to_adaptation;

-- 4. Multi-table join: show, book, and platform
SELECT s.title AS tv_title, b.title AS book_title, p.platform_name
FROM adaptations a
JOIN books b ON b.book_id = a.book_id
JOIN tv_shows s ON s.show_id = a.show_id
LEFT JOIN show_platforms sp ON sp.show_id = s.show_id
LEFT JOIN platforms p ON p.platform_id = sp.platform_id
ORDER BY s.title, b.title, p.platform_name;

-- 5. Rank shows within release year by episode count
SELECT title, first_release_year, episode_count,
       RANK() OVER (
           PARTITION BY first_release_year ORDER BY episode_count DESC
       ) AS episode_rank_in_year
FROM tv_shows
WHERE first_release_year IS NOT NULL AND episode_count IS NOT NULL
ORDER BY first_release_year, episode_rank_in_year;

-- 6. Data quality check: missing relationship sources (expected 0)
SELECT COUNT(*) AS missing_relationship_sources
FROM adaptations
WHERE relationship_source_url IS NULL OR TRIM(relationship_source_url) = '';

-- 7. Books with no linked adaptation (useful if the books table is expanded)
SELECT b.title, b.author
FROM books b
LEFT JOIN adaptations a ON a.book_id = b.book_id
WHERE a.adaptation_id IS NULL
ORDER BY b.title;
