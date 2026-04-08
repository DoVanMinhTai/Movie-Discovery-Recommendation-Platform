import type { Episode } from "./Episode";

export interface Season {
    id: number;
    seasonNumber: number;
    title?: string;
    episodes: Episode[];
    posterPath?: string;
}