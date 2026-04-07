import type { Season } from "./Session";

export interface MediaContentGetVm {
    id: number;
    title: string;
    dtype: 'SERIES' | 'MOVIE';
    tmDBId?: number | null;
    originalTitle?: string | null;
    originalLanguage?: string | null;
    description?: string | null;
    backdropUrl?: string | null;
    posterPath?: string | null;
    trailerKey?: string | null;
    url?: string | null;
    year?: number | null;
    releaseDate?: string | null;
    duration?: number | null;     
    genres?: string | null; 
    rating?: number | null; 
    voteCount?: number | null;
    popularity?: number | null;
    cast?: string[] | null;
    director?: string | null;
    seasons?: Season[] | null;
}