import ImageFallback from "../../../common/components/ImageFallback";
import MovieWrapper from "../../../common/components/MovieWrapper";
import { useRef, useState } from "react";

type Props = {
    title: string,
    movies: any[],
}

export default function MovieRow({ title, movies }: Props) {
    const [sliderIndex, setSliderIndex] = useState(0);
    const sliderRef = useRef<HTMLDivElement>(null);

    const handleArrowClick = (direction: "left" | "right") => {
        if (direction === "left") setSliderIndex((prev => Math.max(prev - 1, 0)));
        else setSliderIndex((prev => prev + 1));
    }

    return (<div className="relative group mb-10">
        <h2 className="text-white text-[20px] font-medium ml-12 mb-2">
            {title}
        </h2>

        <div className="relative overflow-hidden px-12">
            {sliderIndex > 0 && (
                <button
                    className="absolute left-0 top-0 bottom-0 z-40 w-12 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity"
                    onClick={() => handleArrowClick("left")}>
                    ◀
                </button>
            )}

            <div ref={sliderRef}
                className="flex gap-2 transition-transform duration-500 ease-out"
                style={{ transform: `translateX(calc(-${sliderIndex * 100}%))` }}>
                {movies.map((movie) => (
                    <div key={movie.id} className="min-w-[16.666%] aspect-video relative">
                        <MovieWrapper key={movie.id} id={movie.id}>

                            <ImageFallback
                                src={movie.image}
                                alt="movie"
                                className="rounded-sm object-cover w-full h-full"
                                fallbackSrc={"/images/image_fallback.png"}
                            />

                            {movie.progress && (
                                <div className="absolute bottom-0 left-0 h-1 bg-nfGrey-400 w-full">
                                    <div className="bg-nfRed h-full" style={{ width: `${movie.progress}%` }} />
                                </div>)
                            };
                        </MovieWrapper>
                    </div>
                ))};
            </div>
            <button
                onClick={() => handleArrowClick('right')}
                className="absolute right-0 top-0 bottom-0 z-40 w-12 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity"
            > ▶ </button>
        </div>
    </div>);
}
