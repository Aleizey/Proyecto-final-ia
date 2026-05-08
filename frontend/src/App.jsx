import { useState, useEffect, useRef } from 'react';
import { useChat } from './hooks/useChat';
import { Send, Music, Sparkles, BrainCircuit, Plus, Trash2, MessageCircle, Loader2 } from 'lucide-react';

function App() {
  const {
    conversations,
    currentThreadId,
    messages,
    loading,
    loadingConversations,
    loadConversations,
    loadConversationHistory,
    createConversation,
    deleteConversation,
    sendMessage,
    selectConversation,
  } = useChat();

  const [input, setInput] = useState('');
  const [justSentMessage, setJustSentMessage] = useState(false);
  const chatEndRef = useRef(null);

  useEffect(() => {
    loadConversations();
  }, [loadConversations]);

  useEffect(() => {
    if (currentThreadId && !justSentMessage) {
      loadConversationHistory(currentThreadId);
    }
  }, [currentThreadId, loadConversationHistory, justSentMessage]);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim()) return;
    const userMessage = input;
    setInput('');
    setJustSentMessage(true);
    await sendMessage(userMessage, currentThreadId);
    setJustSentMessage(false);
  };

  const handleCreateConversation = async () => {
    await createConversation();
  };

  const handleDeleteConversation = async (threadId, e) => {
    e.stopPropagation();
    await deleteConversation(threadId);
  };

  const handleSelectConversation = (threadId) => {
    selectConversation(threadId);
  };

  return (
    <div className="min-h-screen bg-neutral-950 text-slate-100 font-sans selection:bg-purple-500/30 flex">
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-[10%] -left-[10%] w-[40%] h-[40%] bg-purple-900/20 blur-[120px] rounded-full"></div>
        <div className="absolute -bottom-[10%] -right-[10%] w-[40%] h-[40%] bg-blue-900/20 blur-[120px] rounded-full"></div>
      </div>

      <aside className="w-80 border-r border-white/10 p-4 flex flex-col z-10">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-sm font-bold uppercase tracking-widest text-slate-500">Conversaciones</h2>
          <button
            onClick={handleCreateConversation}
            className="p-2 bg-purple-600 hover:bg-purple-500 rounded-lg transition-colors"
          >
            <Plus size={18} className="text-white" />
          </button>
        </div>

        {loadingConversations ? (
          <div className="flex items-center justify-center py-8">
            <Loader2 className="animate-spin text-purple-500" size={24} />
          </div>
        ) : conversations.length === 0 ? (
          <p className="text-sm text-slate-600 text-center py-8">No hay conversaciones</p>
        ) : (
          <div className="flex-1 overflow-y-auto space-y-2">
            {conversations.map(conv => (
              <div
                key={conv.thread_id}
                onClick={() => handleSelectConversation(conv.thread_id)}
                className={`p-3 rounded-lg cursor-pointer transition-colors group ${currentThreadId === conv.thread_id
                  ? 'bg-purple-600/20 border border-purple-500/30'
                  : 'hover:bg-white/5 border border-transparent'
                  }`}
              >
                <div className="flex items-center justify-between">
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium truncate">{conv.title}</p>
                    <p className="text-xs text-slate-500 truncate">{conv.preview}</p>
                  </div>
                  <button
                    onClick={(e) => handleDeleteConversation(conv.thread_id, e)}
                    className="p-1 text-slate-600 hover:text-red-500 opacity-0 group-hover:opacity-100 transition-all"
                  >
                    <Trash2 size={14} />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </aside>

      <main className="flex-1 flex flex-col max-w-4xl mx-auto p-4 md:p-8 z-10">
        <header className="flex items-center justify-between mb-8 border-b border-white/10 pb-4">
          <div className="flex items-center gap-3">
            <div className="bg-gradient-to-br from-purple-600 to-blue-600 p-2 rounded-lg shadow-lg shadow-purple-500/20">
              <MessageCircle size={24} className="text-white" />
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

        <div className="flex-1 overflow-y-hidden space-y-6 pr-2 custom-scrollbar">
          {!currentThreadId && messages.length === 0 && !loading && (
            <div className="flex flex-col items-center justify-center h-full text-center opacity-40">
              <Music size={48} className="mb-4" />
              <p className="text-lg italic">¿En qué puedo ayudarte con tu evento hoy?</p>
              <p className="text-sm">Configuración de PA, iluminación DMX o Rider Técnico</p>
            </div>
          )}

          {messages.map((msg, i) => (
            <div key={i}>
              {msg.reasoning && (
                <div className="bg-neutral-900/50 border-l-2 border-amber-500/50 p-4 rounded-r-xl mb-2">
                  <div className="flex items-center gap-2 mb-2 text-amber-500">
                    <BrainCircuit size={16} />
                    <span className="text-xs font-bold uppercase tracking-widest">Procesando</span>
                  </div>
                  <p className="text-sm text-slate-400 italic font-mono leading-relaxed">
                    {msg.reasoning}
                  </p>
                </div>
              )}

              {msg.type === 'user' ? (
                <div className="bg-blue-900/20 border border-blue-500/30 p-4 rounded-2xl">
                  <p className="text-sm text-blue-300 font-medium mb-1">Tú</p>
                  <p className="text-slate-200">{msg.content}</p>
                </div>
              ) : (
                <div className="bg-white/5 backdrop-blur-md border border-white/10 p-6 rounded-2xl shadow-2xl">
                  <div className="flex items-center gap-2 mb-4 text-purple-400">
                    <Sparkles size={18} />
                    <span className="text-xs font-bold uppercase tracking-[0.3em]">MARAUDIO</span>
                  </div>
                  <div className="prose prose-invert max-w-none text-slate-200 leading-7">
                    {msg.content}
                  </div>
                </div>
              )}
            </div>
          ))}

          {loading && (
            <div className="flex items-center gap-2 text-purple-500 animate-pulse px-4">
              <div className="w-2 h-2 bg-current rounded-full"></div>
              <div className="w-2 h-2 bg-current rounded-full delay-75"></div>
              <div className="w-2 h-2 bg-current rounded-full delay-150"></div>
            </div>
          )}

          <div ref={chatEndRef} />
        </div>

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
      </main>
    </div>
  );
}

export default App;