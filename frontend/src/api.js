const API_URL = import.meta.env.VITE_API_URL;

export async function fetchMessage() {
  const response = await fetch(`${API_URL}/api/message`);
  return response.json();
}
