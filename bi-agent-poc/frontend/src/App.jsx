import React, { useState } from "react";

function App() {
  const [query, setQuery] = useState("");
  const [answer, setAnswer] = useState("");
  const [file, setFile] = useState(null);

  const handleQuery = async () => {
    const response = await fetch("/query", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query }),
    });
    const data = await response.json();
    setAnswer(data.answer || data.message);
  };

 

  return (
    <div style={{ padding: "20px" }}>
      <h1>Agentic Query App</h1>
      <div>
        <input
          type="text"
          placeholder="Ask your question..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
        <button onClick={handleQuery}>Submit Query</button>
      </div>
      <p>Answer: {answer}</p>
    
    </div>
  );
}

export default App;