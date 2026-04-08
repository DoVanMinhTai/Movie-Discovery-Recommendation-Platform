import { useState } from "react";
import { useNavigate } from "react-router-dom";
import type { Hero } from "../model/MovieHeroGetVm"

type Props = {
  movie: Hero;
}

export default function Banner(hero: Props) {
  const navigate = useNavigate();
  const [isPlayTrailer, setIsPlayTrailer] = useState(false);
  const origin = window.location.origin;

  const handlePlayTrailer = () => {
    setIsPlayTrailer(true);
  }

  const handleMoreInfo = () => {
    navigate(`/movie/${hero.movie.id}`);
  }

  return <>
    <div className="relative h-[85vh] w-full">
      <img
        src={hero.movie.backdrop_url ? `https://image.tmdb.org/t/p/w500${hero.movie.backdrop_url}` : "https://via.placeholder.com/500x750?text=No+Poster"}
        alt={hero.movie.title}
        className="w-full h-full object-cover"
      />
      <div className="absolute inset-0 bg-gradient-to-t from-[#141414] via-transparent to-black/30" />

      <div className="absolute bottom-[25%] left-12 space-y-4">
        <h1 className="text-6xl font-extrabold">{hero.movie.title}</h1>
        <p className="max-w-xl text-lg text-gray-300 drop-shadow-md">
          {hero.movie.description}
        </p>
        <div className="flex gap-3">
          <button
            onClick={handlePlayTrailer}
            className="bg-white text-black px-8 py-2 rounded font-bold hover:bg-white/80 transition">Trailer</button>
          <button
            onClick={handleMoreInfo}
            className="bg-gray-500/60 text-white px-8 py-2 rounded font-bold hover:bg-gray-500/40 transition">Thông tin khác</button>
        </div>
      </div>
    </div>
    {isPlayTrailer && (
      <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50">
        <div className="bg-black rounded-lg overflow-hidden w-3/4 h-3/4">
          <iframe
            width="100%"
            height="100%"
            src={`https://www.youtube.com/embed/${hero.movie.trailerKey}?autoplay=1&mute=1&origin=${origin}&rel=0`}
            title="YouTube video player"
            frameBorder="0"
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
            allowFullScreen></iframe>
        </div>
        <button
          onClick={() => setIsPlayTrailer(false)}
          className="absolute top-4 right-4 text-white text-3xl font-bold"
        > × </button>
      </div >
    )
    }
  </>
}