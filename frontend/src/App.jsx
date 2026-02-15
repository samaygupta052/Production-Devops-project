import { useEffect, useState } from "react";
import { fetchMessage } from "./api";

function App() {
  const [message, setMessage] = useState("");

  useEffect(() => {
    fetchMessage()
      .then(data => setMessage(data.message))
      .catch(err => console.error("API Error:", err));
  }, []);

  return (
    <div style={{ padding: "40px", fontFamily: "Arial" }}>
      <h1>DevOps Practice Project</h1>
      <p>{message}</p>
    </div>
  );
}

export default App;
