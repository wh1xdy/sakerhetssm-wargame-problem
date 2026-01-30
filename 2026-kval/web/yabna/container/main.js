const path = require("path");
const crypto = require("crypto");
const express = require("express");
const puppeteer = require("puppeteer");
const cookieParser = require("cookie-parser");

const app = express();

const port = process.env.PORT || 3333;
const adminCookie = crypto.randomBytes(32).toString("hex");
const flagAccessToken = crypto.randomBytes(32).toString("hex");
const flag = process.env.FLAG || "SSM{example_flag_for_testing}";
const baseUrl = process.env.BASE_URL || `http://127.0.0.1:${port}/`;
const flagId = crypto.randomUUID();

const publicDir = path.join(__dirname, "public");
const sendPublicFile = (res, filename) =>
  res.sendFile(path.join(publicDir, filename));

const notes = new Map();
notes.set(flagId, { note: flag, owner: "admin" });

const clearNotes = () => {
  notes.clear();
  notes.set(flagId, { note: flag, owner: "admin" });
};

setInterval(clearNotes, 15 * 60 * 1000);

const checkAdmin = (req) => {
  const accessToken = (req.query.access || "").toString().trim();
  return (
    req.cookies &&
    req.cookies.admin === adminCookie &&
    accessToken === flagAccessToken
  );
};

app.use((req, res, next) => {
  // pls work good
  res.setHeader(
    "Content-Security-Policy",
    `default-src 'none'; script-src 'self'; style-src 'unsafe-inline'; frame-src *; connect-src 'self'; form-action 'self'; base-uri 'none';`,
  );
  res.setHeader("X-Content-Type-Options", "nosniff");
  next();
});
app.use(cookieParser());
app.use((req, res, next) => {
  let sessionId = req.cookies?.sid;
  if (!sessionId) {
    sessionId = crypto.randomBytes(16).toString("hex");
    res.cookie("sid", sessionId, {
      httpOnly: true,
      secure: false,
      sameSite: "Lax",
    });
    req.cookies.sid = sessionId;
  }
  req.sessionId = sessionId;
  next();
});
app.use(express.static(publicDir));
app.use(express.urlencoded({ extended: false }));
app.use(express.json({ limit: "16kb" }));

app.get("/", (req, res) => sendPublicFile(res, "index.html"));
app.get("/notes", (req, res) => sendPublicFile(res, "note.html"));
app.get("/search", (req, res) => sendPublicFile(res, "search.html"));
app.get("/admin", (req, res) => sendPublicFile(res, "admin.html"));

app.post("/api/notes", (req, res) => {
  const note = (req.body.note || "").trim();

  // pls no fake flags
  if (!note || note.toLowerCase().startsWith(flag.toLowerCase().slice(0, 3))) {
    res.status(400).send("Bad note.");
    return;
  }

  const id = crypto.randomUUID();
  notes.set(id, { note, owner: req.sessionId });
  res.redirect(`/notes#${id}`);
});

app.get("/api/notes/search", (req, res) => {
  const query = (req.query.q || "").trim().toLowerCase();
  const isAdmin = checkAdmin(req);

  if (!query) {
    res.status(400).json({ error: "Query cannot be empty." });
    return;
  }
  if (query.length < 3) {
    res.status(400).json({ error: "Query must be at least 3 characters." });
    return;
  }

  const results = [];
  for (const [id, noteEntry] of notes.entries()) {
    if (!noteEntry.note.toLowerCase().startsWith(query)) {
      continue;
    }
    if (!isAdmin && noteEntry.owner !== req.sessionId) {
      continue;
    }
    // DO NOT LEAK SECRETS TO NON-ADMINS
    if (noteEntry.note.includes(flag) && !isAdmin) {
      continue;
    }

    const entry = {
      id,
      note:
        noteEntry.note.length > 100
          ? noteEntry.note.substring(0, 100) + "..."
          : noteEntry.note,
    };
    results.push(entry);
  }

  res.json({ results: results.slice(0, 4) });
});

app.get("/api/notes/:id", (req, res) => {
  const entry = notes.get(req.params.id);
  if (!entry) {
    res.status(404).json({ error: "Note not found." });
    return;
  }

  const isAdmin = checkAdmin(req);
  if (entry.note.includes(flag) && !isAdmin) {
    res.status(403).json({
      error: "Forbidden: Admin access required for flag notes.",
    });
    return;
  }

  res.json({ id: req.params.id, note: entry.note });
});

app.post("/api/admin", async (req, res) => {
  const url = (req.body?.url || req.query?.url || "").trim();
  if (!url) {
    res.status(400).json({ error: "Missing url." });
    return;
  }

  const key = req.sessionId || req.cookies?.sid || "unknown";
  if (!consumeAdminRate(key)) {
    res
      .status(429)
      .json({ error: "Too many admin requests. Try again later." });
    return;
  }

  enqueueAdminVisit(url);
  res.status(202).json({ ok: true, queued: true });
});

app.get("/api/flag/healthcheck", (req, res) => {
  const flagEntry = notes.get(flagId);
  if (!flagEntry || flagEntry.note !== flag) {
    res.status(500).json({ status: "error", error: "Flag note missing." });
    return;
  }
  res.json({ status: "ok", message: "Flag note present with id " + flagId });
});

async function visitNote(url) {
  const browser = await puppeteer.launch({
    headless: "shell",
    args: [
      "--no-sandbox",
      "--disable-setuid-sandbox",
      "--disable-dev-shm-usage",
      "--disable-gpu",
    ],
  });

  try {
    const page = await browser.newPage();

    await page.goto(`${baseUrl}`, {
      waitUntil: "networkidle2",
      timeout: 5000,
    });
    await page.setCookie({
      name: "admin",
      value: adminCookie,
      url: baseUrl,
      httpOnly: true,
      secure: false,
      sameSite: "Lax",
    });
    await page.close();

    const page2 = await browser.newPage();

    await page2.goto(url, {
      waitUntil: "networkidle2",
      timeout: 5000,
    });

    // If flag note, enter access token
    if (
      page2.url().startsWith(baseUrl) &&
      page2.url().includes("notes#") &&
      page2.url().split("notes#")[1] === flagId
    ) {
      await page2.click("#access");
      await page2.keyboard.type(flagAccessToken);
    }

    await new Promise((resolve) => setTimeout(resolve, 20000));

    await page2.close();
  } finally {
    await browser.close();
  }
}

// --- ratelimit stuff below, not relevant to challenge ---

const adminQueue = [];
let adminInFlight = 0;
const adminConcurrency = 5;
/* const adminJobTtlMs = 60 * 1000; */
const adminRate = {
  windowMs: 60 * 1000,
  max: 3,
  hits: new Map(),
};

const consumeAdminRate = (key) => {
  const now = Date.now();
  const entry = adminRate.hits.get(key);
  if (!entry || now - entry.start >= adminRate.windowMs) {
    adminRate.hits.set(key, { start: now, count: 1 });
    return true;
  }
  if (entry.count >= adminRate.max) {
    return false;
  }
  entry.count += 1;
  return true;
};

const enqueueAdminVisit = (url) => {
  adminQueue.push({ url, enqueuedAt: Date.now() });
  processAdminQueue();
};

const processAdminQueue = async () => {
  while (adminInFlight < adminConcurrency && adminQueue.length) {
    const job = adminQueue.shift();
    /* if (Date.now() - job.enqueuedAt > adminJobTtlMs) {
      continue;
    } */
    adminInFlight += 1;
    (async () => {
      try {
        await visitNote(job.url);
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
