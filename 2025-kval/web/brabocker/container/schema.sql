CREATE TABLE users (
    id TEXT PRIMARY KEY,
    username TEXT NOT NULL,
    created TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE reviews (
    id INTEGER PRIMARY KEY,
    user_id TEXT  NOT NULL REFERENCES users(id),
    review_title TEXT NOT NULL,
    book_title TEXT NOT NULL,
    isbn TEXT NOT NULL,
    rating INTEGER NOT NULL,
    review TEXT NOT NULL,
    is_draft INTEGER NOT NULL,
    created TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE comments (
    id INTEGER PRIMARY KEY,
    review_id INTEGER NOT NULL REFERENCES reviews(id),
    user_id TEXT NOT NULL REFERENCES users(id),
    comment TEXT NOT NULL,
    created TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
