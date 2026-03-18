const express = require('express');
const puppeteer = require('puppeteer');

const app = express();
const PORT = process.env.PORT || 3000;

app.use(express.json());
app.use(express.urlencoded({ extended: true }));

app.get('/', (req, res) => {
  res.send(`
    <!DOCTYPE html>
    <html>
    <head>
      <title>Puppeteer Poetry Viewer</title>
      <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }
        h1 { color: #333; }
        form { margin: 20px 0; }
        input[type="text"] { width: 70%; padding: 10px; font-size: 16px; }
        button { padding: 10px 20px; font-size: 16px; background: #007bff; color: white; border: none; cursor: pointer; }
        button:hover { background: #0056b3; }
        .result { margin-top: 20px; border: 1px solid #ddd; padding: 10px; }
        img { max-width: 100%; height: auto; }
      </style>
    </head>
    <body>
      <h1>Puppeteer Poetry Viewer</h1>
      <p>Flag is in a cookie, the poetry critic will look at any URL.</p>

      <h2>Review Poem</h2>
      <form action="/review-poem" method="GET">
        <input type="text" name="url" placeholder="https://example.com" required />
        <button type="submit">Review Poem</button>
      </form>
    </body>
    </html>
  `);
});


app.get('/review-poem', async (req, res) => {
  const { url } = req.query;

  if (!url) {
    return res.status(400).send('URL parameter is required');
  }

  let browser;
  try {
    browser = await puppeteer.launch({
      headless: 'new',
      args: [
        '--no-sandbox',
        '--disable-setuid-sandbox',
        '--disable-dev-shm-usage',
        '--disable-gpu'
      ]
    });

    const page = await browser.newPage();
    await page.goto('https://flourishing-narwhal-ba7f26.netlify.app');
    await page.setCookie({
      name: "flag",
      value: 'SSM{d0nt_tru5st_th3_t7p3s}'
    })

    await page.goto(url, { waitUntil: 'networkidle2', timeout: 30000 });


    res.send(`Poem viewed.`);
  } catch (error) {
    console.error('Error getting HTML:', error);
    res.status(500).send(`Error: ${error.message}`);
  } finally {
    if (browser) {
      await browser.close();
    }
  }
});


app.listen(PORT, () => {
  console.log(`Puppeteer viewer server running on http://localhost:${PORT}`);
});
