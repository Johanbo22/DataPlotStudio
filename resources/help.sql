CREATE TABLE IF NOT EXISTS help_topics (
    topic_id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    image_url TEXT,
    link TEXT
);

INSERT INTO help_topics (topic_id, title, description, image_url, link)
VALUES (
    'remove_duplicates',
    'Remove Duplicates',
    'This tool removes rows that are duplicates.

    You can choose to check for duplicates across all columns or only specifc ones.

    1. Select Columns: Choose the columns to check for duplicate values.
    2. Keep: Decide whether to keep the ''first'' or ''last'' occurrence of the duplicate row.
    3. Run: Click to process the data.

    This operation is irreversible, so you may want to create a subset of your data first.',
        'resources/images/remove_duplicates.png',

        'https://www.data-plot-studio.com/documentation/tools/remove-duplicates'
);