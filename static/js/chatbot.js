document.getElementById("chat-toggle").onclick = function () {
    let chat = document.getElementById("chat-container");
    chat.style.display = chat.style.display === "flex" ? "none" : "flex";
};
document.getElementById("sendBtn").onclick = sendMessage;
document.getElementById("userInput").addEventListener("keypress", function(e) {
    if (e.key === "Enter") {
        sendMessage();
    }
});

function sendMessage() {
    let inputField = document.getElementById("userInput");
    let message = inputField.value.trim();

    if (message === "") return;

    let chatbox = document.getElementById("chatbox");

    // USER MESSAGE (hardcoded avatar)
    chatbox.innerHTML += `
    <div class="message user">
        <div class="avatar">👤</div>
        <span>${message}</span>
    </div>`;

    fetch("/chat", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ message: message })
    })
    .then(res => res.json())
    .then(data => {
        chatbox.innerHTML += `
        <div class="message bot">
            <span>${data.response}</span>
        </div>`;

        chatbox.scrollTop = chatbox.scrollHeight;
    });

    inputField.value = "";
}