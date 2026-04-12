import { Play, Plus } from "lucide-react";
import type { MediaContentGetVm } from "../model/MediaContentGetVm";
import { API_ENDPOINTS } from "../../../constants/ApiEndpoints";

export const MovieHero = ({ movie, onPlayClick }: { movie: MediaContentGetVm | null, onPlayClick: () => void }) => {
    const TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p/original";
    const fullImageUrl = `${TMDB_IMAGE_BASE}${movie?.backdropUrl}`;
    const handleAddFavorite = async () => {
        if (!movie) return;

        try {
            const response = await fetch(API_ENDPOINTS.USER.ADD_FAVORITE, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem("token")}`
                },
                body: JSON.stringify(movie.id)
            });

            if (response.ok) {
                alert("Đã thêm vào danh sách yêu thích!");
            } else {
                alert("Không thể thêm vào danh sách.");
            }
        } catch (error) {
            console.error("Error adding favorite:", error);
        }
    };
    return (
        <div className="relative w-full h-[85vh] overflow-hidden bg-[#141414]">
            <div className="absolute inset-0">
                {movie?.backdropUrl && (
                    <img
                        src={fullImageUrl}
                        alt={movie.title}
                        className="w-full h-full object-cover object-top opacity-70"
                    />
                )}
                <div className="absolute inset-0 bg-gradient-to-t from-[#141414] via-[#141414]/40 to-transparent" />
                <div className="absolute inset-0 bg-gradient-to-r from-[#141414] via-transparent to-transparent" />
            </div>

            <div className="absolute bottom-[10%] left-4 md:left-12 w-full max-w-3xl z-20 px-4">
                <h1 className="text-4xl md:text-7xl font-black text-white mb-6 tracking-tight drop-shadow-2xl">
                    {movie?.title}
                </h1>

                <div className="flex flex-col md:flex-row items-start md:items-end gap-8">
                    {movie?.trailerKey && (
                        <div className="order-1 md:order-2 w-full max-w-[320px] group relative">
                            <div className="absolute -inset-0.5 bg-red-600 rounded-lg blur opacity-20 group-hover:opacity-40 transition duration-300"></div>
                            <div className="relative">
                                <iframe
                                    src={`https://www.youtube.com/embed/${movie.trailerKey}?autoplay=0&mute=1&controls=0&rel=0`}
                                    allow="autoplay; encrypted-media"
                                    allowFullScreen
                                    className="w-full h-[180px] rounded-lg shadow-2xl border border-white/10"
                                />
                                <div className="absolute top-2 left-2 bg-black/60 px-2 py-0.5 rounded text-[10px] text-white uppercase font-bold tracking-wider">
                                    Trailer Preview
                                </div>
                            </div>
                        </div>
                    )}

                    <div className="flex items-center gap-3 order-2 md:order-1">
                        <button
                            onClick={onPlayClick}
                            className="flex items-center gap-2 bg-white text-black px-8 py-2.5 rounded-md font-bold text-xl hover:bg-white/80 transition active:scale-95 shadow-lg"
                        >
                            <Play fill="black" size={24} /> Phát
                        </button>

                        <button
                            onClick={handleAddFavorite}
                            className="flex items-center gap-2 bg-[#6d6d6eb3] text-white px-6 py-2.5 rounded-md font-bold text-xl hover:bg-[#6d6d6e66] transition active:scale-95"
                        >
                            <Plus size={24} /> Danh sách
                        </button>
                    </div>

                </div>
            </div>

            <div className="absolute bottom-0 w-full h-24 bg-gradient-to-t from-[#141414] to-transparent z-10" />
        </div>
    );
}