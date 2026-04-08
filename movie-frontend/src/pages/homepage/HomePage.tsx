import { useEffect, useState } from "react";
import Banner from "../../modules/homepage/components/Banner";
import type { MovieHeroGetVm } from "../../modules/homepage/model/MovieHeroGetVm.ts";
import MovieRow from "../../modules/movie/components/MovieRow.tsx";
import type { MovieThumbnailGetVm } from "../../modules/movie/model/MovieThumbnailGetVm.ts";
import { getHeroMovie, getMoviePreferredGenres, getTop10, getTrending } from "../../modules/homepage/service/HomePageService.ts";

export default function HomePage() {


  const [moviesTop10, setMoviesTop10] = useState<MovieThumbnailGetVm[]>([]);
  const [moviesTrending, setMoviesTrending] = useState<MovieThumbnailGetVm[]>([]);
  const [movieHero, setMovieHero] = useState<MovieHeroGetVm>();
  const [preferredGenres, setPreferredGenres] = useState<Record<string, MovieThumbnailGetVm[]>>({});

  useEffect(() => {
    getHeroMovie().then((data) => {
      setMovieHero(data);
    });

    getTop10().then((data) => {
      setMoviesTop10(data);
    });

    getTrending().then((data) => {
      setMoviesTrending(data);
    });

    getMoviePreferredGenres(10).then((data) => {
      setPreferredGenres(data);
    });

  }, []);

  return (<>
    {movieHero && <Banner movie={movieHero} />}

    <MovieRow
      key="top10"
      title="Top 10 Movies"
      movies={moviesTop10}
    />

    <MovieRow
      key="trending"
      title="Trending Now"
      movies={moviesTrending}
    />

    {Object.entries(preferredGenres).map(([genreName, movieList]) => (
      <MovieRow
        key={genreName}
        title={`Phim ${genreName} dành cho bạn`}
        movies={movieList}
      />
    ))}
  </>
  );
}