import remarkGfm from "remark-gfm";
import remarkBreaks from "remark-breaks";
import { useState, useRef, useEffect } from "react";
import axios from "axios";
import Login from "./Login";
import ReactMarkdown from "react-markdown";
import { ErrorBoundary } from "react-error-boundary";
import Button from "./components/Button";

function App() {
  const [token, setToken] = useState("");
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState([]);
  const messagesEndRef = useRef(null);

  const askLLM = async () => {
    if (!input.trim()) return;
    const userMessage = { role: "user", text: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");

    const botMessage = { role: "bot", text: "" };
    const botIndex = messages.length + 1;
    setMessages((prev) => [...prev, botMessage]);

    try {
      const response = await fetch("http://localhost:8000/api/chat/", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ message: input }),
      });

      if (!response.ok || !response.body) {
        throw new Error("Streaming failed");
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder("utf-8");
      let partialText = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        const chunk = decoder.decode(value, { stream: true });
        partialText += chunk;

        setMessages((prev) => {
          const updated = [...prev];
          updated[botIndex] = { role: "bot", text: partialText };
          return updated;
        });
      }
    } catch (err) {
      alert("Error asking LLM: " + err.message);
    }
  };

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  if (!token) return <Login setToken={setToken} />;

  return (
    <ErrorBoundary
      fallback={
        <div className="text-red-600 p-4">
          Something went wrong while rendering markdown.
        </div>
      }
    >
      <div className="flex flex-col h-screen mx-auto w-4/5">
        <div className="flex-1 overflow-y-auto p-6 space-y-4 overflow-scroll">
          {messages.map((msg, index) => (
            <div
              key={index}
              className={`p-3 rounded-lg max-w-4/6 ${
                msg.role === "user"
                  ? "bg-blue-900 justify-self-end"
                  : "bg-stone-900 justify-self-start"
              }`}
            >
              <div>
                <ReactMarkdown
                  skipHtml={false}
                  unwrapDisallowed={true}
                  remarkPlugins={[remarkGfm, remarkBreaks]}
                  components={{
                    p: ({ node, ...props }) => (
                      <p
                        className="whitespace-pre-wrap"
                        style={{ whiteSpace: "pre-wrap" }}
                        {...props}
                      />
                    ),
                    code({ node, className, children, ...props }) {
                      const isInline =
                        !node?.position ||
                        node.position.start.line === node.position.end.line;

                      if (isInline) {
                        return (
                          <code
                            className="bg-gray-800 text-white px-1 py-0.5 rounded text-sm"
                            style={{ whiteSpace: "pre-wrap" }}
                            {...props}
                          >
                            {children}
                          </code>
                        );
                      }

                      return (
                        <pre
                          className="bg-gray-900 text-white p-3 rounded overflow-x-auto my-2"
                          style={{ whiteSpace: "pre-wrap" }}
                        >
                          <code className={className} {...props}>
                            {children}
                          </code>
                        </pre>
                      );
                    },
                    table: ({ children }) => (
                      <table className="table-auto border-collapse border border-gray-500">
                        {children}
                      </table>
                    ),
                    th: ({ children }) => (
                      <th className="border border-gray-500 px-2 py-1 font-bold">
                        {children}
                      </th>
                    ),
                    td: ({ children }) => (
                      <td className="border border-gray-500 px-2 py-1">
                        {children}
                      </td>
                    ),
                  }}
                >
                  {msg.text.replace(/\\n/g, "\n")}
                </ReactMarkdown>
              </div>
            </div>
          ))}
          <div ref={messagesEndRef} />
        </div>
        <div className="p-4 border-t flex justify-items-center">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type your message..."
            rows="2"
            className="flex-1 mr-2 p-2 border border-gray-300 rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-blue-500"
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                (async () => {
                  try {
                    await askLLM();
                  } catch (err) {
                    console.error("Failed to ask LLM:", err);
                  }
                })();
              }
            }}
          />
          <Button onClick={askLLM} disabled={input == ""} text="Send" />
        </div>
      </div>
    </ErrorBoundary>
  );
}

export default App;
