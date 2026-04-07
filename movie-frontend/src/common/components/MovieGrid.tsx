import MovieWrapper from "./MovieWrapper";
import type { PageAbleResponse } from "../services/ApiClientService";

type MovieGridProps = {
    data: PageAbleResponse;
    loading: boolean;
    onPageChange: (newPage: number) => void;
};

const MovieGrid = ({ data, loading, onPageChange }: MovieGridProps) => {
    return (
        <div className="flex flex-col w-full px-0">
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-y-10 gap-x-4">
                {loading ? (
                    [...Array(12)].map((_, i) => (
                        <div key={i} className="flex flex-col gap-3">
                            <div className="aspect-[2/3] w-full bg-[#2f2f2f] animate-pulse rounded-md" />
                            <div className="h-4 w-3/4 bg-[#2f2f2f] animate-pulse rounded" />
                        </div>
                    ))
                ) : (
                    data?.content?.map((movie) => (
                        <div key={movie.id} className="group cursor-pointer">
                            <MovieWrapper id={movie.id}>
                                <div className="flex flex-col gap-3">
                                    <div className="relative aspect-[2/3] w-full rounded-md overflow-hidden bg-[#1a1a1a] ring-1 ring-white/10 group-hover:ring-red-600 transition-all duration-300">
                                        <img
                                            src={movie.backdropPath
                                                ? `https://image.tmdb.org/t/p/w500${movie.backdropPath}`
                                                : "https://via.placeholder.com/500x750?text=No+Poster"}
                                            alt={movie.title}
                                            loading="lazy"
                                            className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-110"
                                        />

                                        <div className="absolute inset-0 bg-gradient-to-t from-black via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex flex-col justify-end p-3">
                                            <button className="bg-white text-black text-xs font-bold py-2 rounded-sm transform translate-y-4 group-hover:translate-y-0 transition-transform duration-300 shadow-xl">
                                                XEM CHI TIẾT
                                            </button>
                                        </div>
                                    </div>

                                    <div className="flex flex-col">
                                        <h3 className="text-white text-sm font-semibold truncate group-hover:text-red-500 transition-colors">
                                            {movie.title}
                                        </h3>
                                        <div className="flex items-center gap-2 mt-1">
                                            <span className="text-[10px] text-gray-400 border border-gray-600 px-1 rounded-sm uppercase font-bold">
                                                HD
                                            </span>
                                            <span className="text-xs text-gray-500">
                                                {movie.releaseDate?.substring(0, 4) || "N/A"}
                                            </span>
                                        </div>
                                    </div>
                                </div>
                            </MovieWrapper>
                        </div>
                    ))
                )}
            </div>

            {!loading && data && data.totalPages > 1 && (
                <div className="flex justify-center items-center gap-2 mt-16 py-8">
                    <button
                        disabled={data.number === 0}
                        onClick={() => onPageChange(data.number - 1)}
                        className="p-2 px-4 rounded-md bg-[#2f2f2f] text-white disabled:opacity-20 hover:bg-red-600 transition-all duration-200 font-bold text-sm"
                    >
                        &larr; TRƯỚC
                    </button>

                    <div className="flex items-center bg-[#2f2f2f] px-4 py-2 rounded-md mx-2">
                        <span className="text-white font-bold text-sm mr-1">{data.number + 1}</span>
                        <span className="text-gray-500 text-sm">/ {data.totalPages}</span>
                    </div>

                    <button
                        disabled={data.number + 1 >= data.totalPages}
                        onClick={() => onPageChange(data.number + 1)}
                        className="p-2 px-4 rounded-md bg-[#2f2f2f] text-white disabled:opacity-20 hover:bg-red-600 transition-all duration-200 font-bold text-sm"
                    >
                        TIẾP &rarr;
                    </button>
                </div>
            )}
        </div>
    );
}

export default MovieGrid;