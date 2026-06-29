import { useEffect, useRef, useState } from "react";
import { sendMessage } from "../service/ChatBotService";
import type { MovieThumbnailGetVm } from "../../movie/model/MovieThumbnailGetVm";
import { MovieCard } from "./MovieCard";
import { Bot, MessageCircle, Send, Sparkles, X, Loader2, Target } from "lucide-react";
import ReactMarkdown from 'react-markdown';

export interface ChatbotMetadata {
    intent: string;
    model: string;
    timestamp: number;
}

export interface ChatbotResponse {
    status: 'success' | 'error';
    metadata: ChatbotMetadata;
    message: string;
    movies: any[];
    suggestions?: string[];
}

export interface ChatMessage {
    id: number;
    role: 'user' | 'bot';
    text: string;
    movies?: any[];
    metadata?: ChatbotMetadata;
    suggestions?: string[];
    status?: 'loading' | 'success' | 'error';
}

export default function Chatbot() {
    const [isOpen, setIsOpen] = useState(false);
    const [messages, setMessages] = useState<ChatMessage[]>([
        {
            id: 1,
            role: 'bot',
            text: 'Xin chào! Tôi là Trợ lý Phim thông minh. Bạn đang tìm kiếm thể loại phim nào hay cần tôi gợi ý gì không?',
            movies: [] as MovieThumbnailGetVm[],
            suggestions: ["Phim hành động mới", "Top phim bộ Hàn Quốc", "Gợi ý phim cho tôi"]
        },
    ]);
    const [input, setInput] = useState("");
    const [isLoading, setIsLoading] = useState(false);
    const scrollRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
    }, [messages]);

    const handleSend = async (overrideText?: string) => {
        const textToSend = overrideText || input;
        if (!textToSend.trim() || isLoading) return;

        const userMsg: ChatMessage = {
            id: Date.now(),
            role: 'user',
            text: textToSend,
            movies: [] as MovieThumbnailGetVm[]
        };

        setMessages(prev => [...prev, userMsg]);
        const currentInput = { message: textToSend };
        if (!overrideText) setInput("");
        setIsLoading(true);

        const botMsgId = Date.now() + 1;
        setMessages(prev => [...prev, {
            id: botMsgId,
            role: 'bot',
            text: "",
            movies: [] as MovieThumbnailGetVm[],
            status: 'loading'
        }]);

        try {
            const response = await sendMessage(currentInput);
            console.log("Chatbot - API response:", response);
            const parsed: ChatbotResponse = response;
            console.log("Chatbot - Received response:", parsed.message, parsed.movies, parsed.suggestions);
            let content = parsed.message || "";
            const suggestions = parsed.suggestions || [];

            if (content.includes("Trình bày:") || content.includes("Trả lời:")) {
                const parts = content.split(/Trình bày:|Trả lời:/);
                content = parts[parts.length - 1].trim();
            }

            setMessages(prev => {
                const index = prev.findIndex(m => m.id === botMsgId);
                if (index === -1) return prev;

                const newMessages = [...prev];

                let moviesData: any[] = [];
                if (Array.isArray(parsed.movies)) {
                    moviesData = parsed.movies; 
                } else {
                    moviesData = []; 
                }

                newMessages[index] = {
                    ...newMessages[index],
                    text: content,
                    movies: moviesData,
                    suggestions: suggestions,
                    metadata: parsed.metadata,
                    status: 'success'
                };
                return newMessages;
            });

        } catch (err: any) {
            console.error("Chatbot Error:", err);
            const errorMessage = "Xin lỗi, tôi gặp sự cố khi xử lý yêu cầu của bạn. Vui lòng thử lại sau.";

            setMessages(prev => prev.map(m =>
                m.id === botMsgId
                    ? { ...m, text: errorMessage, status: 'error' }
                    : m
            ));
        } finally {
            setIsLoading(false);
        }
    };

    const handleSuggestionClick = (suggestion: string) => {
        handleSend(suggestion);
    };

    const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    };

    return (
        <div className="fixed bottom-6 right-6 z-[9999] font-sans antialiased">
            {/* Toggle Button */}
            {!isOpen && (
                <button
                    onClick={() => setIsOpen(true)}
                    className="group relative bg-[#E50914] text-white p-4 rounded-full shadow-[0_8px_30px_rgb(229,9,20,0.4)] hover:scale-110 transition-all duration-300 active:scale-90 focus:outline-none"
                >
                    <MessageCircle size={28} />
                    <span className="absolute right-full mr-4 top-1/2 -translate-y-1/2 bg-black/80 text-white text-xs px-3 py-1.5 rounded-md opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap border border-white/10 pointer-events-none">
                        Trò chuyện với AI
                    </span>
                </button>
            )}

            {/* Chat Window */}
            {isOpen && (
                <div className="w-[400px] h-[600px] bg-[#141414] border border-white/10 rounded-2xl shadow-[0_20px_50px_rgba(0,0,0,0.5)] flex flex-col overflow-hidden animate-in fade-in zoom-in-95 duration-300">

                    {/* Header */}
                    <div className="p-4 flex justify-between items-center bg-gradient-to-r from-[#1a1a1a] to-[#141414] border-b border-white/5">
                        <div className="flex items-center gap-3">
                            <div className="p-2 bg-red-600/20 rounded-lg">
                                <Bot size={20} className="text-red-600" />
                            </div>
                            <div>
                                <h2 className="text-white text-sm font-bold tracking-wide">Trợ lý AI</h2>
                                <p className="text-[10px] text-green-500 font-medium flex items-center gap-1">
                                    <span className="w-1.5 h-1.5 bg-green-500 rounded-full animate-pulse"></span> Trực tuyến
                                </p>
                            </div>
                        </div>
                        <button onClick={() => setIsOpen(false)} className="text-zinc-500 hover:text-white transition">
                            <X size={20} />
                        </button>
                    </div>

                    {/* Chat Messages */}
                    <div ref={scrollRef} className="flex-1 overflow-y-auto p-4 space-y-6 scrollbar-hide bg-[#0f0f0f]/30">
                        {messages.map((msg) => (
                            <div key={msg.id} className={`flex flex-col ${msg.role === 'user' ? 'items-end' : 'items-start'}`}>
                                <div className={`max-w-[85%] px-4 py-3 rounded-2xl text-[14px] leading-relaxed shadow-sm ${msg.role === 'user'
                                    ? 'bg-red-600 text-white rounded-tr-none'
                                    : 'bg-[#232323] text-zinc-100 rounded-tl-none border border-white/5'
                                    }`}>
                                    {msg.status === 'loading' ? (
                                        <div className="flex items-center gap-2 py-1">
                                            <Loader2 className="animate-spin" size={16} />
                                            <span className="text-zinc-400 italic">Đang suy nghĩ...</span>
                                        </div>
                                    ) : (
                                        <div className="markdown-content">
                                            <ReactMarkdown>{msg.text}</ReactMarkdown>
                                        </div>
                                    )}

                                    {msg.metadata && msg.role === 'bot' && (
                                        <div className="mt-2 pt-2 border-t border-white/5 text-[10px] text-zinc-500 flex items-center gap-1.5 uppercase tracking-tighter">
                                            <Target size={10} />
                                            <span>Intent: {msg.metadata.intent}</span>
                                            <span className="mx-1">•</span>
                                            <span>Model: {msg.metadata.model}</span>
                                        </div>
                                    )}
                                </div>

                                {/* Suggestion Chips */}
                                {msg.suggestions && msg.suggestions.length > 0 && msg.role === 'bot' && msg.status !== 'loading' && (
                                    <div className="flex flex-wrap gap-2 mt-3 pl-1">
                                        {msg.suggestions.map((s, i) => (
                                            <button
                                                key={i}
                                                onClick={() => handleSuggestionClick(s)}
                                                className="px-3 py-1.5 bg-zinc-800/50 hover:bg-zinc-700 border border-white/5 rounded-full text-[11px] text-zinc-300 transition flex items-center gap-1"
                                            >
                                                <Sparkles size={10} className="text-yellow-500" />
                                                {s}
                                            </button>
                                        ))}
                                    </div>
                                )}

                                {/* Movie Cards Scroll */}
                                {msg.movies && msg.movies.length > 0 && (
                                    <div className="w-full mt-4 overflow-x-auto flex gap-3 no-scrollbar pb-2">
                                        {msg.movies.map((movie: any) => (
                                            <div key={movie.id} className="min-w-[150px] max-w-[150px]">
                                                <MovieCard movie={movie} />
                                            </div>
                                        ))}
                                    </div>
                                )}
                            </div>
                        ))}
                    </div>

                    {/* Footer / Input Area */}
                    <div className="p-4 bg-[#1a1a1a] border-t border-white/5">
                        <div className="relative">
                            <input
                                value={input}
                                onChange={(e) => setInput(e.target.value)}
                                onKeyDown={handleKeyDown}
                                placeholder="Hỏi về phim, diễn viên hoặc thể loại..."
                                disabled={isLoading}
                                className="w-full bg-[#232323] text-white text-sm rounded-xl pl-4 pr-12 py-3.5 focus:outline-none focus:ring-1 focus:ring-red-600 transition-all border border-transparent focus:border-red-600/50 disabled:opacity-50"
                            />
                            <button
                                onClick={() => handleSend()}
                                disabled={!input.trim() || isLoading}
                                className="absolute right-2 top-1/2 -translate-y-1/2 p-2 text-red-600 hover:text-red-500 transition disabled:opacity-30"
                            >
                                {isLoading ? <Loader2 size={20} className="animate-spin" /> : <Send size={20} />}
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
