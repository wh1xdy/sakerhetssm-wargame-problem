-- name: GetReviews :many
SELECT reviews.*, users.username
FROM reviews
INNER JOIN users ON users.id = reviews.user_id
ORDER BY reviews.id DESC;

-- name: GetReview :one
SELECT reviews.*, users.username
FROM reviews
INNER JOIN users ON users.id = reviews.user_id
WHERE reviews.id = ?;

-- name: CreateReview :exec
INSERT INTO reviews (
    user_id,
    review_title,
    book_title,
    isbn,
    rating,
    review,
    is_draft
) VALUES (?, ?, ?, ?, ?, ?, ?);

-- name: GetComments :many
SELECT comments.*, users.username
FROM comments
INNER JOIN users ON comments.user_id = users.id
WHERE review_id = ?
ORDER BY comments.id;

-- name: CreateComment :exec
INSERT INTO comments (review_id, user_id, comment) VALUES (?, ?, ?);

-- name: CreateUser :exec
INSERT INTO users (id, username) VALUES (?, ?);

-- name: GetUsername :one
SELECT username FROM users WHERE id = ?;
