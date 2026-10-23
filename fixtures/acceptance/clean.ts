const parsed = JSON.parse(input);
app.get("/protected", requireAuth, (req, res) => { res.send("ok"); });
const publicBrowserKey = "AIzaSyntheticPublicBrowserKey_123456789";
