const express = require('express');
const mysql = require('mysql2');

const app = express();
const PORT = 3000;

const pool = mysql.createPool({
  host: process.env.DB_HOST || 'nyheter-db',
  user: process.env.DB_USER || 'news_user',
  password: process.env.DB_PASSWORD || 'news_password',
  database: process.env.DB_NAME || 'news_db',
  waitForConnections: true,
  connectionLimit: 10,
  queueLimit: 0
});

const promisePool = pool.promise();

app.use(express.static('public'));
app.use(express.json());

app.get('/api/news', async (req, res) => {
  try {
    const [rows] = await promisePool.query(
      'SELECT id, title FROM news WHERE is_public = TRUE ORDER BY created_at DESC'
    );
    res.json(rows);
  } catch (error) {
    console.error('Databasfel:', error);
    res.status(500).json({ error: 'Databasfel' });
  }
});

app.get('/api/news/:id', async (req, res) => {
  try {
    const { id } = req.params;
    const [rows] = await promisePool.query(
      'SELECT id, title, content FROM news WHERE id = ? AND is_public = TRUE',
      [id]
    );

    if (rows.length === 0) {
      res.status(404).json({ error: 'Artikel hittades inte' });
    } else {
      res.json(rows[0]);
    }
  } catch (error) {
    console.error('Databasfel:', error);
    res.status(500).json({ error: 'Databasfel' });
  }
});

app.get('/api/search', async (req, res) => {
  try {
    const { q } = req.query;

    if (!q) {
      return res.status(400).json({ error: 'Sökfråga krävs' });
    }

    const searchPattern = `%${q}%`;
    const [rows] = await promisePool.query(
      'SELECT id, title, is_public, COUNT(*) OVER() as total FROM news WHERE title LIKE ? ORDER BY created_at DESC',
      [searchPattern]
    );

    const publicRows = rows.filter(row => row.is_public === 1);
    const count = rows.length > 0 ? rows[0].total : 0;

    const result = publicRows.map(row => ({
      id: row.id,
      title: row.title
    }));

    res.json({ results: result, count: count });
  } catch (error) {
    console.error('Databasfel:', error);
    res.status(500).json({ error: 'Databasfel' });
  }
});

app.listen(PORT, () => {
  console.log(`Server körs på port ${PORT}`);
});
