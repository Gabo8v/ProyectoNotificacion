const { Client, LocalAuth } = require("whatsapp-web.js");
const qrcode = require("qrcode-terminal");
const express = require("express");

const app = express();
app.use(express.json());

const client = new Client({
  authStrategy: new LocalAuth(),
  puppeteer: { headless: true },
});

client.on("qr", (qr) => {
  qrcode.generate(qr, { small: true });
  console.log("Escanea el QR con WhatsApp");
});

client.on("ready", () => {
  console.log("Bot de WhatsApp conectado");
});

client.on("message", async (msg) => {
  console.log(`Mensaje recibido de ${msg.from}: ${msg.body}`);

  // Forward incoming message to FastAPI
  try {
    await fetch("http://localhost:8000/whatsapp/webhook", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
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

app.get("/health", (_req, res) => {
  res.json({ status: "ok" });
});

const PORT = 3001;
app.listen(PORT, () => {
  console.log(`WhatsApp bot HTTP server on port ${PORT}`);
});

client.initialize();
