/**
 * Virtual FDE + AI + Cybersecurity Advisor Chatbot Widget
 * Starts minimized in the bottom-right corner; pops up on hover or click
 * asking "How can I help you?" and answers via Gemini LLM + RAG.
 */
(function () {
    const INITIAL_GREETING = "Hi! I'm your virtual FDE + AI + Cybersecurity Advisor. How can I help you?";

    let isOpen = false;
    let isBusy = false;
    let suppressHoverUntil = 0;
    let chatHistory = [];

    function getEls() {
        return {
            root: document.getElementById("fde-advisor-chatbot"),
            launcher: document.getElementById("fde-chat-launcher"),
            panel: document.getElementById("fde-chat-panel"),
            minimizeBtn: document.getElementById("fde-chat-minimize-btn"),
            resetBtn: document.getElementById("fde-chat-reset-btn"),
            messages: document.getElementById("fde-chat-messages"),
            quickPrompts: document.getElementById("fde-chat-quick-prompts"),
            form: document.getElementById("fde-chat-form"),
            input: document.getElementById("fde-chat-input"),
            sendBtn: document.getElementById("fde-chat-send-btn"),
        };
    }

    function escapeHtml(str) {
        return String(str || "")
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#39;");
    }

    function scrollToBottom() {
        const { messages } = getEls();
        if (messages) {
            messages.scrollTop = messages.scrollHeight;
        }
    }

    function appendMessage(role, text, meta = {}) {
        const { messages } = getEls();
        if (!messages) return;

        const row = document.createElement("div");
        row.className = role === "user" ? "fde-chat-row fde-chat-row-user" : "fde-chat-row fde-chat-row-bot";

        if (role === "user") {
            row.innerHTML = `<div class="fde-chat-bubble fde-chat-bubble-user">${escapeHtml(text)}</div>`;
        } else {
            let badgeHtml = "";
            if (meta.mode === "out_of_scope") {
                badgeHtml = `<span class="fde-chat-tag fde-chat-tag-oos">Out of Scope</span>`;
            } else if (meta.mode === "gemini_rag") {
                badgeHtml = `<span class="fde-chat-tag fde-chat-tag-gemini">Gemini + RAG</span>`;
            } else if (meta.mode === "rag") {
                badgeHtml = `<span class="fde-chat-tag fde-chat-tag-rag">RAG Grounded</span>`;
            }

            let sourcesHtml = "";
            if (Array.isArray(meta.sources) && meta.sources.length > 0 && meta.in_scope !== false) {
                const topSource = escapeHtml(meta.sources[0]);
                sourcesHtml = `<span class="fde-chat-source" title="Grounded reference">${topSource}</span>`;
            }

            const metaBlock = (badgeHtml || sourcesHtml)
                ? `<div class="fde-chat-meta">${badgeHtml}${sourcesHtml}</div>`
                : "";

            row.innerHTML = `
                <div class="fde-chat-avatar-mini" aria-hidden="true">
                    <i class="bi bi-headset"></i>
                </div>
                <div class="fde-chat-bubble fde-chat-bubble-bot">
                    <div>${escapeHtml(text)}</div>
                    ${metaBlock}
                </div>
            `;
        }

        messages.appendChild(row);
        scrollToBottom();
    }

    function showTypingIndicator() {
        const { messages } = getEls();
        if (!messages) return;
        removeTypingIndicator();
        const typing = document.createElement("div");
        typing.id = "fde-chat-typing";
        typing.className = "fde-chat-row fde-chat-row-bot";
        typing.innerHTML = `
            <div class="fde-chat-avatar-mini" aria-hidden="true">
                <i class="bi bi-headset"></i>
            </div>
            <div class="fde-chat-bubble fde-chat-bubble-bot fde-chat-typing-bubble">
                <span class="fde-dot"></span><span class="fde-dot"></span><span class="fde-dot"></span>
            </div>
        `;
        messages.appendChild(typing);
        scrollToBottom();
    }

    function removeTypingIndicator() {
        const el = document.getElementById("fde-chat-typing");
        if (el) el.remove();
    }

    function renderInitialGreeting() {
        const { messages, quickPrompts } = getEls();
        if (!messages) return;
        messages.innerHTML = "";
        chatHistory = [];
        appendMessage("bot", INITIAL_GREETING, { mode: "greeting" });
        if (quickPrompts) {
            quickPrompts.classList.remove("hidden");
        }
    }

    function openChatbot(focusInput = true) {
        const { launcher, panel, input, messages } = getEls();
        if (!launcher || !panel) return;
        if (isOpen) {
            if (focusInput && input) input.focus();
            return;
        }
        isOpen = true;
        if (messages && messages.children.length === 0) {
            renderInitialGreeting();
        }
        launcher.classList.add("fde-chat-hidden");
        launcher.setAttribute("aria-expanded", "true");
        panel.classList.remove("fde-chat-hidden");
        panel.classList.add("fde-chat-pop-in");
        scrollToBottom();
        if (focusInput && input) {
            setTimeout(() => input.focus(), 80);
        }
    }

    function minimizeChatbot() {
        const { launcher, panel } = getEls();
        if (!launcher || !panel) return;
        isOpen = false;
        suppressHoverUntil = Date.now() + 550;
        panel.classList.add("fde-chat-hidden");
        panel.classList.remove("fde-chat-pop-in");
        launcher.classList.remove("fde-chat-hidden");
        launcher.setAttribute("aria-expanded", "false");
    }

    async function sendQuestion(questionText) {
        const text = (questionText || "").trim();
        if (!text || isBusy) return;

        const { input, sendBtn, quickPrompts } = getEls();
        if (quickPrompts) {
            quickPrompts.classList.add("hidden");
        }

        appendMessage("user", text);
        if (input) {
            input.value = "";
        }

        isBusy = true;
        if (sendBtn) sendBtn.disabled = true;
        showTypingIndicator();

        try {
            const response = await fetch("/api/advisor-chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    message: text,
                    history: chatHistory.slice(-4),
                }),
            });
            const data = await response.json();
            removeTypingIndicator();

            const reply = (data && data.answer)
                ? data.answer
                : "Sorry, I couldn't process that right now. Please ask an FDE, AI, or Cybersecurity question.";

            appendMessage("bot", reply, {
                mode: data.mode,
                in_scope: data.in_scope,
                sources: data.sources || [],
            });

            chatHistory.push({ role: "user", content: text });
            chatHistory.push({ role: "model", content: reply });
        } catch (err) {
            removeTypingIndicator();
            appendMessage(
                "bot",
                "Connection issue reaching the Advisor service. Please try again in a moment.",
                { mode: "error" }
            );
        } finally {
            isBusy = false;
            if (sendBtn) sendBtn.disabled = false;
            if (input && isOpen) input.focus();
        }
    }

    function initAdvisorChatbot() {
        const { root, launcher, minimizeBtn, resetBtn, form, input, quickPrompts } = getEls();
        if (!root || !launcher) return;

        // Always start in minimized state with initial greeting prepped inside
        renderInitialGreeting();

        // Popup on hover OR click on the minimized corner widget
        launcher.addEventListener("mouseenter", function () {
            if (Date.now() < suppressHoverUntil) return;
            openChatbot(true);
        });

        launcher.addEventListener("click", function (e) {
            e.preventDefault();
            e.stopPropagation();
            openChatbot(true);
        });

        if (minimizeBtn) {
            minimizeBtn.addEventListener("click", function (e) {
                e.preventDefault();
                e.stopPropagation();
                minimizeChatbot();
            });
        }

        if (resetBtn) {
            resetBtn.addEventListener("click", function (e) {
                e.preventDefault();
                e.stopPropagation();
                renderInitialGreeting();
                if (input) input.focus();
            });
        }

        if (quickPrompts) {
            quickPrompts.addEventListener("click", function (e) {
                const chip = e.target.closest(".fde-chat-chip");
                if (!chip) return;
                e.preventDefault();
                e.stopPropagation();
                const q = chip.getAttribute("data-question") || chip.textContent;
                sendQuestion(q);
            });
        }

        if (form) {
            form.addEventListener("submit", function (e) {
                e.preventDefault();
                e.stopPropagation();
                if (input) {
                    sendQuestion(input.value);
                }
            });
        }

        document.addEventListener("keydown", function (e) {
            if (e.key === "Escape" && isOpen) {
                minimizeChatbot();
            }
        });
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", initAdvisorChatbot);
    } else {
        initAdvisorChatbot();
    }
})();
