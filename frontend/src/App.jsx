import { useState, useEffect, useRef } from 'react';
import { useChat } from './hooks/useChat';
import { Send, Music, Sparkles, BrainCircuit, Plus, Trash2, MessageCircle, Loader2, Download, FileText, PanelLeftClose, PanelLeft } from 'lucide-react';
import maraudioLogo from './photo/maraudio.png';

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
    presupuestos,
    loadPresupuestos,
  } = useChat();

  const [input, setInput] = useState('');
  const [showPresupuestos, setShowPresupuestos] = useState(false);
  const [showSidebar, setShowSidebar] = useState(true);
  const [justSentMessage, setJustSentMessage] = useState(false);
  const chatEndRef = useRef(null);

  useEffect(() => {
    loadConversations();
    loadPresupuestos();
  }, [loadConversations, loadPresupuestos]);

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

  const formatMarkdown = (text) => {
    return text
      .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.+?)\*/g, '<em>$1</em>')
      .replace(/`(.+?)`/g, '<code class="bg-neutral-800 px-1 rounded">$1</code>')
      .replace(/\n/g, '<br />');
  };

  return (
    <div className="min-h-screen bg-neutral-950 text-slate-100 font-sans selection:bg-purple-500/30 flex">
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-[10%] -left-[10%] w-[40%] h-[40%] bg-purple-900/20 blur-[120px] rounded-full"></div>
        <div className="absolute -bottom-[10%] -right-[10%] w-[40%] h-[40%] bg-blue-900/20 blur-[120px] rounded-full"></div>
      </div>

      {showSidebar && (
        <aside className="w-72 border-r border-white/10 p-4 flex flex-col z-10 h-screen sticky top-0">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-sm font-bold uppercase tracking-widest text-slate-500">Conversaciones</h2>
            <button
              onClick={handleCreateConversation}
              className="p-2 bg-purple-600 hover:bg-purple-500 rounded-lg transition-colors"
            >
              <Plus size={18} className="text-white" />
            </button>
          </div>

          <div className="flex-1 overflow-y-auto space-y-2 custom-scrollbar">
            {loadingConversations ? (
              <div className="flex items-center justify-center py-8">
                <Loader2 className="animate-spin text-purple-500" size={24} />
              </div>
            ) : conversations.length === 0 ? (
              <p className="text-sm text-slate-600 text-center py-8">No hay conversaciones</p>
            ) : (
              conversations.map(conv => (
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
              ))
            )}
          </div>
        </aside>
      )}

      <main className="flex-1 flex flex-col p-4 md:p-6 z-10 min-w-0 h-screen shrink-0">
        <header className="flex items-center justify-between mb-6 border-b border-white/10 pb-4 shrink-0">
          <div className="flex items-center gap-3">
            <button
              onClick={() => setShowSidebar(!showSidebar)}
              className="p-2 hover:bg-white/5 rounded-lg transition-colors"
            >
              {showSidebar ? <PanelLeftClose size={20} className="text-slate-400" /> : <PanelLeft size={20} className="text-slate-400" />}
            </button>
            <div className="rounded-full overflow-hidden border-2 border-purple-500/30">
              <img src={maraudioLogo} alt="Maraudio" className="w-10 h-10 object-contain" />
            </div>
            <div>
              <h1 className="text-xl font-black tracking-tighter uppercase text-purple-300">Mar<span className="text-sky-200">audio</span></h1>
              <p className="text-[10px] text-slate-500 uppercase tracking-[0.2em]">Soporte Tecnico</p>
            </div>
          </div>
          <div className="flex items-center gap-4">
            <button
              onClick={() => setShowPresupuestos(!showPresupuestos)}
              className="flex items-center gap-2 px-3 py-2 bg-purple-600/20 hover:bg-purple-600/30 border border-purple-500/30 rounded-lg transition-colors"
            >
              <FileText size={18} className="text-purple-400" />
              <span className="text-sm text-purple-400">Presupuestos</span>
              {presupuestos.length > 0 && (
                <span className="bg-purple-500 text-white text-xs px-2 py-0.5 rounded-full">{presupuestos.length}</span>
              )}
            </button>
            <span className="text-[10px] font-mono text-purple-400 bg-purple-400/10 px-2 py-1 rounded hidden md:block">SYSTEM ONLINE</span>
          </div>
        </header>

        {showPresupuestos && (
          <div className="mb-4 bg-white/5 border border-white/10 rounded-xl p-4">
            <h3 className="text-sm font-bold text-purple-400 mb-3 flex items-center gap-2">
              <FileText size={16} />
              PDFs Generados
            </h3>
            {presupuestos.length === 0 ? (
              <p className="text-sm text-slate-500">No hay presupuestos generados</p>
            ) : (
              <div className="space-y-2">
                {presupuestos.map((p, i) => (
                  <div key={i} className="flex items-center justify-between bg-white/5 p-3 rounded-lg">
                    <div>
                      <p className="text-sm text-slate-200">{p.name}</p>
                      <p className="text-xs text-slate-500">{(p.size / 1024).toFixed(1)} KB</p>
                    </div>
                    <a
                      href={`http://localhost:8000/presupuestos/${p.name}`}
                      download
                      className="flex items-center gap-2 px-3 py-1.5 bg-purple-600 hover:bg-purple-500 rounded-lg transition-colors"
                    >
                      <Download size={14} className="text-white" />
                      <span className="text-sm text-white">Descargar</span>
                    </a>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        <div className="flex-1 overflow-y-auto space-y-4 custom-scrollbar pb-4 min-h-0 scrollbar-hide">
          {!currentThreadId && messages.length === 0 && !loading && (
            <div className="flex flex-col items-center justify-center h-full text-center opacity-40">
              <Music size={48} className="mb-4" />
              <p className="text-lg italic">¿En que puedo ayudarte con tu evento hoy?</p>
              <p className="text-sm">Configuracion de PA, iluminacion DMX o Rider Tecnico</p>
            </div>
          )}

          {messages.map((msg, i) => (
            <div key={i}>
              {msg.reasoning && (
                <div className="bg-neutral-900/50 border-l-2 border-amber-500/50 p-3 rounded-r-lg mb-2 max-w-xl">
                  <div className="flex items-center gap-2 mb-1 text-amber-500">
                    <BrainCircuit size={14} />
                    <span className="text-xs font-bold uppercase tracking-widest">Procesando</span>
                  </div>
                  <p className="text-xs text-slate-400 italic font-mono leading-relaxed">
                    {msg.reasoning}
                  </p>
                </div>
              )}

{msg.type === 'user' || msg.type === 'HumanMessage' ? (
                <div className="max-w-xl ml-auto">
                  <div className="bg-blue-600/30 p-4 rounded-full px-10">
                    <p className="text-lg text-slate-200">{msg.content}</p>
                  </div>
                </div>
              ) : (
                <div className="max-w-2xl">
                  <div className="flex items-center gap-2 mb-2 text-purple-400">
                    <Sparkles size={16} />
                    <span className="text-xs font-bold uppercase tracking-[0.3em]">MARAUDIO</span>
                  </div>
                  <div
                    className="text-slate-300 leading-relaxed text-lg"
                    dangerouslySetInnerHTML={{ __html: formatMarkdown(msg.content) }}
                  />
                  {msg.pdfFile && (
                    <div className="mt-3 flex items-center gap-3 bg-purple-600/10 border border-purple-500/30 p-3 rounded-xl inline-flex">
                      <FileText size={20} className="text-purple-400" />
                      <span className="text-sm text-slate-200">{msg.pdfFile}</span>
                      <a
                        href={`http://localhost:8000/presupuestos/${msg.pdfFile}`}
                        download
                        className="flex items-center gap-1.5 px-3 py-1.5 bg-purple-600 hover:bg-purple-500 rounded-lg transition-colors ml-2"
                      >
                        <Download size={14} className="text-white" />
                        <span className="text-sm text-white">Descargar</span>
                      </a>
                    </div>
                  )}
                </div>
              )}
            </div>
          ))}

          {loading && (
            <div className="flex items-center gap-2 text-purple-500 animate-pulse">
              <div className="w-2 h-2 bg-current rounded-full"></div>
              <div className="w-2 h-2 bg-current rounded-full delay-75"></div>
              <div className="w-2 h-2 bg-current rounded-full delay-150"></div>
            </div>
          )}

          <div ref={chatEndRef} />
        </div>

        <footer className="mt-4 pt-4 border-t border-white/10 shrink-0">
          <div className="relative group max-w-3xl mx-auto">
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSend()}
              placeholder="Escribe tu consulta..."
              className="w-full bg-neutral-900 border border-white/10 rounded-full py-4 px-6 pr-14 focus:outline-none focus:ring-2 focus:ring-purple-600/50 focus:border-purple-500 transition-all placeholder:text-slate-600 text-slate-200 text-base"
            />
            <button
              onClick={handleSend}
              disabled={loading}
              className="absolute right-2 top-1/2 -translate-y-1/2 p-2.5 bg-purple-600 hover:bg-purple-500 rounded-full transition-colors disabled:opacity-50"
            >
              <Send size={18} className="text-white" />
            </button>
          </div>
          <p className="text-[10px] text-center mt-3 text-slate-600 uppercase tracking-tighter">
            Powered by SoundEngineering AI
          </p>
        </footer>
      </main>
    </div>
  );
}

export default App;