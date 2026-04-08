import type { MovieThumbnailVm } from "../../movie/model/MovieThumbnailGetVm";

export function MovieCard({ movie }: { movie: MovieThumbnailVm }) {
    return <>
            <div
                onClick={() => window.location.href = `/movie/${movie.id}`}
                className="flex items-center gap-3 bg-black/40 border border-white/10 p-2 rounded-lg mt-2 cursor-pointer hover:bg-white/10 transition"
            >
                <img
                    src={movie.backdropPath
                        ? `https://image.tmdb.org/t/p/w500${movie.backdropPath}`
                        : 'https://via.placeholder.com/200x112?text=No+Image'}
                    className="w-20 h-12 object-cover rounded shadow-md"
                    alt={movie.title}
                />
                <div className="flex-1 min-w-0">
                    <h4 className="text-[12px] font-bold text-white truncate">{movie.title}</h4>
                    {/* <p className="text-[10px] text-gray-400">{movie.releaseDate}</p> */}
                </div>
                <span className="text-nfRed text-lg">Chi Tiet</span>
            </div>
    </>
}