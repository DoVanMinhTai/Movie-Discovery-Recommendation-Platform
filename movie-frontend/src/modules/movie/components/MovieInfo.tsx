import { Star, Clock, Globe } from "lucide-react";
import type { MediaContentGetVm } from "../model/MediaContentGetVm";

export const MovieInfo = ({ movie }: { movie: MediaContentGetVm | null }) => {
    if (!movie) return (
        <div className="w-full animate-pulse bg-[#181818] h-64 rounded-xl" />
    );

    const TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p/w500";

    console.log("MovieInfo Rendered with movie:", movie);

    return (
        <div className="w-full bg-[#181818] text-white rounded-xl shadow-2xl overflow-hidden border border-white/5">
            <div className="flex flex-col md:flex-row gap-8 p-8">

                <div className="hidden md:block w-64 flex-shrink-0">
                    <img
                        src={`${TMDB_IMAGE_BASE}${movie.posterPath}`}
                        alt={movie.title}
                        className="w-full rounded-lg shadow-2xl border border-white/10"
                    />
                </div>

                <div className="flex-1">
                    <div className="mb-6">
                        <h2 className="text-4xl font-black mb-2">
                            {movie.title} <span className="text-gray-500 font-light">({movie.year})</span>
                        </h2>
                        <p className="text-gray-400 italic text-sm">{movie.originalTitle}</p>
                    </div>

                    <div className="flex flex-wrap gap-6 mb-8 text-sm font-medium">
                        <div className="flex items-center gap-2">
                            <Star className="text-yellow-500" size={20} fill="currentColor" />
                            <span className="text-xl font-bold">{movie.rating?.toFixed(1)}</span>
                            <span className="text-gray-500">/10 ({movie.voteCount?.toLocaleString()} votes)</span>
                        </div>
                        <div className="flex items-center gap-2 text-gray-300 border-l border-gray-700 pl-6">
                            <Clock size={18} />
                            <span>{movie.duration} phút</span>
                        </div>
                        <div className="flex items-center gap-2 text-gray-300 border-l border-gray-700 pl-6 uppercase">
                            <Globe size={18} />
                            <span>{movie.originalLanguage || 'EN'}</span>
                        </div>
                    </div>

                    <div className="flex flex-wrap gap-2 mb-8">
                        {movie.genres && movie.genres.split(',').map((genre) => (
                            <span key={genre} className="px-3 py-1.5 bg-red-600 text-white rounded-full text-xs font-semibold">
                                {genre.trim()}
                            </span>
                        ))}
                    </div>

                    <div className="mb-8">
                        <h3 className="text-lg font-bold mb-2 flex items-center gap-2">
                            <Info size={20} className="text-red-500" /> Nội dung phim
                        </h3>
                        <p className="text-gray-300 leading-relaxed text-base">
                            {movie.description}
                        </p>
                    </div>

                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-y-4 gap-x-12 pt-6 border-t border-white/5 text-sm">
                        <div className="flex flex-col gap-1">
                            <span className="text-gray-500 font-bold uppercase text-[10px] tracking-widest">Đạo diễn</span>
                            <span className="text-white font-medium">{movie.director || "Đang cập nhật"}</span>
                        </div>
                        <div className="flex flex-col gap-1">
                            <span className="text-gray-500 font-bold uppercase text-[10px] tracking-widest">Ngày phát hành</span>
                            <span className="text-white font-medium">
                                {movie.releaseDate ? new Date(movie.releaseDate).toLocaleDateString('vi-VN') : "Chưa rõ"}
                            </span>
                        </div>
                        <div className="flex flex-col gap-1">
                            <span className="text-gray-500 font-bold uppercase text-[10px] tracking-widest">Độ phổ biến</span>
                            <span className="text-white font-medium">{movie.popularity?.toFixed(0)}</span>
                        </div>
                        <div className="flex flex-col gap-1">
                            <span className="text-gray-500 font-bold uppercase text-[10px] tracking-widest">Trạng thái</span>
                            <span className="text-green-500 font-medium">Có sẵn chất lượng 4K</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

const Info = ({ size, className }: any) => (
    <svg xmlns="http://www.w3.org/2000/svg" width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}><circle cx="12" cy="12" r="10" /><path d="M12 16v-4" /><path d="M12 8h.01" /></svg>
);