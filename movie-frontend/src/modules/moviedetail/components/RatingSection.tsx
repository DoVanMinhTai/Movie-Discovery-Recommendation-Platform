import { useState, useEffect } from "react";
import { toast } from "react-hot-toast";
import { Star, Lock, PlayCircle, Heart } from "lucide-react";
import { canRateMovie, rateMovie } from "../services/MovieService";

export const RatingSection = ({ mediaId }: { mediaId: number }) => {
    const [hover, setHover] = useState(0);
    const [rating, setRating] = useState(0);
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [hasWatched, setHasWatched] = useState(false);
    const [isLoading, setIsLoading] = useState(true);

    const labels: { [key: number]: string } = {
        1: "Không thích",
        2: "Tạm được",
        3: "Khá hay",
        4: "Rất tuyệt",
        5: "Cực phẩm!"
    };

    useEffect(() => {
        const checkStatus = async () => {
            try {
                const watched = await canRateMovie(mediaId);
                setHasWatched(watched);
            } catch (error) {
                console.error("Lỗi kiểm tra lịch sử xem:", error);
                setHasWatched(false);
            } finally {
                setIsLoading(false);
            }
        };
        checkStatus();
    }, [mediaId]);

    const handleRate = async (score: number) => {
        if (!hasWatched) {
            toast.error("Bạn cần xem phim trước khi để lại đánh giá!");
            return;
        }

        setIsSubmitting(true);
        try {
            const success = await rateMovie({
                movieId: mediaId,
                score: score,
                comment: ""
            });

            if (success) {
                setRating(score);
                toast.success(`Tuyệt vời! ${score} sao đã được ghi nhận.`);
            } else {
                toast.error("Gửi đánh giá thất bại.");
            }
        } catch (error) {
            toast.error("Lỗi kết nối server.");
        } finally {
            setIsSubmitting(false);
        }
    };

    if (isLoading) return <div className="animate-pulse h-32 bg-white/5 rounded-lg mt-10" />;

    return (
        <div className="w-full mt-6">
            <div className={`relative overflow-hidden p-6 rounded-xl border transition-all duration-500 ${hasWatched
                    ? "bg-[#181818] border-zinc-800 shadow-xl"
                    : "bg-zinc-900/30 border-zinc-800/50"
                }`}>

                <div className="relative z-10">
                    <div className="flex items-center justify-between mb-6">
                        <div className="flex items-center gap-2">
                            <Heart size={18} className={hasWatched ? "text-red-500" : "text-zinc-500"} fill={hasWatched ? "currentColor" : "none"} />
                            <h3 className="text-lg font-semibold text-white">Bạn thấy phim thế nào?</h3>
                        </div>

                        {!hasWatched && (
                            <span className="flex items-center gap-1.5 text-[11px] font-bold uppercase tracking-wider text-amber-500 bg-amber-500/10 px-2.5 py-1 rounded-full border border-amber-500/20">
                                <Lock size={12} /> Chưa xem
                            </span>
                        )}
                    </div>

                    {!hasWatched ? (
                        <div className="space-y-4">
                            <p className="text-zinc-400 text-sm leading-relaxed">
                                Đánh giá phim chỉ dành cho thành viên đã thưởng thức nội dung này.
                                Hãy xem phim để có thể chia sẻ cảm nhận của bạn với cộng đồng nhé!
                            </p>
                            <button className="flex items-center gap-2 px-5 py-2 bg-white text-black font-bold rounded-md text-sm hover:bg-zinc-200 transition active:scale-95">
                                <PlayCircle size={18} /> Xem ngay
                            </button>
                        </div>
                    ) : (
                        <div className="flex flex-col items-center sm:items-start">
                            <p className="text-zinc-400 text-sm mb-4 text-center sm:text-left">
                                Lựa chọn của bạn giúp chúng mình gợi ý những phim bạn sẽ thích hơn.
                            </p>

                            <div className="flex items-center gap-3">
                                {[1, 2, 3, 4, 5].map((star) => (
                                    <button
                                        key={star}
                                        disabled={isSubmitting}
                                        className="relative group outline-none"
                                        onMouseEnter={() => setHover(star)}
                                        onMouseLeave={() => setHover(0)}
                                        onClick={() => handleRate(star)}
                                    >
                                        <Star
                                            size={38}
                                            strokeWidth={1.5}
                                            className={`transition-all duration-300 transform ${star <= (hover || rating)
                                                    ? "fill-red-600 text-red-600 scale-110 drop-shadow-[0_0_10px_rgba(220,38,38,0.3)]"
                                                    : "text-zinc-700 group-hover:text-zinc-500"
                                                } ${isSubmitting ? "animate-pulse" : "active:scale-90"}`}
                                        />
                                    </button>
                                ))}
                            </div>

                            <div className="mt-5 h-5 flex justify-center sm:justify-start w-full">
                                <p className={`text-sm font-medium transition-all duration-300 ${rating > 0 ? "text-green-500" : "text-red-500"
                                    }`}>
                                    {rating > 0
                                        ? `Đã lưu: ${labels[rating]}`
                                        : hover > 0 ? labels[hover] : ""
                                    }
                                </p>
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};