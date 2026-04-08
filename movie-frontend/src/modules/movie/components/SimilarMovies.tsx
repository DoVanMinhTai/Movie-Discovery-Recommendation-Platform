import type { MovieThumbnailGetVm } from "../model/MovieThumbnailGetVm";
import MovieRow from "./MovieRow";

export const SimilarMovies = ({ similarMovies }: { similarMovies: MovieThumbnailGetVm[] }) => {
    return (
       <MovieRow title="Similar Movies" movies={similarMovies} />
    );
}