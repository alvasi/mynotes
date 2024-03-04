CREATE TABLE deadlines (
    id SERIAL PRIMARY KEY,
    userid VARCHAR(100) NOT NULL,
    task TEXT NOT NULL,
    deadline DATE,
    completed BOOLEAN
);

SELECT * FROM deadlines;