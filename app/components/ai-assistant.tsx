"use client"
import React, { useRef, useEffect } from "react"
import { useState } from "react"
import { Bot, Send, X } from "lucide-react"
import { Button } from "./ui/button"
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "./ui/card"
import { Input } from "./ui/input"
import { ScrollArea } from "./ui/scroll-area"

interface AIAssistantProps {
  onClose: () => void;
  currentPath: string;
  selectedFiles: string[];
}

export function AIAssistant({ onClose, currentPath, selectedFiles }: AIAssistantProps) {
  const [messages, setMessages] = useState([
    {
      role: "assistant",
      content: "Hello! I'm your AI file assistant. How can I help you today?",
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [queryType, setQueryType] = useState<"general" | "search" | "summarize">("general");
  const [searchDirectory, setSearchDirectory] = useState("");

  const chatContainerRef = useRef<HTMLDivElement>(null); // Reference for the chat container

  // Scroll to the bottom whenever messages change
  useEffect(() => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
    }
  }, [messages, loading]);

  const handleSend = async () => {
    if (!input.trim()) return;

    // Add user message
    setMessages((prev) => [...prev, { role: "user", content: input }]);

    // Clear the input box and set loading state
    setInput("");
    setLoading(true);

    try {
      // Handle "summarize" query type
      if (queryType === "summarize") {
        const responseSummarize = await fetch("http://localhost:8321/summarize-document", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            filepath: input,
            max_length: 500, // Optional: Adjust as needed
            overlap: 100,    // Optional: Adjust as needed
          }),
        });

        if (!responseSummarize.ok) {
          throw new Error(`Failed to fetch summary: ${responseSummarize.status} - ${responseSummarize.statusText}`);
        }

        const dataSummarize = await responseSummarize.json();

        if (dataSummarize.error) {
          throw new Error(dataSummarize.error);
        }

        const summary = dataSummarize.summary || "No summary available.";

        // Add assistant's response
        setMessages((prev) => [...prev, { role: "assistant", content: summary }]);
        return; // Stop further execution for summarize
      }

      // Handle "search" query type
      if (queryType === "search") {
        const responseSearch = await fetch("http://localhost:8321/search-files", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            query: input, // The search query entered by the user
            start_dir: searchDirectory || "/", // The directory to start the search from, defaults to root
          }),
        });

        if (!responseSearch.ok) {
          throw new Error(`Failed to search files: ${responseSearch.status} - ${responseSearch.statusText}`);
        }

        const dataSearch = await responseSearch.json();

        if (dataSearch.error) {
          throw new Error(dataSearch.error);
        }

        // Extract the top match and other details
        const topMatch = dataSearch.top_match || {};
        const faissTopFiles = dataSearch.faiss_top_files || [];
        const ollamaResponse = dataSearch.ollama_response || {};

        // Format the response for the assistant
        const searchResultMessage = `
          **Top Match**:
          - File Path: ${topMatch.file_path || "N/A"}
          - Confidence: ${topMatch.confidence || "N/A"}
          - Context: ${topMatch.context || "N/A"}

          **Other Matches**:
          ${faissTopFiles.length > 0 ? faissTopFiles.join("\n") : "No other matches found."}
        `;

        // Add assistant's response
        setMessages((prev) => [...prev, { role: "assistant", content: searchResultMessage }]);
        return; // Stop further execution for search
      }

      // Default behavior for other query types
      const action = "generate"; // Default action for all query types
      const params = { prompt: input }; // Default parameters

      const response = await fetch("http://localhost:8321/ai-assistant", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ action, params }),
      });

      if (!response.ok) {
        throw new Error(`Failed to fetch AI response: ${response.status} - ${response.statusText}`);
      }

      const data = await response.json();
      const aiResponse = data.ollama_response || "Sorry, I couldn't process your request.";

      // Add assistant's response
      setMessages((prev) => [...prev, { role: "assistant", content: aiResponse }]);
    } catch (error: any) {
      console.error("Error fetching AI response:", error);
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: `An error occurred: ${error.message}` },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="w-full sm:w-80 border-l bg-background flex flex-col h-full">
      <Card className="h-full rounded-none border-0 flex flex-col">
        {/* Header */}
        <CardHeader className="flex flex-col space-y-2 px-4 py-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Bot className="h-5 w-5 text-primary" />
              <div>
                <CardTitle className="text-lg font-semibold">AI Assistant</CardTitle>
                <p className="text-sm text-muted-foreground">Your intelligent file assistant</p>
              </div>
            </div>
            <Button variant="ghost" size="icon" onClick={onClose}>
              <X className="h-4 w-4" />
            </Button>
          </div>
        </CardHeader>

        {/* Query Type Buttons */}
        <div className="flex flex-col gap-4 px-4 py-3">
          <Button
            variant={queryType === "general" ? "secondary" : "ghost"}
            size="sm"
            className={`w-full text-center ${
              queryType === "general" ? "ring-2 ring-primary ring-offset-2" : ""
            }`}
            onClick={() => setQueryType("general")}
          >
            General Queries
          </Button>
          <Button
            variant={queryType === "search" ? "secondary" : "ghost"}
            size="sm"
            className={`w-full text-center ${
              queryType === "search" ? "ring-2 ring-primary ring-offset-2" : ""
            }`}
            onClick={() => setQueryType("search")}
          >
            Search for a File
          </Button>
          <Button
            variant={queryType === "summarize" ? "secondary" : "ghost"}
            size="sm"
            className={`w-full text-center ${
              queryType === "summarize" ? "ring-2 ring-primary ring-offset-2" : ""
            }`}
            onClick={() => setQueryType("summarize")}
          >
            File Summarization
          </Button>
        </div>

        {/* Chat Content */}
        <CardContent className="flex-1 p-0 overflow-hidden">
          <ScrollArea className="h-full" ref={chatContainerRef}>
            <div className="flex flex-col gap-3 p-4">
              {messages.map((message, index) => (
                <div key={index} className={`flex ${message.role === "assistant" ? "justify-start" : "justify-end"}`}>
                  <div
                    className={`rounded-lg px-3 py-2 text-sm shadow ${
                      message.role === "assistant" ? "bg-muted text-foreground" : "bg-primary text-primary-foreground"
                    } max-w-[90%] break-words`}
                  >
                    {message.content}
                  </div>
                </div>
              ))}
              {loading && (
                <div className="flex justify-start">
                  <div className="rounded-lg px-3 py-2 text-sm bg-muted text-foreground max-w-[90%] flex items-center gap-2">
                    <div className="animate-spin h-4 w-4 border-2 border-primary border-t-transparent rounded-full"></div>
                    Reasoning...
                  </div>
                </div>
              )}
            </div>
          </ScrollArea>
        </CardContent>

        {/* Input Box */}
        <CardFooter className="p-3">
          <div className="flex w-full items-center gap-2">
            {queryType === "general" && (
              <>
                <Input
                  placeholder="Ask a question..."
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && handleSend()}
                  className="flex-1"
                  disabled={loading}
                />
                <Button size="icon" onClick={handleSend} disabled={loading}>
                  <Send className="h-4 w-4" />
                </Button>
              </>
            )}

            {queryType === "summarize" && (
              <>
                <Input
                  placeholder="Enter an absolute file path..."
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && handleSend()}
                  className="flex-1"
                  disabled={loading}
                />
                <Button size="icon" onClick={handleSend} disabled={loading}>
                  <Send className="h-4 w-4" />
                </Button>
              </>
            )}

            {queryType === "search" && (
              <>
                <div className="flex flex-col gap-2 w-full">
                  <label className="text-sm text-muted-foreground">Directory (Optional)</label>
                  <Input
                    placeholder="Enter directory to search..."
                    value={searchDirectory}
                    onChange={(e) => setSearchDirectory(e.target.value)}
                    className="flex-1"
                    disabled={loading}
                    title="Optional: Specify a directory to narrow your search."
                  />
                  <label className="text-sm text-muted-foreground">Search Query</label>
                  <Input
                    placeholder="Enter search query..."
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyDown={(e) => e.key === "Enter" && handleSend()}
                    className="flex-1"
                    disabled={loading}
                    title="Enter the file name or keywords to search."
                  />
                </div>
                <Button size="icon" onClick={handleSend} disabled={loading}>
                  <Send className="h-4 w-4" />
                </Button>
              </>
            )}
          </div>
        </CardFooter>
      </Card>
    </div>
  );
}