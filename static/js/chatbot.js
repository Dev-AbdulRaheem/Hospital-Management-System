/**
 * Simple FAQ chatbot — keyword matching (no external API).
 */
var FAQ = [
  { q: ["hours", "timing", "open"], a: "Outpatient hours: Mon–Sat 8:00 AM – 8:00 PM. Emergency is 24/7." },
  { q: ["appointment", "book"], a: "Use Book Appointment after signing in as a patient, or call +1 (555) 123-4567." },
  { q: ["insurance", "payment"], a: "We accept major insurance plans. Billing desk can confirm coverage at visit." },
  { q: ["emergency", "ambulance"], a: "Emergency entrance is on the east side; dial local emergency services or our front desk." },
  { q: ["visitor", "visiting"], a: "Visiting hours for wards: 4:00 PM – 7:00 PM daily (ICU rules may differ)." },
  { q: ["report", "lab"], a: "Lab reports are available at the patient portal after your doctor reviews them." },
];

function findAnswer(text) {
  var lower = text.toLowerCase();
  for (var i = 0; i < FAQ.length; i++) {
    for (var j = 0; j < FAQ[i].q.length; j++) {
      if (lower.indexOf(FAQ[i].q[j]) !== -1) return FAQ[i].a;
    }
  }
  return "Thanks for your question. For specific medical advice, please contact our reception or your physician.";
}

document.addEventListener("DOMContentLoaded", function () {
  var panel = document.getElementById("chatbotPanel");
  var log = document.getElementById("chatbotLog");
  var input = document.getElementById("chatbotInput");
  var toggle = document.getElementById("chatbotToggle");
  var closeBtn = document.querySelector("[data-chatbot-close]");
  if (!panel || !log || !toggle) return;

  toggle.addEventListener("click", function () {
    var open = panel.classList.toggle("open");
    toggle.setAttribute("aria-expanded", open ? "true" : "false");
  });
  if (closeBtn) {
    closeBtn.addEventListener("click", function () {
      panel.classList.remove("open");
      toggle.setAttribute("aria-expanded", "false");
    });
  }

  function appendLine(who, msg) {
    var div = document.createElement("div");
    div.className = "chat-line";
    div.innerHTML = "<strong>" + who + ":</strong> " + msg;
    log.appendChild(div);
    log.scrollTop = log.scrollHeight;
  }

  document.getElementById("chatbotSend").addEventListener("click", function () {
    var t = (input.value || "").trim();
    if (!t) return;
    appendLine("You", t);
    input.value = "";
    setTimeout(function () {
      appendLine("Assistant", findAnswer(t));
    }, 400);
  });
});
