import { useState } from 'react';

function App() {
  const [input, setInput] = useState('');
  const [chat, setChat] = useState({ message: '', reasoning: '' });

  const handleSend = async () => {
    const response = await fetch('http://localhost:8000/chat/stream', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: input }),
    });

    const reader = response.body.getReader();
    const decoder = new TextDecoder();

    while (true) {
      const { value, done } = await reader.read();
      if (done) break;

      const chunk = decoder.decode(value);
      const lines = chunk.split("\n").filter(line => line.trim());

      for (const line of lines) {
        try {
          const data = JSON.parse(line);
          setChat({
            message: data.content || '',
            reasoning: data.reasoning || ''
          });
        } catch (e) {
          console.error("Error parseando JSON del stream:", line);
        }
      }
    }
  };

  return (
    <div className="">
      <input value={input} onChange={(e) => setInput(e.target.value)} className="" />
      <button onClick={handleSend} className="">Preguntar</button>

      {chat.reasoning && (
        <div className="">
          <strong>Pensamiento de Gemma:</strong> {chat.reasoning}
        </div>
      )}

      <div className="">
        <strong>Respuesta:</strong> {chat.message}
      </div>
    </div>
  );
}

export default App