document.getElementById("chat-toggle").onclick = function () {
    let chat = document.getElementById("chat-container");
    const helpPrompt = document.getElementById("help-prompt");
    let isOpen = chat.style.display === "flex";
    chat.style.display = isOpen ? "none" : "flex";

    if (isOpen) {
        showSuggestions([
            "What services do you offer?",
            "Do you build websites?",
            "How can I contact you?"
        ]);
    }
    else{
       showSuggestions([
            "What services do you offer?",
            "Do you build websites?",
            "How can I contact you?"
        ]); 
        helpPrompt.style.display = "none";
    }
};
document.getElementById("sendBtn").onclick = function(e) {
    e.preventDefault();
    sendMessage();
};
document.getElementById("userInput").addEventListener("keypress", function(e) {
    if (e.key === "Enter") {
        sendMessage();
    }
});

window.onload = function() {
    setTimeout(function() {
        document.getElementById("help-prompt").style.display = "block";
    },1000);
};
document.getElementById("close-chat").onclick = function() {
    document.getElementById("help-prompt").style.display = "none";
};
document.getElementById("close-chat-btn").onclick = function () {
    document.getElementById("chat-container").style.display = "none";
};

document.getElementById("open-chat").onclick = function(e) {
    e.stopPropagation();

    document.getElementById("help-prompt").style.display = "none";
    document.getElementById("chat-container").style.display = "flex";
    showSuggestions([
        "What services do you offer?",
        "Do you build websites?",
        "How can I contact you?"
    ]);
};

document.addEventListener("click", function (event) {
    let chat = document.getElementById("chat-container");
    let toggle = document.getElementById("chat-toggle");
    let openBtn = document.getElementById("open-chat");

    if (
        !chat.contains(event.target) &&
        !toggle.contains(event.target) &&
        !openBtn.contains(event.target)
    ) {
        chat.style.display = "none";
        document.getElementById("help-prompt").style.display = "none";
    }
});
function showSuggestions(suggestions) {
    let container = document.getElementById("suggestions");
    container.innerHTML = "";

    if (!suggestions || suggestions.length === 0) {
        container.style.display = "none";
        return;
    }

    suggestions.forEach(text => {
        let btn = document.createElement("button");
        btn.innerText = text;
        btn.className = "suggest-btn";

        btn.onclick = function () {
            sendMessage(text);
        };

        container.appendChild(btn);
    });

    container.style.display = "flex";
}
function sendMessage(customMessage = null) {
    let inputField = document.getElementById("userInput");
    let message = customMessage || inputField.value.trim();

    const loader = document.getElementById("loader"); // loader element

    if (!message) return;

    let chatbox = document.getElementById("chatbox");

    chatbox.innerHTML += `
    <div class="message user">
        <div class="avatar">👤</div>
        <span>${message}</span>
    </div>`;

    loader.style.display = "block"; // show loader

    fetch("/chat", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ message: message })
    })
    .then(res => res.json())
    .then(data => {
        console.log("API Response:", data);
        loader.style.display = "none"; // hide loader

        chatbox.innerHTML += `
        <div class="message bot">
            <span>${data.response}</span>
        </div>`;

        chatbox.scrollTop = chatbox.scrollHeight;

        if (data.suggestions && data.suggestions.length > 0) {
            showSuggestions(data.suggestions);
        } else {
            showSuggestions([]);
        }
    });

    inputField.value = "";
}

document.getElementById("new-tab-btn").onclick = function(e) {
    e.stopPropagation();
    let chatbox = document.getElementById("chatbox");
    chatbox.innerHTML = `
        <div class="bot-message">👋 Hi there! I'm Nimbad assistant. How can I help you today?</div>`;
    showSuggestions([
        "What services do you offer?",
        "Do you build websites?",
        "How can I contact you?"
    ]);
}