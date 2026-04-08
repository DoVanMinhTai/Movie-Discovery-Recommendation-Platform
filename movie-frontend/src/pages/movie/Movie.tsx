import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { getMediaContentById, getMovieSimilarById } from "../../modules/movie/service/MovieService";
import type { MediaContentGetVm } from "../../modules/movie/model/MovieVm";
import { MovieHero } from "../../modules/movie/components/MovieHero";
import { MovieInfo } from "../../modules/movie/components/MovieInfo";
import { EpisodesSelector } from "../../modules/movie/components/EpisodesSelector";
import { SimilarMovies } from "../../modules/movie/components/SimilarMovies";
import VideoOverlay from "../../modules/movie/components/VideoOverlay";
import type { MovieThumbnailGetVm } from "../../modules/movie/model/MovieThumbnailGetVm";
import { RatingSection } from "../../modules/movie/components/RatingSection";

export default function MovieDetail() {
  const { id } = useParams<{ id: string }>();
  const [mediaContent, setMediaContent] = useState<MediaContentGetVm | null>(null);
  const [similarMovies, setSimilarMovies] = useState<MovieThumbnailGetVm[]>([]);
  const [isPlaying, setIsPlaying] = useState<boolean>(false);
  const [type, setType] = useState<string>("");
  const [selectedEpisode, setSelectedEpisode] = useState<any>(null);
  const [selectedIndex, setSelectedIndex] = useState<number>(0);

  useEffect(() => {
    if (id) {
      getMediaContentById(Number(id)).then((data: any) => {
        if (data.type === "MOVIE") {
          const mediaContent = data.movieDetailVm;
          setMediaContent(mediaContent);
          setType("MOVIE");
        } else if (data.type === "SERIES") {
          const mediaContent = data.seriesDetailVm;
          setMediaContent(mediaContent);
          setType("SERIES");
        }
      });

      getMovieSimilarById(Number(id)).then((data) => {
        setSimilarMovies(data);
      });
    }
  }, [id]);

  function handlePlay() {
    if (type === "MOVIE") {
      setSelectedEpisode(null);
      setIsPlaying(true);
    } else if (type === "SERIES") {
      const firstSeason = mediaContent?.seasons?.[0];
      const firstEpisode = firstSeason?.episodes?.[0];

      if (firstEpisode) {
        setSelectedEpisode(firstEpisode);
        setIsPlaying(true);
      } else {
        alert("Thông tin tập phim đang được cập nhật!");
      }
    }
  }

  function handleSelectEpisode(episode: any, seasonIndex?: number) {
    setSelectedEpisode(episode);
    setSelectedIndex(seasonIndex ?? 0);
    setIsPlaying(true);
  }

  return (<>

    <MovieHero movie={mediaContent} onPlayClick={() => handlePlay()} />
    <MovieInfo movie={mediaContent} />
    {
      mediaContent && mediaContent.seasons && (
        <EpisodesSelector movie={mediaContent} onEpisodeClick={handleSelectEpisode} />
      )
    }
    {mediaContent?.id &&
      < RatingSection mediaId={mediaContent?.id} />
    }
    <SimilarMovies similarMovies={similarMovies} />
    {isPlaying && (
      <VideoOverlay
        movie={mediaContent}
        episode={selectedEpisode}
        listEpisode={mediaContent?.seasons?.[selectedIndex].episodes ?? []}
        onClose={() => setIsPlaying(false)}
        onSelectEpisode={(ep) => setSelectedEpisode(ep)}
      />
    )}
  </>);
}