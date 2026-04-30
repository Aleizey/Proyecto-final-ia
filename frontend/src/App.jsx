import { useState } from 'react';
import { Send, Music, Speaker, Sparkles, BrainCircuit } from 'lucide-react'; // Instala lucide-react o usa SVGs

function App() {
  const [input, setInput] = useState('');
  const [chat, setChat] = useState({ message: '', reasoning: '' });
  const [loading, setLoading] = useState(false);

  const handleSend = async () => {
    if (!input) return;
    setLoading(true);
    // Tu lógica de fetch se mantiene igual...
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
        } catch (e) { console.error(e); }
      }
    }
    setLoading(false);
  };

  return (
    <div className="min-h-screen bg-neutral-950 text-slate-100 font-sans selection:bg-purple-500/30">
      {/* BACKGROUND DECORATION */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-[10%] -left-[10%] w-[40%] h-[40%] bg-purple-900/20 blur-[120px] rounded-full"></div>
        <div className="absolute -bottom-[10%] -right-[10%] w-[40%] h-[40%] bg-blue-900/20 blur-[120px] rounded-full"></div>
      </div>

      <div className="relative z-10 max-w-4xl mx-auto p-4 md:p-8 flex flex-col h-screen">

        {/* HEADER AREA */}
        <header className="flex items-center justify-between mb-8 border-b border-white/10 pb-4">
          <div className="flex items-center gap-3">
            <div className="bg-gradient-to-br from-purple-600 to-blue-600 p-2 rounded-lg shadow-lg shadow-purple-500/20">
              <Speaker size={24} className="text-white" />
            </div>
            <div>
              <h1 className="text-xl font-black tracking-tighter uppercase">Mar<span className="text-purple-500">audio</span></h1>
              <p className="text-[10px] text-slate-500 uppercase tracking-[0.2em]">Soporte Técnico</p>
            </div>
          </div>
          <div className="hidden md:block text-right">
            <span className="text-[10px] font-mono text-purple-400 bg-purple-400/10 px-2 py-1 rounded">SYSTEM ONLINE</span>
          </div>
        </header>

        {/* CHAT AREA */}
        <main className="flex-1 overflow-y-auto space-y-6 pr-2 custom-scrollbar">
          {!chat.message && !loading && (
            <div className="flex flex-col items-center justify-center h-full text-center opacity-40">
              <Music size={48} className="mb-4" />
              <p className="text-lg italic">¿En qué puedo ayudarte con tu evento hoy?</p>
              <p className="text-sm">Configuración de PA, iluminación DMX o Rider Técnico</p>
            </div>
          )}

          {/* REASONING BLOCK (Estilo "Caja de Herramientas") */}
          {chat.reasoning && (
            <div className="bg-neutral-900/50 border-l-2 border-amber-500/50 p-4 rounded-r-xl">
              <div className="flex items-center gap-2 mb-2 text-amber-500">
                <BrainCircuit size={16} />
                <span className="text-xs font-bold uppercase tracking-widest">Procesando Configuración</span>
              </div>
              <p className="text-sm text-slate-400 italic font-mono leading-relaxed">
                {chat.reasoning}
              </p>
            </div>
          )}

          {/* RESPONSE BLOCK */}
          {chat.message && (
            <div className="bg-white/5 backdrop-blur-md border border-white/10 p-6 rounded-2xl shadow-2xl animate-in fade-in slide-in-from-bottom-4 duration-500">
              <div className="flex items-center gap-2 mb-4 text-purple-400">
                <Sparkles size={18} />
                <span className="text-xs font-bold uppercase tracking-[0.3em]">MARAUDIO</span>
              </div>
              <div className="prose prose-invert max-w-none text-slate-200 leading-7">
                {chat.message}
              </div>
            </div>
          )}

          {loading && (
            <div className="flex items-center gap-2 text-purple-500 animate-pulse px-4">
              <div className="w-2 h-2 bg-current rounded-full"></div>
              <div className="w-2 h-2 bg-current rounded-full delay-75"></div>
              <div className="w-2 h-2 bg-current rounded-full delay-150"></div>
            </div>
          )}
        </main>

        {/* INPUT AREA */}
        <footer className="mt-6">
          <div className="relative group">
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSend()}
              placeholder="Escribe tu consulta técnica o idea para el evento..."
              className="w-full bg-neutral-900 border border-white/10 rounded-2xl py-4 pl-6 pr-14 focus:outline-none focus:ring-2 focus:ring-purple-600/50 focus:border-purple-500 transition-all placeholder:text-slate-600 text-slate-200"
            />
            <button
              onClick={handleSend}
              disabled={loading}
              className="absolute right-2 top-1/2 -translate-y-1/2 p-3 bg-purple-600 hover:bg-purple-500 rounded-xl transition-colors disabled:opacity-50"
            >
              <Send size={20} className="text-white" />
            </button>
          </div>
          <p className="text-[10px] text-center mt-4 text-slate-600 uppercase tracking-tighter">
            Powered by SoundEngineering AI v3.5 — 2026 High Fidelity Standard
          </p>
        </footer>
      </div>
    </div>
  );
}

export default App;