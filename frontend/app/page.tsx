"use client";

import { Show, SignInButton, SignUpButton, UserButton, useUser } from "@clerk/nextjs";
import { useState } from "react";

export default function Home() {
  const { user } = useUser();

  const [session, setSession] = useState<any>(null);
  const [prompt, setPrompt] = useState("");
  const [messages, setMessages] = useState<any[]>([]);

  const [apiKey, setApiKey] = useState("");
  const [keyStatus, setKeyStatus] = useState("");

  async function createSession() {
    const res = await fetch("http://127.0.0.1:8000/sessions", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        user_id: user?.id,
        session_name: "My First Real Session",
        provider: "openai",
        model: "gpt-4.1-mini",
      }),
    });

    const data = await res.json();
    setSession(data);
    setMessages([]);
  }

  async function sendPrompt() {
    if (!session) {
      alert("Create a session first");
      return;
    }

    const res = await fetch("http://127.0.0.1:8000/chat", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        session_id: session.id,
        prompt: prompt,
      }),
    });

    const data = await res.json();

    if (!res.ok) {
      alert(data.detail || "Something went wrong");
      return;
    }

    setMessages((prev) => [...prev, data]);
    setPrompt("");
  }
  async function saveApiKey() {
    const res = await fetch("http://127.0.0.1:8000/api-keys", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        user_id: user?.id,
        provider: "openai",
        api_key: apiKey,
      }),
    });

    const data = await res.json();
    setKeyStatus(data.message);
    setApiKey("");
  }

  return (
    <main style={{ padding: "24px", maxWidth: "800px" }}>
      <Show when="signed-out">
        <h1>Welcome to Tokeep</h1>
        <SignInButton />
        <SignUpButton />
      </Show>

      <Show when="signed-in">
        <UserButton />

        <h1>Tokeep Dashboard</h1>
        <p>You are logged in.</p>
        <h2>Connect OpenAI</h2>

        <input
          type="password"
          value={apiKey}
          onChange={(e) => setApiKey(e.target.value)}
          placeholder="Paste your OpenAI API key"
          style={{ width: "100%", padding: "8px" }}
        />

        <button onClick={saveApiKey} style={{ marginTop: "8px" }}>
          Save API Key
        </button>

        {keyStatus && <p>{keyStatus}</p>}

        <button onClick={createSession}>Create Session</button>

        {session && (
          <div>
            <h2>Current Session</h2>
            <p><b>Session ID:</b> {session.id}</p>
            <p><b>Model:</b> {session.model}</p>
            <p><b>Total Tokens:</b> {session.total_tokens}</p>
            <p><b>Total Cost:</b> ${session.total_cost}</p>

            <textarea
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="Type your prompt here..."
              rows={4}
              style={{ width: "100%", marginTop: "16px" }}
            />

            <br />

            <button onClick={sendPrompt} style={{ marginTop: "8px" }}>
              Send Prompt
            </button>
          </div>
        )}

        <hr />

        <h2>Messages</h2>

        {messages.map((message, index) => (
          <div key={index} style={{ marginBottom: "20px" }}>
            <p><b>Prompt:</b> {message.prompt}</p>
            <p><b>Response:</b> {message.response}</p>
            <p><b>Input Tokens:</b> {message.input_tokens}</p>
            <p><b>Output Tokens:</b> {message.output_tokens}</p>
            <p><b>Total Tokens:</b> {message.total_tokens}</p>
            <p><b>Cost:</b> ${message.cost}</p>
          </div>
        ))}
      </Show>
    </main>
  );
}