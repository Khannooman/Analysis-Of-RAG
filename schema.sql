CREATE TABLE IF NOT  Users(
    id TEXT,
    email VARCHAR(50) NOT NULL,
    name VARCHAR(30) NOT NULL,
    date_of_birth DATE NOT NULL,
    phone VARCHAR(20) NOT NULL,
    create_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT user_pk PRIMARY KEY (id),
    CONSTRAINT email_unique UNIQUE (email),
    CONSTRAINT phone_unique UNIQUE (phone)
);

CREATE TABLE IF NOT chat_history(
    id TEXT,
    session_id TEXT NOT NULL,
    user_id TEXT,
    message TEXT NOT NULL,
    role TEXT NOT NULL,
    CURRENT_TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chat_history_pk PRIMARY KEY (id),
    CONSTRAINT chat_history FOREIGN KEY (user_id) REFERENCES Users (user_id)
)


