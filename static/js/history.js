/**
 * PRPCEM College Assistant - Chat History Manager
 * Manages the slide-out history drawer, date grouping, loading conversations,
 * and deleting sessions.
 */

(function () {
  const drawer = document.getElementById("historyDrawer");
  const overlay = document.getElementById("drawerOverlay");
  const drawerBody = document.getElementById("historyDrawerBody");
  const closeBtn = document.getElementById("closeHistoryBtn");

  function openDrawer() {
    if (drawer && overlay) {
      drawer.classList.add("active");
      overlay.classList.add("active");
      loadHistoryList();
    }
  }

  function closeDrawer() {
    if (drawer && overlay) {
      drawer.classList.remove("active");
      overlay.classList.remove("active");
    }
  }

  if (closeBtn) closeBtn.addEventListener("click", closeDrawer);
  if (overlay) overlay.addEventListener("click", closeDrawer);

  async function loadHistoryList() {
    if (!drawerBody) return;
    drawerBody.innerHTML = '<div style="text-align:center; padding: 20px; color: var(--text-muted);">Loading history...</div>';

    try {
      const res = await fetch("/api/history");
      const data = await res.json();
      const sessions = data.sessions || [];

      if (sessions.length === 0) {
        drawerBody.innerHTML = '<div style="text-align:center; padding: 30px 10px; color: var(--text-muted); font-size: 0.88rem;">No previous conversations found.</div>';
        return;
      }

      // Group sessions into Today, Yesterday, Older
      const today = new Date().toDateString();
      const yesterdayDate = new Date();
      yesterdayDate.setDate(yesterdayDate.getDate() - 1);
      const yesterday = yesterdayDate.toDateString();

      const groups = {
        "Today": [],
        "Yesterday": [],
        "Older": []
      };

      sessions.forEach(s => {
        const itemDate = new Date(s.last_activity).toDateString();
        if (itemDate === today) {
          groups["Today"].push(s);
        } else if (itemDate === yesterday) {
          groups["Yesterday"].push(s);
        } else {
          groups["Older"].push(s);
        }
      });

      let html = "";
      for (const [groupName, items] of Object.entries(groups)) {
        if (items.length > 0) {
          html += `<div class="history-group">
            <div class="history-group-title">${groupName}</div>`;
          items.forEach(item => {
            const title = escapeHtml(item.first_message || "Conversation");
            html += `
              <div class="history-item" data-session="${item.session_id}">
                <span class="history-item-text" title="${title}">${title}</span>
                <button class="btn-delete-history" data-session="${item.session_id}" title="Delete chat">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <polyline points="3 6 5 6 21 6"></polyline>
                    <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                  </svg>
                </button>
              </div>`;
          });
          html += `</div>`;
        }
      }

      drawerBody.innerHTML = html;

      // Attach click events
      drawerBody.querySelectorAll(".history-item").forEach(el => {
        el.addEventListener("click", (e) => {
          if (e.target.closest(".btn-delete-history")) return;
          const sessId = el.getAttribute("data-session");
          if (window.ChatbotApp && window.ChatbotApp.loadSession) {
            window.ChatbotApp.loadSession(sessId);
            closeDrawer();
          }
        });
      });

      drawerBody.querySelectorAll(".btn-delete-history").forEach(btn => {
        btn.addEventListener("click", async (e) => {
          e.stopPropagation();
          const sessId = btn.getAttribute("data-session");
          if (confirm("Delete this conversation?")) {
            await fetch(`/api/history/${sessId}`, { method: "DELETE" });
            loadHistoryList();
          }
        });
      });

    } catch (err) {
      drawerBody.innerHTML = '<div style="text-align:center; padding: 20px; color: var(--danger-color);">Error loading history.</div>';
    }
  }

  function escapeHtml(text) {
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
  }

  window.HistoryDrawer = {
    open: openDrawer,
    close: closeDrawer
  };
})();
