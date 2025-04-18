"use client"
import React from "react"
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
  const [queryType, setQueryType] = useState<"general" | "search" | "summarize">("general"); // Track query type

  const handleSend = async () => {
    if (!input.trim()) return;

    // Add user message
    setMessages((prev) => [...prev, { role: "user", content: input }]);

    // Clear the input box and set loading state
    setInput("");
    setLoading(true);

    try {
      // Validation for "summarize" query type
      if (queryType === "summarize") {
        // Check if the input is an absolute path
        const isAbsolutePath = input.startsWith("/") || /^[a-zA-Z]:\\/.test(input); // Unix or Windows absolute path
        if (!isAbsolutePath) {
          setMessages((prev) => [
            ...prev,
            { role: "assistant", content: "The provided path is not an absolute path. Please enter a valid absolute path." },
          ]);
          setLoading(false);
          return; // Stop execution here
        }

        // Check if the path exists on the file system
        const pathExists = await fetch(`/api/check-path`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ path: input }),
        }).then((res) => res.json());

        if (!pathExists.exists) {
          setMessages((prev) => [
            ...prev,
            { role: "assistant", content: "The provided path does not exist on the file system. Please enter a valid path." },
          ]);
          setLoading(false);
          return; // Stop execution here
        }
      }

      // Send the query to the model
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
      const aiResponse = data.response || "Sorry, I couldn't process your request.";

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
    <div className="w-80 border-l bg-background flex flex-col h-full">
      <Card className="h-full rounded-none border-0 flex flex-col">
        {/* Header */}
        <CardHeader className="flex flex-col space-y-2 px-4 py-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Bot className="h-5 w-5 text-primary" />
              <CardTitle className="text-base">AI Assistant</CardTitle>
            </div>
            <Button variant="ghost" size="icon" onClick={onClose}>
              <X className="h-4 w-4" />
            </Button>
          </div>

          {/* Query Type Buttons */}
          <div className="flex flex-col gap-2 px-2 py-2">
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
        </CardHeader>

        {/* Chat Content */}
        <CardContent className="flex-1 p-0 overflow-hidden">
          <ScrollArea className="h-full">
            <div className="flex flex-col gap-3 p-4">
              {messages.map((message, index) => (
                <div key={index} className={`flex ${message.role === "assistant" ? "justify-start" : "justify-end"}`}>
                  <div
                    className={`rounded-lg px-3 py-2 text-sm ${
                      message.role === "assistant" ? "bg-muted text-foreground" : "bg-primary text-primary-foreground"
                    } max-w-[90%]`}
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
                <Input
                  placeholder="Search for a file..."
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
          </div>
        </CardFooter>
      </Card>
    </div>
  );
}