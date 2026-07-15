import { useState, useRef, useEffect } from "react";
import { sendChatMessage } from "../services/api";

const SUGGESTIONS = [
  "Best time to fly Mumbai to Goa?",
  "Will prices rise for Diwali?",
  "Cheapest day to fly Delhi-Bangalore?",
];

export default function ChatAssistant() {
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState([
    { role: "bot", text: "Hi! I'm your PriceLens travel assistant. Ask me about flight prices, best travel dates, or festival impact." },
  ]);
  const [input, setInput] = useState("");
  const [typing, setTyping] = useState(false);
  const scrollRef = useRef(null);

  useEffect(() => {
    if (scrollRef.current) scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
  }, [messages, typing]);

  const send = async (text) => {
    const msg = (text ?? input).trim();
    if (!msg || typing) return;
    setMessages((m) => [...m, { role: "user", text: msg }]);
    setInput("");
    setTyping(true);
    try {
      const data = await sendChatMessage(msg);
      setMessages((m) => [...m, { role: "bot", text: data.reply }]);
    } catch {
      setMessages((m) => [...m, { role: "bot", text: "Sorry, I couldn't reach the assistant right now." }]);
    } finally {
      setTyping(false);
    }
  };

  return (
    <>
      {open && (
        <div className="chat-panel">
          <div className="chat-panel-header">
            <span>✈ Travel Assistant</span>
            <button className="modal-close" style={{ position: "static", width: 26, height: 26 }} onClick={() => setOpen(false)}>✕</button>
          </div>
          <div className="chat-messages" ref={scrollRef}>
            {messages.map((m, i) => (
              <div key={i} className={`chat-msg ${m.role}`}>
                <div className={m.role === "bot" ? "bot-avatar" : "user-avatar"}>{m.role === "bot" ? "✈" : "👤"}</div>
                <div className="msg-bubble">{m.text}</div>
              </div>
            ))}
            {typing && (
              <div className="chat-msg bot">
                <div className="bot-avatar">✈</div>
                <div className="msg-bubble">
                  <div className="typing-indicator">
                    <div className="typing-dot" /><div className="typing-dot" /><div className="typing-dot" />
                  </div>
                </div>
              </div>
            )}
            {messages.length === 1 && (
              <div style={{ display: "flex", flexDirection: "column", gap: 6, marginTop: 4 }}>
                {SUGGESTIONS.map((s) => (
                  <button key={s} className="time-btn" style={{ textAlign: "left" }} onClick={() => send(s)}>{s}</button>
                ))}
              </div>
            )}
          </div>
          <div className="chat-input-bar">
            <input
              className="chat-input"
              placeholder="Ask about flights, prices..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && send()}
            />
            <button className="chat-send-btn" onClick={() => send()}>➤</button>
          </div>
        </div>
      )}
      <button className="chat-fab" onClick={() => setOpen((o) => !o)} title="Travel Assistant">
        {open ? "✕" : "💬"}
      </button>
    </>
  );
}
