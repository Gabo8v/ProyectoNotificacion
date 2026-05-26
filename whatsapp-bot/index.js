const { Client, LocalAuth } = require("whatsapp-web.js");
const qrcode = require("qrcode-terminal");
const QR = require("qrcode");
const express = require("express");
const path = require("path");

const app = express();
app.use(express.json());

const client = new Client({
  authStrategy: new LocalAuth(),
  puppeteer: {
    headless: true,
    executablePath: "C:\\Program Files\\BraveSoftware\\Brave-Browser\\Application\\brave.exe",
    args: ["--no-sandbox", "--disable-gpu"],
  },
});

let latestQr = null;

client.on("qr", (qr) => {
  latestQr = qr;
  qrcode.generate(qr, { small: true });
  console.log("Escanea el QR con WhatsApp");
  const outPath = path.join(__dirname, "..", "qr.png");
  QR.toFile(outPath, qr, { type: "png", width: 512, margin: 2 }, (err) => {
    if (!err) console.log("QR guardado en qr.png");
  });
});

client.on("ready", () => {
  console.log("Bot de WhatsApp conectado");
});

client.on("message", async (msg) => {
  console.log(`Mensaje recibido de ${msg.from}: ${msg.body}`);

  // Forward incoming message to FastAPI
  try {
    const headers = { "Content-Type": "application/json" };
    const apiKey = process.env.WEBHOOK_API_KEY || "";
    if (apiKey) headers["X-API-Key"] = apiKey;
    await fetch("http://localhost:8002/whatsapp/webhook", {
      method: "POST",
      headers,
      body: JSON.stringify({
        from: msg.from,
        body: msg.body,
        messageId: msg.id._serialized,
        timestamp: msg.timestamp,
      }),
    });
  } catch (err) {
    console.error("Error forwarding to FastAPI:", err.message);
  }
});

// Endpoint for FastAPI to send messages
app.post("/send-message", async (req, res) => {
  const { to, message } = req.body;
  if (!to || !message) {
    return res.status(400).json({ error: "to and message are required" });
  }
  try {
    const response = await client.sendMessage(to, message);
    res.json({ success: true, messageId: response.id._serialized });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

app.get("/qr-image", (_req, res) => {
  if (!latestQr) return res.status(404).json({ error: "No QR available" });
  QR.toDataURL(latestQr, { type: "image/png", width: 512, margin: 2 }, (err, url) => {
    if (err) return res.status(500).json({ error: err.message });
    res.send(`<img src="${url}" style="image-rendering:pixelated;width:512px;height:512px"/>`);
  });
});

app.get("/qr-raw", (_req, res) => {
  if (!latestQr) return res.status(404).json({ error: "No QR available" });
  QR.toDataURL(latestQr, { type: "image/png", width: 1024, margin: 4 }, (err, url) => {
    if (err) return res.status(500).json({ error: err.message });
    res.json({ qr: url });
  });
});

app.get("/health", (_req, res) => {
  res.json({ status: "ok" });
});

const PORT = 3001;
app.listen(PORT, () => {
  console.log(`WhatsApp bot HTTP server on port ${PORT}`);
});

client.initialize();
