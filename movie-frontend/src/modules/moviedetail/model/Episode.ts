export interface Episode {
    id: number;
    seasonNumber: number;
    episodeNumber: number;
    title: string;
    overview: string;   
    videoUrl: string;
    stillPath: string;  
    duration?: number; 
}