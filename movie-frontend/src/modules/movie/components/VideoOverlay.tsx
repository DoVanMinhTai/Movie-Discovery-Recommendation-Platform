import { useEffect, useRef } from "react";
import type { MediaContentGetVm } from "../model/MovieVm";
import type { Episode } from "../model/Episode";

type Props = {
    movie: MediaContentGetVm | null;
    episode?: any;
    listEpisode?: Episode[];
    onClose: () => void;
    onSelectEpisode: (episode: any) => void;
};

export default function VideoOverlay({ movie, episode, listEpisode, onClose, onSelectEpisode }: Props) {
    const isSeries = movie?.dtype === 'SERIES';

    const displayEpisodes = (isSeries && (!listEpisode || listEpisode.length === 0))
        ? Array.from({ length: 24 }, (_, i) => ({
            id: i + 1,
            episodeNumber: i + 1,
            title: `Tập ${i + 1}: Cuộc chiến bắt đầu`,
            videoUrl: "https://test-streams.mux.dev/x36xhzz/x36xhzz.m3u8"
        }))
        : listEpisode;

    const currentEpisode = (!episode && isSeries) ? displayEpisodes?.[0] : episode;

    // const embedUrl = currentEpisode ? currentEpisode.videoUrl : (movie?.url || "https://test-streams.mux.dev/x36xhzz/x36xhzz.m3u8");
    const embedUrl = "https://test-streams.mux.dev/x36xhzz/x36xhzz.m3u8";

    const displayTitle = episode
        ? `${movie?.title} - ${episode.title}`
        : movie?.title;

    useEffect(() => {
        document.body.style.overflow = 'hidden';
        return () => {
            document.body.style.overflow = 'auto';
        };
    }, []);

    const scrollContainerRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (scrollContainerRef.current) {
            scrollContainerRef.current.scrollTo({ top: 0, behavior: 'smooth' });
        }
    }, [episode]);

    if (!embedUrl) return null;

    return (
        <div className="fixed inset-0 z-[9999] bg-black flex flex-col h-screen overflow-hidden overscroll-none">

            <div className="absolute top-0 left-0 right-0 p-4 z-[100] bg-gradient-to-b from-black/95 via-black/50 to-transparent flex items-center justify-between transition-opacity duration-300">
                <div className="flex items-center gap-4 min-w-0">
                    <button
                        onClick={onClose}
                        className="text-white p-2 hover:bg-white/20 active:bg-white/30 rounded-full transition-colors"
                        title="Quay lại"
                    >
                        <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
                            <path d="m15 18-6-6 6-6" />
                        </svg>
                    </button>
                    <div className="min-w-0">
                        <h1 className="text-white font-bold text-base sm:text-lg truncate drop-shadow-md">
                            {displayTitle}
                        </h1>
                        <p className="text-gray-300 text-[10px] sm:text-xs opacity-80 truncate">
                            Nguồn: {new URL(embedUrl).hostname}
                        </p>
                    </div>
                </div>
            </div>

            <div className="w-full bg-black flex-none z-50 shadow-xl">
                <div className="w-full aspect-video">
                    <iframe
                        key={currentEpisode?.id || 'movie'}
                        src={embedUrl}
                        className="w-full h-full border-none"
                        allowFullScreen
                        sandbox="allow-forms allow-pointer-lock allow-same-origin allow-scripts allow-top-navigation"
                        allow="autoplay; encrypted-media"
                        referrerPolicy="no-referrer"
                    ></iframe>
                </div>
            </div>

            <div
                ref={scrollContainerRef}
                className="flex-1 overflow-y-auto bg-[#141414] custom-scrollbar"
            >
                {isSeries && (
                    <div className="p-4 border-b border-white/5">
                        <div className="flex justify-between items-center mb-4">
                            <h3 className="text-white font-bold text-sm uppercase tracking-wider">Danh sách tập</h3>
                            <span className="text-gray-500 text-xs">{displayEpisodes?.length} tập</span>
                        </div>

                        <div className="grid grid-cols-5 sm:grid-cols-6 md:grid-cols-8 gap-3">
                            {displayEpisodes?.map((ep) => (
                                <button
                                    key={ep.id}
                                    onClick={() => onSelectEpisode(ep)}
                                    className={`aspect-square rounded-md flex items-center justify-center font-bold text-sm transition-all active:scale-90 ${ep.id === currentEpisode?.id
                                            ? 'bg-red-600 text-white ring-2 ring-red-600 ring-offset-2 ring-offset-[#141414]'
                                            : 'bg-white/10 text-gray-400'
                                        }`}
                                >
                                    {ep.episodeNumber}
                                </button>
                            ))}
                        </div>
                    </div>
                )}

                <div className="p-5 space-y-4 pb-24">
                    <div className="flex items-center gap-3">
                        <span className="text-green-500 font-bold text-sm">95% Match</span>
                        <span className="text-gray-400 text-sm">{movie?.year}</span>
                        <span className="border border-gray-600 px-1 text-[10px] text-gray-400 rounded">HD</span>
                        <span className="text-gray-400 text-sm">{movie?.duration} phút</span>
                    </div>

                    <p className="text-gray-300 text-sm leading-relaxed">
                        {movie?.description || "Mô tả nội dung phim đang được cập nhật..."}
                    </p>

                    <div className="pt-2 border-t border-white/5 space-y-2">
                        <p className="text-[12px] text-gray-500">
                            <span className="text-gray-400">Đạo diễn:</span> {movie?.director || 'N/A'}
                        </p>
                        <p className="text-[12px] text-gray-500">
                            {/* <span className="text-gray-400">Thể loại:</span> {movie?.genres?.join(', ') || 'N/A'} */}
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );
}