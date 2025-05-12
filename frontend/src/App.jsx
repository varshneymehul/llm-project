import remarkGfm from "remark-gfm";
import remarkBreaks from "remark-breaks";
import { useState, useRef, useEffect } from "react";
import axios from "axios";
import Login from "./Login";
import ReactMarkdown from "react-markdown";
import { ErrorBoundary } from "react-error-boundary";
import Button from "./components/Button";
import AuthenticatedImage from "./components/AuthenticatedImage"; // Import the new component

function App() {
  const [token, setToken] = useState("");
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState([]);
  const messagesEndRef = useRef(null);

  const [showGraphExplorer, setShowGraphExplorer] = useState(false);
  const [graphFolders, setGraphFolders] = useState([]);
  const [selectedFolder, setSelectedFolder] = useState(null);
  const [folderContent, setFolderContent] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

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

  useEffect(() => {
    if (showGraphExplorer) {
      fetchGraphFolders();
    }
  }, [showGraphExplorer]);

  useEffect(() => {
    if (selectedFolder) {
      fetchFolderContent(selectedFolder);
    }
  }, [selectedFolder]);

  const fetchGraphFolders = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await axios.get(
        "http://localhost:8000/api/graph-folders/",
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );
      setGraphFolders(response.data.folders.sort());
    } catch (err) {
      console.error("Failed to fetch graph folders:", err);
      setError(
        "Failed to load graph folders: " +
          (err.response?.data?.error || err.message)
      );
    } finally {
      setIsLoading(false);
    }
  };

  const fetchFolderContent = async (folderName) => {
    setIsLoading(true);
    setError(null);
    setFolderContent(null);
    try {
      const response = await axios.get(
        `http://localhost:8000/api/graph-folders/${folderName}/`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );
      console.log(response.data);
      setFolderContent(response.data);
    } catch (err) {
      console.error("Failed to fetch folder content:", err);
      setError(
        "Failed to load folder content: " +
          (err.response?.data?.error || err.message)
      );
    } finally {
      setIsLoading(false);
    }
  };

  if (!token) return <Login setToken={setToken} />;

  return (
    <div className="flex h-screen">
      <div className="w-32 bg-gray-800 flex flex-col p-2">
        <button
          className="bg-blue-600 hover:bg-blue-700 hover:cursor-pointer transition-all text-white p-2 rounded mb-2"
          onClick={() => setShowGraphExplorer(!showGraphExplorer)}
        >
          📂 Graphs
        </button>
      </div>

      {showGraphExplorer ? (
        <div className="flex-1 p-4 overflow-y-auto bg-gray-900 text-white">
          <h2 className="text-xl font-bold mb-4">Graph Explorer</h2>

          {error && (
            <div className="bg-red-800 text-white p-3 mb-4 rounded">
              {error}
            </div>
          )}

          {isLoading && !selectedFolder && (
            <div className="text-white font-bold">Loading folders...</div>
          )}

          {!selectedFolder && !isLoading && graphFolders.length === 0 && (
            <div className="text-gray-400">No graph folders found.</div>
          )}

          {!selectedFolder && !isLoading && graphFolders.length > 0 && (
            <>
              <div className="mb-4">
                Select a repository to view its graphs:
              </div>
              <ul className="text-white">
                {graphFolders.map((folder, idx) => (
                  <li
                    key={idx}
                    className="cursor-pointer hover:bg-gray-700 p-2 rounded mb-1"
                    onClick={() => setSelectedFolder(folder)}
                  >
                    {folder}
                  </li>
                ))}
              </ul>
            </>
          )}

          {selectedFolder && isLoading && (
            <div>
              <button
                className="text-blue-400 underline mb-4"
                onClick={() => setSelectedFolder(null)}
              >
                ← Back to folders
              </button>
              <div className="mt-4 text-white font-bold">
                Loading graphs for {selectedFolder}...
              </div>
            </div>
          )}

          {selectedFolder && !isLoading && folderContent && (
            <div>
              <button
                className="text-blue-400 underline mb-4"
                onClick={() => setSelectedFolder(null)}
              >
                ← Back to folders
              </button>

              <h3 className="text-xl font-bold mb-4">{selectedFolder}</h3>

              <div className="mb-4">
                {folderContent.fileImage && (
                  <div className="mb-8">
                    <h4 className="text-lg font-semibold mb-2">
                      File Structure
                    </h4>
                    {/* Use AuthenticatedImage instead of img */}
                    <AuthenticatedImage
                      src={`http://localhost:8000/api/graph-file/${selectedFolder}/${folderContent.fileImage}`}
                      alt="File Dependency"
                      className="border border-gray-700 rounded p-2 max-w-2/3"
                      token={token}
                    />
                  </div>
                )}

                {folderContent.functionalImage && (
                  <div className="mb-8">
                    <h4 className="text-lg font-semibold mb-2">
                      Function Calls
                    </h4>
                    {/* Use AuthenticatedImage instead of img */}
                    <AuthenticatedImage
                      src={`http://localhost:8000/api/graph-file/${selectedFolder}/${folderContent.functionalImage}`}
                      alt="Functional Dependency"
                      className="border border-gray-700 rounded p-2 max-w-2/3"
                      token={token}
                    />
                  </div>
                )}
              </div>

              {Object.keys(folderContent.dependencies || {}).length > 0 && (
                <div>
                  <h4 className="text-lg font-semibold mb-2">Dependencies</h4>
                  <pre className="bg-gray-800 text-white p-4 rounded text-sm overflow-x-auto">
                    {JSON.stringify(folderContent.dependencies, null, 2)}
                  </pre>
                </div>
              )}
            </div>
          )}
        </div>
      ) : (
        <ErrorBoundary
          fallback={
            <div className="text-red-600 p-4">
              Something went wrong while rendering markdown.
            </div>
          }
        >
          <div className="flex flex-col h-screen mx-auto w-4/5 overflow-x-hidden">
            <div className="flex-1 overflow-y-auto p-6 space-y-4 overflow-x-hidden overflow-scroll">
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
              <Button onClick={askLLM} disabled={input === ""} text="Send" />
            </div>
          </div>
        </ErrorBoundary>
      )}
    </div>
  );
}

export default App;
