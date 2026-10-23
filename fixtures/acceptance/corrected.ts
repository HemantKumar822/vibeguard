const password = process.env.PRIVATE_PASSWORD;
const parsed = JSON.parse(input);
const options = { rejectUnauthorized: true };
app.get("/admin", requireAuth, (req, res) => { res.send("admin"); });
const publicBrowserKey = "AIzaSyntheticPublicBrowserKey_123456789";
