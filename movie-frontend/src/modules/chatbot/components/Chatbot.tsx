import { useEffect, useRef, useState } from "react";
import { sendMessage } from "../service/ChatBotService";
import type { MovieThumbnailGetVm } from "../../movie/model/MovieThumbnailGetVm";
import { MovieCard } from "./MovieCard";
import { Bot, MessageCircle, Send, Sparkles, X } from "lucide-react";

export default function Chatbot() {
    const [isOpen, setIsOpen] = useState(false);
    const [messages, setMessages] = useState([
        { id: 1, role: 'bot', text: 'Chào bạn! Hôm nay bạn muốn tìm cảm giác mạnh hay một chút lãng mạn? Hãy nói cho mình gu phim của bạn nhé!', movies: [] as MovieThumbnailGetVm[] },
    ]);
    const [input, setInput] = useState("");
    const [isTyping, setIsTyping] = useState(false);
    const scrollRef = useRef<HTMLDivElement>(null);
    const accumulatedTextRef = useRef("");
    const currentMoviesRef = useRef<MovieThumbnailGetVm[]>([]);
    const lastUpdateRef = useRef(0);

    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
    }, [messages])

    const handleSend = async () => {
        if (!input.trim()) return;

        const userMsg = { id: Date.now(), role: 'user', text: input, movies: [] as MovieThumbnailGetVm[] };
        setMessages(prev => [...prev, userMsg]);
        const currentInput = { message: input, userId: 123 };
        setInput("");
        setIsTyping(true);

        const botMsgId = Date.now() + 1;
        setMessages(prev => [...prev, { id: botMsgId, role: 'bot', text: "", movies: [] as MovieThumbnailGetVm[] }]);

        try {
            const response = await sendMessage(currentInput)

            if (!response.ok) throw new Error("Network response was not ok");
            if (!response.body) throw new Error("ReadableStream not supported");

            const reader = response.body.getReader();
            const decoder = new TextDecoder();

            while (true) {
                const { value, done } = await reader.read();
                console.log("Reader read - done:", done, "value:", value);

                if (value) {
                    const chunk = decoder.decode(value, { stream: true });
                    console.log("Dữ liệu thô nhận được:", chunk);
                }
                if (done) {
                    console.log("Stream finished");
                    break;
                }

                const chunk = decoder.decode(value, { stream: true });
                const lines = chunk.split("\n");

                for (const line of lines) {
                    let textToParse = line.trim();

                    if (textToParse.startsWith("data:")) {
                        textToParse = textToParse.replace("data:", "").trim();
                    }

                    if (!textToParse) continue;

                    try {
                        const parsed = JSON.parse(textToParse);

                        let content = parsed.message || "";
                        if (content.includes("Trình bày:") || content.includes("Trả lời:")) {
                            const parts = content.split(/Trình bày:|Trả lời:/);
                            content = parts[parts.length - 1].trim();
                        }

                        accumulatedTextRef.current = content;
                        if (parsed.data) {
                            currentMoviesRef.current = parsed.data;
                        }

                        const now = Date.now();
                        if (now - lastUpdateRef.current > 80) {
                            updateUI(botMsgId);
                            lastUpdateRef.current = now;
                        }
                    } catch (e) {
                        console.error("Lỗi parse JSON tại dòng:", textToParse, e);
                    }
                }
                updateUI(botMsgId);
            }
        } catch (error) {
            console.error("Streaming error:", error);
        } finally {
            setIsTyping(false);
        }
    };

    const updateUI = (botMsgId: number) => {
        setMessages(prev => {
            const index = prev.findIndex(m => m.id === botMsgId);
            if (index === -1) return prev;

            const newMessages = [...prev];
            newMessages[index] = {
                ...newMessages[index],
                text: accumulatedTextRef.current,
                movies: currentMoviesRef.current
            };
            return newMessages;
        });
    };

    return (
        <div className="fixed bottom-6 right-6 z-[9999] font-sans antialiased">
            {/* Nút mở Chatbot */}
            {!isOpen && (
                <button
                    onClick={() => setIsOpen(true)}
                    className="group bg-[#E50914] text-white p-4 rounded-full shadow-[0_8px_30px_rgb(229,9,20,0.4)] hover:scale-110 transition-all duration-300 active:scale-90"
                >
                    <MessageCircle size={28} />
                    <span className="absolute right-full mr-4 top-1/2 -translate-y-1/2 bg-black/80 text-white text-xs px-3 py-1.5 rounded-md opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap border border-white/10">
                        Tìm phim nhanh cùng Trợ lý
                    </span>
                </button>
            )}

            {/* Cửa sổ Chat */}
            {isOpen && (
                <div className="w-[400px] h-[600px] bg-[#141414] border border-white/10 rounded-2xl shadow-[0_20px_50px_rgba(0,0,0,0.5)] flex flex-col overflow-hidden animate-in fade-in zoom-in-95 duration-300">

                    {/* Header */}
                    <div className="p-4 flex justify-between items-center bg-gradient-to-r from-[#1a1a1a] to-[#141414] border-b border-white/5">
                        <div className="flex items-center gap-3">
                            <div className="p-2 bg-red-600/20 rounded-lg">
                                <Bot size={20} className="text-red-600" />
                            </div>
                            <div>
                                <h2 className="text-white text-sm font-bold tracking-wide">Trợ lý Phim</h2>
                                <p className="text-[10px] text-green-500 font-medium flex items-center gap-1">
                                    <span className="w-1.5 h-1.5 bg-green-500 rounded-full animate-pulse"></span> Sẵn sàng gợi ý
                                </p>
                            </div>
                        </div>
                        <button onClick={() => setIsOpen(false)} className="text-zinc-500 hover:text-white transition">
                            <X size={20} />
                        </button>
                    </div>

                    {/* Chat Body */}
                    <div ref={scrollRef} className="flex-1 overflow-y-auto p-4 space-y-6 scrollbar-hide">
                        {messages.map((msg) => (
                            <div key={msg.id} className={`flex flex-col ${msg.role === 'user' ? 'items-end' : 'items-start'}`}>
                                <div className={`max-w-[85%] px-4 py-3 rounded-2xl text-[14px] leading-relaxed shadow-sm ${msg.role === 'user'
                                    ? 'bg-red-600 text-white rounded-tr-none'
                                    : 'bg-[#232323] text-zinc-100 rounded-tl-none border border-white/5'
                                    }`}>
                                    {msg.text || (msg.role === 'bot' && isTyping && "...")}
                                </div>

                                {/* Hiển thị Phim theo chiều ngang nếu có */}
                                {msg.movies && msg.movies.length > 0 && (
                                    <div className="w-full mt-3 overflow-x-auto flex gap-3 no-scrollbar pb-2">
                                        {msg.movies.map((movie) => (
                                            <div key={movie.id} className="min-w-[140px] max-w-[140px]">
                                                <MovieCard movie={movie} />
                                            </div>
                                        ))}
                                    </div>
                                )}
                            </div>
                        ))}

                        {isTyping && messages[messages.length - 1].role === 'user' && (
                            <div className="flex items-center gap-2 text-zinc-500 italic text-xs ml-2">
                                <Sparkles size={14} className="animate-spin-slow" />
                                Đang tìm những bộ phim hay nhất...
                            </div>
                        )}
                    </div>

                    {/* Footer / Input */}
                    <div className="p-4 bg-[#1a1a1a] border-t border-white/5">
                        <div className="flex gap-2 overflow-x-auto mb-3 no-scrollbar">
                            {['Phim hành động', 'Top phim bộ', 'Cực phẩm Netflix'].map((txt) => (
                                <button
                                    key={txt}
                                    onClick={() => { setInput(txt); }}
                                    className="whitespace-nowrap px-3 py-1.5 bg-zinc-800/50 hover:bg-zinc-700 border border-white/5 rounded-full text-[11px] text-zinc-300 transition"
                                >
                                    {txt}
                                </button>
                            ))}
                        </div>
                        <div className="relative">
                            <input
                                value={input}
                                onChange={(e) => setInput(e.target.value)}
                                onKeyDown={(e) => e.key === 'Enter' && handleSend()}
                                placeholder="Bạn đang tìm phim gì?"
                                className="w-full bg-[#232323] text-white text-sm rounded-xl pl-4 pr-12 py-3.5 focus:outline-none focus:ring-1 focus:ring-red-600 transition-all border border-transparent focus:border-red-600/50"
                            />
                            <button
                                onClick={handleSend}
                                className="absolute right-2 top-1/2 -translate-y-1/2 p-2 text-red-600 hover:text-red-500 transition disabled:opacity-30"
                                disabled={!input.trim() || isTyping}
                            >
                                <Send size={20} />
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}