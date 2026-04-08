import { useState } from "react";
import type { MediaContentGetVm } from "../model/MovieVm";

interface Episode {
    id: number;
    seasonNumber: number;
    episodeNumber: number;
    title: string;
    overview: string;
    videoUrl: string;
    stillPath: string;
}

interface Props {
    movie: MediaContentGetVm | null;
    onEpisodeClick: (episode: Episode, seasonIndex: number) => void;
}
export const EpisodesSelector = ({ movie, onEpisodeClick }: Props) => {
    const [selectedSeasonIdx, setSelectedSeasonIdx] = useState(0);

    if (!movie) return null;

    const isSeries = movie.dtype === 'SERIES';
    const currentSeason = movie.seasons?.[selectedSeasonIdx];

    return (
        <div className="bg-[#141414] text-white p-8 rounded-b-lg">
            {/* 1. Header & Trailer Section */}
            <div className="flex flex-col md:flex-row justify-between items-end mb-8 border-b border-gray-700 pb-6">
                <div>
                    <h2 className="text-3xl font-bold mb-2">Tập phim</h2>
                    {isSeries && (
                        <select
                            className="bg-nfGrey-800 border border-gray-600 p-2 rounded text-lg font-bold outline-none focus:border-white"
                            onChange={(e) => setSelectedSeasonIdx(Number(e.target.value))}
                        >
                            {movie.seasons?.map((s, idx) => (
                                <option key={s.id} value={idx}>Mùa {s.seasonNumber}</option>
                            ))}
                        </select>
                    )}
                </div>

                {movie.trailerKey && (
                    <div className="mt-4 md:mt-0">
                        <p className="text-sm text-gray-400 mb-2">Trailer chính thức</p>
                        <iframe
                            className="rounded-lg shadow-2xl"
                            width="350"
                            height="197"
                            src={`https://www.youtube.com/embed/${movie.trailerKey}`}
                            title="Trailer"
                            allowFullScreen
                        ></iframe>
                    </div>
                )}
            </div>

            <div className="space-y-2">
                {isSeries ? (
                    currentSeason?.episodes && currentSeason.episodes.length > 0 ? (
                        currentSeason.episodes.map((episode: Episode, index) => (
                            <div 
                                key={episode.id} 
                                onClick={() => onEpisodeClick(episode, index)} // <-- Sự kiện Click ở đây
                                className="group flex items-center gap-4 p-4 rounded-md hover:bg-zinc-800 transition cursor-pointer border-b border-zinc-900 last:border-none"
                            >
                                {/* Số thứ tự */}
                                <span className="text-2xl text-gray-500 font-bold w-8">{index + 1}</span>
                                
                                {/* Thumbnail tập phim */}
                                <div className="relative w-40 h-24 flex-shrink-0 overflow-hidden rounded-md">
                                    <img 
                                        src={episode.stillPath ? `https://image.tmdb.org/t/p/w300${episode.stillPath}` : "https://via.placeholder.com/300x169?text=No+Image"} 
                                        alt={episode.title}
                                        className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-300"
                                    />
                                    <div className="absolute inset-0 bg-black/20 group-hover:bg-black/0 transition-colors flex items-center justify-center">
                                        <div className="w-10 h-10 border-2 border-white rounded-full flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
                                            <span className="text-white text-xs">▶</span>
                                        </div>
                                    </div>
                                </div>

                                {/* Thông tin tập phim */}
                                <div className="flex-1">
                                    <div className="flex justify-between mb-1">
                                        <h4 className="font-bold text-gray-200 group-hover:text-white transition-colors">
                                            {episode.episodeNumber}. {episode.title}
                                        </h4>
                                        <span className="text-gray-400 text-sm">Phát ngay</span>
                                    </div>
                                    <p className="text-sm text-gray-500 line-clamp-2 leading-relaxed">
                                        {episode.overview || "Không có mô tả cho tập này."}
                                    </p>
                                </div>
                            </div>
                        ))
                    ) : (
                        <p className="text-gray-500 italic py-10 text-center">Các tập phim của mùa này đang được cập nhật...</p>
                    )
                ) : (
                    <div className="text-gray-400 italic p-10 border border-dashed border-gray-700 rounded-lg text-center">
                        Đây là phim lẻ, vui lòng nhấn nút "Phát" phía trên để xem.
                    </div>
                )}
            </div>
        </div>
    );
};