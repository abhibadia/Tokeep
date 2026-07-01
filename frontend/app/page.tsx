import { Show, SignInButton, SignUpButton, UserButton } from "@clerk/nextjs";

export default function Home() {
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
      </Show>
    </main>
  );
}