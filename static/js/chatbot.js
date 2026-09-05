/**
 * PRPCEM College Assistant - Main Chat Interface Logic
 * Handles session tracking, message rendering, typing indicators,
 * cutoff card generation, three-dot menu actions, and quick chips.
 */

(function () {
  let sessionId = sessionStorage.getItem("prpcem_session_id");
  if (!sessionId) {
    sessionId = "sess_" + Math.random().toString(36).substring(2, 10) + "_" + Date.now();
    sessionStorage.setItem("prpcem_session_id", sessionId);
  }

  const chatFeed = document.getElementById("chatFeed");
  const welcomeScreen = document.getElementById("welcomeScreen");
  const chatInput = document.getElementById("chatInput");
  const sendBtn = document.getElementById("sendBtn");
  const typingRow = document.getElementById("typingRow");

  // Three-dot menu elements
  const threeDotBtn = document.getElementById("threeDotBtn");
  const threeDotMenu = document.getElementById("threeDotMenu");
  const menuClearChat = document.getElementById("menuClearChat");
  const menuNewChat = document.getElementById("menuNewChat");
  const menuHistory = document.getElementById("menuHistory");

  // Modals
  const clearChatModal = document.getElementById("clearChatModal");
  const btnCancelClear = document.getElementById("btnCancelClear");
  const btnConfirmClear = document.getElementById("btnConfirmClear");

  const themeModal = document.getElementById("themeModal");
  const themeBtn = document.getElementById("themeBtn");
  const closeThemeModalBtn = document.getElementById("closeThemeModalBtn");

  // Initialize
  setupEvents();
  if (window.VoiceModule && window.VoiceModule.init) {
    window.VoiceModule.init();
  }

  function setupEvents() {
    // Input & Auto-grow
    if (chatInput) {
      chatInput.addEventListener("input", () => {
        chatInput.style.height = "auto";
        chatInput.style.height = Math.min(chatInput.scrollHeight, 120) + "px";
        sendBtn.disabled = !chatInput.value.trim();
      });

      chatInput.addEventListener("keydown", (e) => {
        if (e.key === "Enter" && !e.shiftKey) {
          e.preventDefault();
          if (chatInput.value.trim() && !sendBtn.disabled) {
            handleSendMessage();
          }
        }
      });
    }

    if (sendBtn) {
      sendBtn.addEventListener("click", handleSendMessage);
    }

    // Quick Action Chips
    document.querySelectorAll(".chip-btn").forEach(btn => {
      btn.addEventListener("click", () => {
        const query = btn.getAttribute("data-query");
        if (query) {
          chatInput.value = query;
          chatInput.style.height = "auto";
          sendBtn.disabled = false;
          handleSendMessage();
        }
      });
    });

    // Three-dot menu toggle (Requirement #33)
    if (threeDotBtn && threeDotMenu) {
      threeDotBtn.addEventListener("click", (e) => {
        e.stopPropagation();
        threeDotMenu.classList.toggle("show");
      });

      document.addEventListener("click", (e) => {
        if (!threeDotMenu.contains(e.target) && e.target !== threeDotBtn) {
          threeDotMenu.classList.remove("show");
        }
      });
    }

    // Clear Chat Action (Requirement #34)
    if (menuClearChat) {
      menuClearChat.addEventListener("click", () => {
        threeDotMenu.classList.remove("show");
        if (clearChatModal) clearChatModal.classList.add("show");
      });
    }

    if (btnCancelClear && clearChatModal) {
      btnCancelClear.addEventListener("click", () => {
        clearChatModal.classList.remove("show");
      });
    }

    if (btnConfirmClear && clearChatModal) {
      btnConfirmClear.addEventListener("click", () => {
        clearChatModal.classList.remove("show");
        // Clears only current visual conversation, preserves in history
        document.querySelectorAll(".message-row").forEach(el => el.remove());
        if (welcomeScreen) welcomeScreen.style.display = "flex";
      });
    }

    // New Chat Action (Requirement #35)
    if (menuNewChat) {
      menuNewChat.addEventListener("click", () => {
        threeDotMenu.classList.remove("show");
        startNewChatSession();
      });
    }

    // History Action (Requirement #36)
    if (menuHistory) {
      menuHistory.addEventListener("click", () => {
        threeDotMenu.classList.remove("show");
        if (window.HistoryDrawer) window.HistoryDrawer.open();
      });
    }

    // Voice Settings Menu Action (Requirement #10 & #11)
    const menuVoiceSettings = document.getElementById("menuVoiceSettings");
    if (menuVoiceSettings) {
      menuVoiceSettings.addEventListener("click", () => {
        threeDotMenu.classList.remove("show");
        if (window.VoiceModule && window.VoiceModule.openVoiceSettings) {
          window.VoiceModule.openVoiceSettings();
        }
      });
    }

    // Microphone Voice Input (Requirement #10)
    const micBtn = document.getElementById("micBtn");
    if (micBtn) {
      micBtn.addEventListener("click", () => {
        if (window.VoiceModule) {
          if (window.VoiceModule.isListening()) {
            window.VoiceModule.stopListening();
          } else {
            window.VoiceModule.startListening();
          }
        }
      });
    }

    // Theme Modal Triggers (Requirement #38)
    if (themeBtn && themeModal) {
      themeBtn.addEventListener("click", () => {
        themeModal.classList.add("show");
      });
    }

    if (closeThemeModalBtn && themeModal) {
      closeThemeModalBtn.addEventListener("click", () => {
        themeModal.classList.remove("show");
      });
    }

    // Theme Selector Options
    document.querySelectorAll(".theme-option-row").forEach(row => {
      row.addEventListener("click", () => {
        const themeVal = row.getAttribute("data-theme-val");
        if (window.ThemeManager) {
          window.ThemeManager.apply(themeVal);
        }
      });
    });
  }

  function startNewChatSession() {
    sessionId = "sess_" + Math.random().toString(36).substring(2, 10) + "_" + Date.now();
    sessionStorage.setItem("prpcem_session_id", sessionId);
    document.querySelectorAll(".message-row").forEach(el => el.remove());
    if (welcomeScreen) welcomeScreen.style.display = "flex";
    if (chatInput) {
      chatInput.value = "";
      chatInput.focus();
    }
  }

  async function handleSendMessage() {
    const text = chatInput.value.trim();
    if (!text) return;

    // Hide welcome screen
    if (welcomeScreen) welcomeScreen.style.display = "none";

    // Append User Message
    appendMessage(text, "user");
    chatInput.value = "";
    chatInput.style.height = "auto";
    sendBtn.disabled = true;

    // Show Typing Indicator (Requirement #42)
    showTyping(true);
    scrollToBottom();

    try {
      const response = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: text, session_id: sessionId })
      });

      const data = await response.json();
      showTyping(false);

      // Render Bot Message with card formatting if present
      appendBotResponse(data);
    } catch (err) {
      showTyping(false);
      appendMessage("Unable to connect to college server. Please try again.", "bot", {
        source: "System Error",
        source_url: null
      });
    }

    scrollToBottom();
    if (chatInput) chatInput.focus();
  }

  function appendMessage(text, sender, meta = null) {
    const row = document.createElement("div");
    row.className = `message-row ${sender}`;

    const now = new Date();
    const timeStr = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

    if (sender === "user") {
      row.innerHTML = `
        <div class="bubble-container">
          <div class="message-bubble">
            <div class="bubble-content">${escapeHtml(text)}</div>
          </div>
          <div class="message-meta">${timeStr}</div>
        </div>
      `;
    } else {
      let contentHtml = formatMarkdown(text);
      row.innerHTML = `
        <div class="avatar">
          <img src="/static/images/logo.svg" alt="PRPCEM">
        </div>
        <div class="bubble-container">
          <div class="message-bubble">
            <div class="bubble-content">${contentHtml}</div>
            ${renderSourceBadge(meta ? meta.source : null, meta ? meta.source_url : null)}
          </div>
          <div class="message-meta">PRPCEM Assistant • ${timeStr}</div>
        </div>
      `;
      if (window.VoiceModule && window.VoiceModule.attachSpeakerBtn) {
        const bubble = row.querySelector(".message-bubble");
        if (bubble) window.VoiceModule.attachSpeakerBtn(bubble, text);
      }
    }

    chatFeed.appendChild(row);
  }

  function appendBotResponse(data) {
    const row = document.createElement("div");
    row.className = "message-row bot";

    const now = new Date();
    const timeStr = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

    let extraHtml = "";

    // Requirement #21: Modern Cutoff UI Card
    if (data.card_type === "cutoff_card" && Array.isArray(data.card_data)) {
      extraHtml += renderCutoffCards(data.card_data, data.disclaimer);
    }

    const contentHtml = formatMarkdown(data.answer);

    row.innerHTML = `
      <div class="avatar">
        <img src="/static/images/logo.svg" alt="PRPCEM">
      </div>
      <div class="bubble-container" style="width: 100%;">
        <div class="message-bubble">
          <div class="bubble-content">${contentHtml}</div>
          ${extraHtml}
          ${renderSourceBadge(data.source, data.source_url)}
        </div>
        <div class="message-meta">PRPCEM Assistant • ${timeStr}</div>
      </div>
    `;

    if (window.VoiceModule && window.VoiceModule.attachSpeakerBtn) {
      const bubble = row.querySelector(".message-bubble");
      if (bubble) window.VoiceModule.attachSpeakerBtn(bubble, data.answer);
    }

    chatFeed.appendChild(row);
  }

  function renderCutoffCards(cards, disclaimer) {
    let html = "";
    cards.forEach(c => {
      html += `
        <div class="cutoff-card">
          <div class="cutoff-card-header">
            <span>PRPCEM ${escapeHtml(c.branch)} CUTOFF</span>
            <span>CAP Round ${c.cap_round}</span>
          </div>
          <div class="cutoff-card-body">
            <div class="cutoff-item">
              <span class="label">Academic Year</span>
              <span class="value">${escapeHtml(c.academic_year)}</span>
            </div>
            <div class="cutoff-item">
              <span class="label">Category</span>
              <span class="value">${escapeHtml(c.category)}</span>
            </div>
            <div class="cutoff-item">
              <span class="label">Cutoff Type</span>
              <span class="value">${escapeHtml(c.cutoff_type)}</span>
            </div>
            <div class="cutoff-item highlight">
              <span class="label">Closing Score</span>
              <span class="value">${escapeHtml(c.cutoff_value)}</span>
            </div>
          </div>
          <div class="cutoff-card-footer">
            <span>${escapeHtml(c.source_name)}</span>
            <a href="${escapeHtml(c.source_url)}" target="_blank" rel="noopener" class="source-btn">View Source ↗</a>
          </div>
        </div>
      `;
    });

    if (disclaimer) {
      html += `<div class="cutoff-disclaimer">${escapeHtml(disclaimer)}</div>`;
    }

    return html;
  }

  function renderSourceBadge(sourceName, sourceUrl) {
    if (!sourceName && !sourceUrl) return "";
    const name = sourceName || "PRPCEM Official Verified Source";
    const url = sourceUrl || "https://prpotepatilengg.ac.in/";

    return `
      <div class="source-badge-box">
        <span class="source-label">
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path>
          </svg>
          Source: ${escapeHtml(name)}
        </span>
        <a href="${escapeHtml(url)}" target="_blank" rel="noopener" class="source-btn">
          View Source ↗
        </a>
      </div>
    `;
  }

  function formatMarkdown(text) {
    if (!text) return "";
    let formatted = escapeHtml(text);

    // Bold **text**
    formatted = formatted.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");

    // Italic *text*
    formatted = formatted.replace(/\*(.*?)\*/g, "<em>$1</em>");

    // Convert bullet points (• or -)
    const lines = formatted.split("\n");
    let inList = false;
    let result = [];

    lines.forEach(line => {
      const trimmed = line.trim();
      if (trimmed.startsWith("• ") || trimmed.startsWith("- ")) {
        if (!inList) {
          result.push("<ul>");
          inList = true;
        }
        result.push(`<li>${trimmed.substring(2)}</li>`);
      } else {
        if (inList) {
          result.push("</ul>");
          inList = false;
        }
        if (trimmed) {
          result.push(`<p>${trimmed}</p>`);
        }
      }
    });

    if (inList) result.push("</ul>");
    return result.join("");
  }

  function showTyping(show) {
    if (typingRow) {
      if (show) {
        typingRow.classList.add("active");
        chatFeed.appendChild(typingRow);
      } else {
        typingRow.classList.remove("active");
      }
    }
  }

  function scrollToBottom() {
    setTimeout(() => {
      chatFeed.scrollTop = chatFeed.scrollHeight;
    }, 50);
  }

  function escapeHtml(text) {
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
  }

  // Load an existing session into chat feed
  async function loadSession(sessId) {
    try {
      const res = await fetch(`/api/history?session_id=${sessId}`);
      const data = await res.json();
      const messages = data.messages || [];

      document.querySelectorAll(".message-row").forEach(el => el.remove());
      if (welcomeScreen) welcomeScreen.style.display = "none";

      sessionId = sessId;
      sessionStorage.setItem("prpcem_session_id", sessionId);

      messages.forEach(m => {
        appendMessage(m.user_message, "user");
        appendMessage(m.bot_response, "bot", {
          source: "PRPCEM Chat History",
          source_url: m.source_url
        });
      });

      scrollToBottom();
    } catch (e) {
      console.error("Error loading session:", e);
    }
  }

  // Export to window
  window.ChatbotApp = {
    loadSession: loadSession,
    startNewChat: startNewChatSession
  };
})();
