const path = require("path");
const crypto = require("crypto");
const express = require("express");
const session = require("express-session");
const puppeteer = require("puppeteer");

const app = express();

const port = process.env.PORT || 3333;
const flag = process.env.FLAG || "SSM{example_flag_for_testing}";
const baseUrl = `http://127.0.0.1:${port}/`;
const publicDir = path.join(__dirname, "public");

app.use((req, res, next) => {
  // pls work good
  res.setHeader(
    "Content-Security-Policy",
    "default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; connect-src *;",
  );
  res.setHeader("X-Content-Type-Options", "nosniff");
  next();
});

app.use(express.static(publicDir));
app.use(express.text());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(
  session({
    secret: crypto.randomBytes(32).toString("hex"),
    resave: false,
    saveUninitialized: true,
  }),
);

app.post("/api/aesthetics", (req, res) => {
  const newAesthetic = req.body;
  req.session.aesthetics ??= {};

  const aestheticId = crypto
    .createHash("sha256")
    .update(JSON.stringify(newAesthetic))
    .digest("hex");

  req.session.aesthetics[aestheticId] = newAesthetic;
  res.send({ id: aestheticId });
});

app.get("/api/aesthetics", (req, res) => {
  if (req.headers["mode"] !== "read") {
    return res.status(403).send({
      error: "Not in read mode.",
    });
  }

  const ids = Object.keys(req.session.aesthetics || {});
  res.send({ ids });
});

app.get("/api/aesthetics/:id", (req, res) => {
  if (req.headers["mode"] !== "read") {
    return res.status(403).send({
      error: "Not in read mode.",
    });
  }

  const aesthetic = req.session.aesthetics?.[req.params.id];
  if (!aesthetic) {
    return res.status(404).send({ error: "Aesthetic not found." });
  }

  res.send(aesthetic);
});

app.delete("/api/aesthetics/:id", (req, res) => {
  if (!req.session.aesthetics?.[req.params.id]) {
    return res.status(404).send({ error: "Aesthetic not found." });
  }
  delete req.session.aesthetics[req.params.id];

  res.send({ deleted: true });
});

app.post("/api/admin", async (req, res) => {
  const url = (req.body?.url || "").trim();
  if (!url) {
    res.status(400).send({ error: "Missing url." });
    return;
  }

  if (!url.startsWith("http://") && !url.startsWith("https://")) {
    res.status(400).send({ error: "Only http(s) URLs are allowed." });
    return;
  }

  enqueueAdminVisit(url);
  res.status(202).send({ ok: true, queued: true });
});

async function visitAesthetic(url) {
  const browser = await puppeteer.launch({
    headless: true,
    args: [
      "--no-sandbox",
      "--disable-setuid-sandbox",
      "--disable-dev-shm-usage",
      "--disable-gpu",
    ],
  });

  try {
    const page1 = await browser.newPage();

    await page1.goto(baseUrl, {
      waitUntil: "networkidle2",
      timeout: 5000,
    });

    await page1.waitForSelector("#aesthetic-name");
    await page1.type("#aesthetic-name", "flag");
    await page1.waitForSelector("#aesthetic-description");
    await page1.type("#aesthetic-description", flag);
    await page1.waitForSelector("#save-aesthetic");
    await page1.click("#save-aesthetic");

    await new Promise((resolve) => setTimeout(resolve, 1000));
    await page1.close();

    // visit user page yay
    const page2 = await browser.newPage();

    await page2.goto(url, {
      waitUntil: "networkidle2",
      timeout: 5000,
    });

    await new Promise((resolve) => setTimeout(resolve, 15000));

    await page2.close();
  } finally {
    await browser.close();
  }
}

// --- ratelimit stuff below, not relevant to challenge ---

const adminQueue = [];
let adminInFlight = 0;
const adminConcurrency = 5;

const enqueueAdminVisit = (url) => {
  adminQueue.push({ url, enqueuedAt: Date.now() });
  processAdminQueue();
};

const processAdminQueue = async () => {
  while (adminInFlight < adminConcurrency && adminQueue.length) {
    const job = adminQueue.shift();
    adminInFlight += 1;
    (async () => {
      try {
        await visitAesthetic(job.url);
      } catch (err) {
        console.error("Admin visit failed:", err);
      } finally {
        adminInFlight -= 1;
        if (adminQueue.length) {
          setImmediate(processAdminQueue);
        }
      }
    })();
  }
};

app.listen(port, () => {
  console.log(`Server listening on port ${port}`);
});
