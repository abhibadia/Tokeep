"use client";

import { Show, SignInButton, SignUpButton, UserButton, useUser } from "@clerk/nextjs";
import { useState } from "react";

export default function Home() {
  const { user } = useUser();
  const [session, setSession] = useState<any>(null);

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
  }

  return (
    <main>
      <Show when="signed-out">
        <h1>Welcome to Tokeep</h1>
        <SignInButton />
        <SignUpButton />
      </Show>

      <Show when="signed-in">
        <UserButton />
        <h1>Tokeep Dashboard</h1>
        <p>You are logged in.</p>

        <button onClick={createSession}>Create Session</button>

        {session && (
          <pre>{JSON.stringify(session, null, 2)}</pre>
        )}
      </Show>
    </main>
  );
}