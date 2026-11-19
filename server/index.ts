import express from "express";
import path from "node:path";

const app = express();
app.use(express.json());

app.get("/api/hello", (req, res) => {
  res.json({ message: "Hallo vom Server" });
});

app.listen(3000, () => console.log("Server läuft auf http://localhost:3000"));
