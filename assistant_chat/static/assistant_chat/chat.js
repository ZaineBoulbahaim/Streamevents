// Seleccionamos los elementos del DOM que usaremos
const chatBox = document.getElementById("chatBox");
const userMessageInput = document.getElementById("userMessage");
const sendButton = document.getElementById("sendBtn");
const onlyFutureCheckbox = document.getElementById("onlyFuture");
const loadingBox = document.getElementById("loadingBox");
const eventsBox = document.getElementById("eventsBox");

// Función para hacer scroll automático al último mensaje
function scrollToBottom() {
  chatBox.scrollTop = chatBox.scrollHeight;
}

// Función para añadir una burbuja de mensaje al chat
// role: "user" o "assistant"
// text: contenido del mensaje
// Devuelve la burbuja para poder modificarla después (útil en streaming)
function addBubble(role, text) {
  const wrapper = document.createElement("div");
  const bubble = document.createElement("div");

  if (role === "user") {
    // Burbuja del usuario: alineada a la derecha, fondo azul
    wrapper.className = "d-flex justify-content-end";
    bubble.className = "bg-primary text-white rounded p-2 px-3";
  } else {
    // Burbuja del asistente: alineada a la izquierda, fondo gris claro
    wrapper.className = "d-flex justify-content-start";
    bubble.className = "bg-light border rounded p-2 px-3";
  }

  bubble.style.maxWidth = "75%";
  bubble.innerText = text;
  wrapper.appendChild(bubble);
  chatBox.appendChild(wrapper);

  scrollToBottom();
  return bubble;
}

// Función para renderizar las cards de eventos recomendados
function renderEventCards(events) {
  eventsBox.innerHTML = "";

  if (events.length === 0) return;

  // Título de la sección
  const title = document.createElement("h5");
  title.innerText = "Esdeveniments recomanats";
  title.className = "mb-3";
  eventsBox.appendChild(title);

  // Creamos una card de Bootstrap por cada evento
  events.forEach(event => {
    const card = document.createElement("div");
    card.className = "card mb-3 shadow-sm";
    card.innerHTML = `
      <div class="card-body">
        <h5 class="card-title">
          <a href="${event.url}">${event.title}</a>
        </h5>
        <p class="card-text">
          <span class="badge bg-secondary">${event.category || "Sense categoria"}</span>
          <span class="ms-2 text-muted">
            ${event.scheduled_date ? new Date(event.scheduled_date).toLocaleDateString("ca-ES") : ""}
          </span>
        </p>
        <small class="text-muted">Rellevància: ${event.score}</small>
      </div>
    `;
    eventsBox.appendChild(card);
  });
}

async function sendMessage() {
  const message = userMessageInput.value.trim();
  if (!message) return;

  userMessageInput.value = "";

  // Eliminamos el mensaje de bienvenida si existe
  const welcome = chatBox.querySelector(".text-center");
  if (welcome) welcome.remove();

  // Añadimos la burbuja del usuario
  addBubble("user", message);

  // Mostramos el spinner
  loadingBox.classList.remove("d-none");
  eventsBox.innerHTML = "";

  try {
    // Hacemos la petición POST al endpoint de streaming
    const response = await fetch("/assistant/api/stream/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message: message,
        only_future: onlyFutureCheckbox.checked
      })
    });

    // Ocultamos el spinner y creamos la burbuja del asistente vacía
    loadingBox.classList.add("d-none");
    const assistantBubble = addBubble("assistant", "");

    // Leemos el stream usando ReadableStream
    // (usamos fetch en lugar de EventSource porque EventSource no soporta POST)
    const reader = response.body.getReader();
    const decoder = new TextDecoder("utf-8");
    let buffer = "";

    // Acumulamos todos los tokens aquí para parsear el JSON al final
    let fullText = "";

    while (true) {
      // Leemos el siguiente chunk del stream
      const { done, value } = await reader.read();
      if (done) break;

      // Decodificamos el chunk de bytes a texto
      buffer += decoder.decode(value, { stream: true });

      // Procesamos todas las líneas completas del buffer
      // SSE llega en formato: "data: contenido\n\n"
      const lines = buffer.split("\n\n");

      // La última parte puede estar incompleta, la guardamos para el siguiente chunk
      buffer = lines.pop();

      for (const line of lines) {
        if (!line.startsWith("data: ")) continue;

        // Extraemos el contenido después de "data: "
        const data = line.slice(6);

        if (data === "[DONE]") {
          // Stream terminado: parseamos el JSON acumulado y mostramos solo el answer
          try {
            const llmJson = JSON.parse(fullText);

            // Mostramos solo el answer en la burbuja, no el JSON completo
            assistantBubble.innerText = llmJson.answer || fullText;

            // Si hay follow_up lo añadimos debajo del answer
            if (llmJson.follow_up) {
              assistantBubble.innerText += "\n\n💬 " + llmJson.follow_up;
            }
          } catch (e) {
            // Si no es JSON válido, mostramos el texto acumulado tal cual
            assistantBubble.innerText = fullText;
          }
          scrollToBottom();
          break;

        } else if (data.startsWith("EVENTS:")) {
          // Evento especial con los datos de los eventos en JSON
          const eventsData = JSON.parse(data.slice(7));
          renderEventCards(eventsData);

        } else {
          // Acumulamos el token sin mostrarlo todavía
          // porque necesitamos el JSON completo para parsearlo
          const token = data.replace(/\\n/g, "\n");
          fullText += token;

          // Mostramos puntos suspensivos para que el usuario sepa que está generando
          assistantBubble.innerText = "...";
        }
      }
    }

  } catch (error) {
    loadingBox.classList.add("d-none");
    addBubble("assistant", "❌ Hi ha hagut un error. Torna-ho a intentar.");
    console.error("Error:", error);
  }
}

// Enviar al hacer clic en el botón
sendButton.addEventListener("click", sendMessage);

// Enviar también al pulsar Enter en el input
userMessageInput.addEventListener("keydown", (event) => {
  if (event.key === "Enter") sendMessage();
});

// Al cargar la página, hacer scroll al último mensaje del historial
scrollToBottom();