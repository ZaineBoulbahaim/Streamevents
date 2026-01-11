document.addEventListener('DOMContentLoaded', () => {
    const chatContainer = document.querySelector('.chat-container');
    if(!chatContainer) return;

    const chatMessages = document.getElementById('chat-messages');
    const chatForm = document.getElementById('chat-form');
    const chatInput = document.getElementById('chat-input');
    const chatErrors = document.getElementById('chat-errors');
    const messageCountBadge = document.getElementById('message-count');
    const eventId = chatContainer.dataset.eventId;
    console.log('Event ID:', eventId);
    console.log('Chat container:', chatContainer);
    console.log('Dataset completo:', chatContainer.dataset);
    const IS_CREATOR = chatContainer.dataset.isCreator === "true";

    function escapeHtml(text) {
        return text.replace(/&/g, "&amp;")
                   .replace(/</g, "&lt;")
                   .replace(/>/g, "&gt;")
                   .replace(/"/g, "&quot;")
                   .replace(/'/g, "&#039;");
    }

    function updateMessageCount(count) {
        if(messageCountBadge) messageCountBadge.textContent = count;
    }

    function scrollToBottom() {
        if(chatMessages) chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function createMessageElement(msg) {
        const div = document.createElement('div');
        div.className = `chat-message mb-2 ${msg.is_highlighted ? 'highlighted' : ''}`;
        div.dataset.messageId = msg.id;

        let actionsHtml = '';
        if(msg.can_delete) actionsHtml += `<button class="btn btn-sm btn-danger delete-message">🗑</button>`;
        if(IS_CREATOR) actionsHtml += `<button class="btn btn-sm btn-warning highlight-message">${msg.is_highlighted ? '⭐' : '☆'}</button>`;

        div.innerHTML = `
            <div class="message-header d-flex justify-content-between">
                <strong>${escapeHtml(msg.display_name)}</strong>
                <small class="text-muted">${escapeHtml(msg.created_at)}</small>
            </div>
            <div class="message-content">${escapeHtml(msg.message)}</div>
            <div class="message-actions">${actionsHtml}</div>
        `;
        return div;
    }

    async function loadMessages() {
        if(!eventId) return;
        try {
            const res = await fetch(`/chat/load/${eventId}/`);
            if(!res.ok) throw new Error('Error cargando mensajes');
            const data = await res.json();
            chatMessages.innerHTML = '';
            data.messages.forEach(msg => chatMessages.appendChild(createMessageElement(msg)));
            updateMessageCount(data.messages.length);
            scrollToBottom();
        } catch(err) {
            console.error("Error cargando mensajes:", err);
            if(chatErrors) chatErrors.textContent = 'No se pudieron cargar los mensajes.';
        }
    }

    async function sendMessage(e) {
        e.preventDefault();
        if(!chatInput || !chatInput.value.trim() || !eventId) return;

        try {
            const formData = new URLSearchParams();
            formData.append('message', chatInput.value.trim());
            const res = await fetch(`/chat/send/${eventId}/`, {
                method: 'POST',
                headers: {'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value},
                body: formData
            });
            const data = await res.json();
            if(data.success) {
                chatInput.value = '';
                chatErrors.textContent = '';
                loadMessages();
            } else {
                chatErrors.textContent = data.error || JSON.stringify(data.errors);
            }
        } catch(err) {
            console.error("Error enviando mensaje:", err);
            if(chatErrors) chatErrors.textContent = 'No se pudo enviar el mensaje.';
        }
    }

    async function deleteMessage(messageId) {
        if(!confirm("Segur que vols eliminar aquest missatge?")) return;
        try {
            const res = await fetch(`/chat/delete/${messageId}/`, {
                method: 'POST',
                headers: {'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value},
            });
            const data = await res.json();
            if(data.success) loadMessages();
            else alert(data.error);
        } catch(err) {
            console.error("Error eliminando mensaje:", err);
        }
    }

    async function highlightMessage(messageId) {
        try {
            const res = await fetch(`/chat/highlight/${messageId}/`, {
                method: 'POST',
                headers: {'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value},
            });
            const data = await res.json();
            if(data.success) loadMessages();
            else alert(data.error);
        } catch(err) {
            console.error("Error destacando mensaje:", err);
        }
    }

    // Delegación para botones dentro de chat
    chatMessages.addEventListener('click', (e) => {
        const msgDiv = e.target.closest('.chat-message');
        if(!msgDiv) return;
        const messageId = msgDiv.dataset.messageId;
        if(e.target.classList.contains('delete-message')) deleteMessage(messageId);
        if(e.target.classList.contains('highlight-message')) highlightMessage(messageId);
    });
    console.log('Chat form found:', chatForm);
    if(chatForm) chatForm.addEventListener('submit', sendMessage);

    loadMessages();
    setInterval(loadMessages, 3000); // polling cada 3 segundos
});
