CREATE TABLE IF NOT EXISTS alunos (
    id_alun INTEGER PRIMARY KEY,
    nome_alun TEXT COLLATE BINARY,
    port_alun TEXT,
    img_alun TEXT NOT NULL
);