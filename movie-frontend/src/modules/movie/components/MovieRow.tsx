import { useRef } from "react";
import MovieWrapper from "../../../common/components/MovieWrapper"
import type { MovieThumbnailGetVm } from "../model/MovieThumbnailGetVm"

type Props = {
    title: string,
    movies: MovieThumbnailGetVm[],
    isLarge?: boolean
}

export default function MovieRow({ title, movies, isLarge }: Props) {
    const sliderRef = useRef<HTMLDivElement>(null);

    const handleArrowClick = (direction: "left" | "right") => {
        if (!sliderRef.current) return;

        const { scrollLeft, clientWidth } = sliderRef.current;
        const scrollTo = direction === "left"
            ? scrollLeft - clientWidth
            : scrollLeft + clientWidth;

        sliderRef.current.scrollTo({ left: scrollTo, behavior: "smooth" });
    }

    return <> {movies && movies.length > 0 && (

        <div className="group container mx-auto space-y-2 mb-5 mt-5 relative">
            <h2 className="text-xl font-semibold text-white">{title}</h2>
            <div className="relative">
                <button
                    className="absolute left-0 top-0 z-40 h-full w-12 bg-black/40 text-white opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex items-center justify-center hover:bg-black/60"
                    onClick={() => handleArrowClick("left")}
                >
                    <span className="text-3xl">‹</span>
                </button>
                <div className="flex gap-3 overflow-x-auto scrollbar-hide py-4 hide-scrollbar"
                    ref={sliderRef}

                >
                    {movies.map((movie) => (
                        <MovieWrapper key={movie.id} id={movie.id}>
                            <div
                                key={movie.id}
                                className={`flex-none transition-transform duration-300 hover:scale-105 cursor-pointer ${isLarge ? "h-80 w-56" : "h-32 w-56"
                                    }`}
                            >
                                <img
                                    src={movie.backdropPath ? `https://image.tmdb.org/t/p/w500${movie.backdropPath}` : "https://via.placeholder.com/500x750?text=No+Poster"}
                                    alt={movie.title}
                                    className="h-full w-full rounded-md object-cover"
                                />
                            </div>
                            <div className="text-white text-sm mt-2 truncate">{movie.title}</div>
                        </MovieWrapper>
                    ))}
                </div>
                <button
                    className="absolute right-0 top-0 z-40 h-full w-12 bg-black/40 text-white opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex items-center justify-center hover:bg-black/60"
                    onClick={() => handleArrowClick("right")}
                >
                    <span className="text-3xl">›</span>
                </button>
            </div>
        </div>
    )
    }
    </>
}
