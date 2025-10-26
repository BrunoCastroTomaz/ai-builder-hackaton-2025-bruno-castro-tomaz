const input = document.getElementById("input");
const send = document.getElementById("send");
const messages = document.getElementById("messages");

function addMessage(text, who="bot") {
  const el = document.createElement("div");
  el.classList.add("message", who);
  el.innerText = text;
  messages.appendChild(el);
  messages.scrollTop = messages.scrollHeight; // scroll automático
}

async function sendMessage() {
  const q = input.value.trim();
  if (!q) return;
  addMessage(q, "user");
  input.value = "";
  const loading = "...";
  addMessage(loading, "bot");
  try {
    const res = await fetch("/ask", {
      method: "POST",
      headers: {"Content-Type":"application/json"},
      body: JSON.stringify({question: q})
    });
    const data = await res.json();
    // remove último loading
    messages.removeChild(messages.lastChild);
    addMessage(data.answer, "bot");
  } catch (err) {
    messages.removeChild(messages.lastChild);
    addMessage("Erro ao contatar o servidor.", "bot");
  }
}

// Eventos
send.onclick = sendMessage;
input.addEventListener("keydown", (e) => { if(e.key === "Enter") sendMessage(); });
