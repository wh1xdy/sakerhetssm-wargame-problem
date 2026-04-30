'use strict'
const express = require('express');
const path = require('path');
const app = express();
const port = 3000;

app.use(express.json());
app.use(express.static(
  path.join(__dirname),
  {}, //TODO can we rely on default settings?
));

function deepMerge(obj1, obj2) {
  const result = obj1;
  const keys = new Set(
    Object.getOwnPropertyNames(obj1).concat(
      Object.getOwnPropertyNames(obj2)
    ))
  keys.forEach(key => {
    if (key in obj1 && key in obj2) {
      if (typeof obj1[key] === 'object' && typeof obj2[key] === 'object') {
        result[key] = deepMerge(obj1[key], obj2[key], key);
      }
    } else if (key in obj2) {
      result[key] = obj2[key];
    }
  })
  return result;
}

app.post('/join', (req, res) => {

  try {
    const { obj1, obj2 } = req.body;

    if (!obj1 || !obj2) {
      return res.status(400).json({
        error: 'Both obj1 and obj2 are required in request body'
      });
    }

    if (typeof obj1 !== 'object' || typeof obj2 !== 'object' || Array.isArray(obj1) || Array.isArray(obj2)) {
      return res.status(400).json({
        error: 'Both obj1 and obj2 must be valid JSON objects'
      });
    }

    const joinedObject = deepMerge(obj1, obj2);

    res.json({
      success: true,
      result: joinedObject
    });
  } catch (error) {
    res.status(500).json({
      error: 'Internal server error',
      message: error.message
    });
  }
});

app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'index.html'));
});

app.listen(port, () => {
  console.log(`Server running at http://localhost:${port}`);
});