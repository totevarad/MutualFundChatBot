export interface ChatResponse {
  answer: string;
  source_url: string;
  last_updated: string;
  is_refusal: boolean;
}

export async function sendMessage(query: string, userId: string): Promise<ChatResponse> {
  const res = await fetch("http://localhost:8000/api/v1/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query, user_id: userId }),
  });

  if (!res.ok) {
    throw new Error("Failed to communicate with API");
  }

  return res.json();
}

export async function clearMemory(userId: string): Promise<void> {
  await fetch(`http://localhost:8000/api/v1/memory/${userId}`, {
    method: "DELETE",
  });
}
