// get_token.js
import fetch from "node-fetch";

const API_BASE = "http://localhost:8000";
const USERNAME = "Boiko_016f5470";
const PASSWORD = "password123";

async function getToken() {
  const params = new URLSearchParams();
  params.append("username", USERNAME);
  params.append("password", PASSWORD);

  try {
    const response = await fetch(`${API_BASE}/token`, {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: params.toString()
    });

    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }

    const data = await response.json();

    if (!data.access_token) {
      console.error("Не отримано токен:", data);
      return;
    }

    console.log("Access token:", data.access_token);
  } catch (err) {
    console.error("Помилка запиту:", err);
  }
}

getToken();
