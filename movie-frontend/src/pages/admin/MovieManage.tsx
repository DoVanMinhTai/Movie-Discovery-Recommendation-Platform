import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { adminService } from "../../modules/admin/service/AdminService";
import toast from "react-hot-toast";
import { useState, useEffect } from "react";
import { Trash2, Edit3, Plus, Key, X, AlertTriangle, Search, Upload, Film, Calendar, Check, Loader2 } from "lucide-react";
import ImageFallback from "../../common/components/ImageFallback";

const AdminPasswordModal = ({ isOpen, onClose, onConfirm, title, loading }: any) => {
    const [password, setPassword] = useState("");

    useEffect(() => {
        if (isOpen) setPassword("");
    }, [isOpen]);

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 z-[110] flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
            <div className="bg-zinc-900 border border-zinc-800 w-full max-w-md rounded-2xl shadow-2xl overflow-hidden animate-in fade-in zoom-in duration-200">
                <div className="p-6 border-b border-zinc-800 flex justify-between items-center bg-zinc-800/20">
                    <div className="flex items-center gap-3">
                        <div className="p-2 bg-red-500/10 rounded-lg">
                            <Key size={20} className="text-red-500" />
                        </div>
                        <h3 className="font-bold text-white text-lg">{title}</h3>
                    </div>
                    <button onClick={onClose} className="text-zinc-500 hover:text-white transition-colors">
                        <X size={20} />
                    </button>
                </div>
                
                <div className="p-8">
                    <div className="flex items-center gap-3 p-4 bg-yellow-500/5 border border-yellow-500/10 rounded-xl mb-6">
                        <AlertTriangle size={24} className="text-yellow-600 flex-shrink-0" />
                        <p className="text-[11px] text-zinc-400 leading-relaxed">
                            Thao tác này sẽ thay đổi trực tiếp dữ liệu trong Database. Vui lòng nhập mật khẩu Admin để xác nhận.
                        </p>
                    </div>

                    <div className="space-y-4">
                        <div className="space-y-2">
                            <label className="text-[10px] font-black text-zinc-500 uppercase tracking-widest ml-1">Mật khẩu xác thực</label>
                            <input
                                type="password"
                                autoFocus
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                className="w-full bg-zinc-950 border border-zinc-800 rounded-xl px-4 py-3 text-white outline-none focus:border-red-600 transition-all placeholder:text-zinc-700 text-sm"
                                placeholder="Nhập admin password..."
                                onKeyDown={(e) => e.key === 'Enter' && onConfirm(password)}
                            />
                        </div>
                        
                        <button
                            onClick={() => onConfirm(password)}
                            disabled={loading || !password}
                            className="w-full bg-red-600 hover:bg-red-700 disabled:bg-zinc-800 disabled:text-zinc-600 text-white font-bold py-3.5 rounded-xl transition-all shadow-lg shadow-red-900/20 flex items-center justify-center gap-2"
                        >
                            {loading ? (
                                <>
                                    <Loader2 className="w-4 h-4 animate-spin" />
                                    Đang xác thực thực thi...
                                </>
                            ) : "XÁC NHẬN THỰC THI"}
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
};

const MovieFormModal = ({ isOpen, onClose, editMovie, onSubmit, isPending }: any) => {
    const [title, setTitle] = useState("");
    const [originalTitle, setOriginalTitle] = useState("");
    const [overview, setOverview] = useState("");
    const [releaseDate, setReleaseDate] = useState("");
    const [genresId, setGenresId] = useState<number[]>([]);
    const [backdropPath, setBackdropPath] = useState("");
    const [trailerKey, setTrailerKey] = useState("");
    
    const [posterFile, setPosterFile] = useState<File | null>(null);
    const [posterPreview, setPosterPreview] = useState("");
    const [posterError, setPosterError] = useState("");
    const [posterUploading, setPosterUploading] = useState(false);

    const [isDuplicate, setIsDuplicate] = useState(false);
    const [duplicateChecking, setDuplicateChecking] = useState(false);

    const [isPassModalOpen, setIsPassModalOpen] = useState(false);
    const [pendingPayload, setPendingPayload] = useState<any>(null);

    const { data: genresData } = useQuery({
        queryKey: ['admin-genres'],
        queryFn: adminService.getGenres
    });

    useEffect(() => {
        if (isOpen) {
            if (editMovie) {
                setTitle(editMovie.title || "");
                setOriginalTitle(editMovie.originalTitle || "");
                setOverview(editMovie.overview || "");
                setReleaseDate(editMovie.releaseDate ? editMovie.releaseDate.substring(0, 10) : "");
                setGenresId(editMovie.genres ? editMovie.genres.map((g: any) => g.id) : (editMovie.genresId || []));
                setBackdropPath(editMovie.backdropPath || "");
                setTrailerKey(editMovie.trailerKey || "");
                setPosterPreview(editMovie.posterPath || "");
                setPosterFile(null);
                setPosterError("");
                setIsDuplicate(false);
            } else {
                setTitle("");
                setOriginalTitle("");
                setOverview("");
                setReleaseDate("");
                setGenresId([]);
                setBackdropPath("");
                setTrailerKey("");
                setPosterPreview("");
                setPosterFile(null);
                setPosterError("");
                setIsDuplicate(false);
            }
        }
    }, [editMovie, isOpen]);

    const performDuplicateCheck = async (currentTitle: string, currentDate: string) => {
        if (!currentTitle) return;
        const yearStr = currentDate ? currentDate.substring(0, 4) : "";
        if (!yearStr) return;
        const year = parseInt(yearStr);
        if (isNaN(year)) return;

        setDuplicateChecking(true);
        try {
            const res: any = await adminService.checkDuplicate(currentTitle, year, editMovie?.id);
            setIsDuplicate(res.isDuplicate);
        } catch (err) {
            console.error("Lỗi check duplicate phim", err);
        } finally {
            setDuplicateChecking(false);
        }
    };

    const handlePosterChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (!file) return;

        if (file.type !== "image/jpeg" && file.type !== "image/png" && file.type !== "image/jpg") {
            setPosterError("File phải là ảnh (JPG/PNG) và nhỏ hơn 5MB");
            setPosterFile(null);
            setPosterPreview("");
            return;
        }
        if (file.size > 5 * 1024 * 1024) {
            setPosterError("File phải là ảnh (JPG/PNG) và nhỏ hơn 5MB");
            setPosterFile(null);
            setPosterPreview("");
            return;
        }

        setPosterError("");
        setPosterFile(file);
        setPosterPreview(URL.createObjectURL(file));
    };

    const handleFormSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        
        if (isDuplicate) {
            toast.error("Phim bị trùng tên và năm phát hành!");
            return;
        }

        let finalPosterPath = posterPreview;

        if (posterFile) {
            setPosterUploading(true);
            try {
                const uploadPoster = (await import("../../common/utils/uploadPoster")).uploadPoster;
                finalPosterPath = await uploadPoster(posterFile);
            } catch (err: any) {
                toast.error(err.message || "Lỗi tải poster lên Supabase");
                setPosterUploading(false);
                return;
            } finally {
                setPosterUploading(false);
            }
        }

        const formattedDate = releaseDate ? new Date(releaseDate).toISOString() : new Date().toISOString();
        const payload = {
            title,
            originalTitle,
            genresId,
            overview,
            releaseDate: formattedDate,
            posterPath: finalPosterPath,
            backdropPath: backdropPath || "",
            runtime: 0,
            voteAverage: 0,
            voteCount: 0,
            popularity: 0,
            tmDBId: null,
            trailerKey: trailerKey || ""
        };

        const finalPayload = editMovie 
            ? { id: editMovie.id, moviePostVm: payload }
            : payload;

        setPendingPayload(finalPayload);
        setIsPassModalOpen(true);
    };

    const handleConfirmPassword = async (password: string) => {
        try {
            await onSubmit(pendingPayload, password);
            setIsPassModalOpen(false);
            onClose();
        } catch (err) {
            // Error managed by parent components/mutations
        }
    };

    if (!isOpen) return null;

    return (
        <>
            <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/85 backdrop-blur-md p-4 overflow-y-auto">
                <div className="bg-zinc-900 border border-zinc-800 w-full max-w-4xl rounded-2xl shadow-2xl overflow-hidden animate-in fade-in zoom-in duration-200 max-h-[90vh] flex flex-col my-8">
                    {/* Header */}
                    <div className="p-6 border-b border-zinc-800 flex justify-between items-center bg-zinc-800/20 sticky top-0 z-10 backdrop-blur-lg">
                        <div className="flex items-center gap-3">
                            <div className="p-2 bg-red-500/10 rounded-lg">
                                <Film size={20} className="text-red-500" />
                            </div>
                            <h3 className="font-bold text-white text-lg">
                                {editMovie ? `Sửa phim: ${editMovie.title}` : "Thêm phim mới"}
                            </h3>
                        </div>
                        <button onClick={onClose} className="text-zinc-500 hover:text-white transition-colors">
                            <X size={20} />
                        </button>
                    </div>

                    {/* Content */}
                    <form onSubmit={handleFormSubmit} className="p-8 overflow-y-auto flex-1 space-y-6 scrollbar-thin">
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            
                            {/* Left Column Fields */}
                            <div className="space-y-4">
                                <div className="space-y-1.5">
                                    <label className="text-[10px] font-black text-zinc-500 uppercase tracking-widest ml-1">Tên phim</label>
                                    <input
                                        type="text"
                                        required
                                        value={title}
                                        onChange={(e) => setTitle(e.target.value)}
                                        onBlur={() => performDuplicateCheck(title, releaseDate)}
                                        className="w-full bg-zinc-950 border border-zinc-800 rounded-xl px-4 py-2.5 text-white outline-none focus:border-red-600 transition-all text-sm"
                                        placeholder="Nhập tên phim tiếng Việt..."
                                    />
                                    {duplicateChecking && (
                                        <p className="text-xs text-zinc-500 ml-1 animate-pulse">Đang kiểm tra trùng tên...</p>
                                    )}
                                    {isDuplicate && (
                                        <div className="flex items-center gap-1.5 p-2 bg-yellow-500/10 border border-yellow-500/20 rounded-lg text-yellow-500 text-[11px] mt-1.5">
                                            <AlertTriangle size={14} className="flex-shrink-0" />
                                            <span>Phim bị trùng tên và năm phát hành trong cơ sở dữ liệu!</span>
                                        </div>
                                    )}
                                </div>

                                <div className="space-y-1.5">
                                    <label className="text-[10px] font-black text-zinc-500 uppercase tracking-widest ml-1">Tên gốc</label>
                                    <input
                                        type="text"
                                        required
                                        value={originalTitle}
                                        onChange={(e) => setOriginalTitle(e.target.value)}
                                        className="w-full bg-zinc-950 border border-zinc-800 rounded-xl px-4 py-2.5 text-white outline-none focus:border-red-600 transition-all text-sm"
                                        placeholder="Nhập tên gốc (Tiếng Anh/Original Title)..."
                                    />
                                </div>

                                <div className="space-y-1.5">
                                    <label className="text-[10px] font-black text-zinc-500 uppercase tracking-widest ml-1">Ngày phát hành</label>
                                    <div className="relative">
                                        <input
                                            type="date"
                                            required
                                            value={releaseDate}
                                            onChange={(e) => setReleaseDate(e.target.value)}
                                            onBlur={() => performDuplicateCheck(title, releaseDate)}
                                            className="w-full bg-zinc-950 border border-zinc-800 rounded-xl px-4 py-2.5 text-white outline-none focus:border-red-600 transition-all text-sm"
                                        />
                                    </div>
                                </div>

                                <div className="space-y-1.5">
                                    <label className="text-[10px] font-black text-zinc-500 uppercase tracking-widest ml-1">Đường dẫn Backdrop (Ảnh nền)</label>
                                    <input
                                        type="text"
                                        value={backdropPath}
                                        onChange={(e) => setBackdropPath(e.target.value)}
                                        className="w-full bg-zinc-950 border border-zinc-800 rounded-xl px-4 py-2.5 text-white outline-none focus:border-red-600 transition-all text-sm"
                                        placeholder="Ví dụ: /path_backdrop.jpg..."
                                    />
                                </div>

                                <div className="space-y-1.5">
                                    <label className="text-[10px] font-black text-zinc-500 uppercase tracking-widest ml-1">Trailer Key (YouTube)</label>
                                    <input
                                        type="text"
                                        value={trailerKey}
                                        onChange={(e) => setTrailerKey(e.target.value)}
                                        className="w-full bg-zinc-950 border border-zinc-800 rounded-xl px-4 py-2.5 text-white outline-none focus:border-red-600 transition-all text-sm"
                                        placeholder="Ví dụ: dQw4w9WgXcQ..."
                                    />
                                </div>
                            </div>

                            {/* Right Column Fields */}
                            <div className="space-y-4">
                                <div className="space-y-1.5">
                                    <label className="text-[10px] font-black text-zinc-500 uppercase tracking-widest ml-1">Poster Phim (Tải lên Supabase)</label>
                                    <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center">
                                        <div className="w-24 h-36 border border-zinc-800 rounded-xl overflow-hidden bg-zinc-950 flex-shrink-0 relative group">
                                            {posterPreview ? (
                                                <img src={posterPreview} alt="Preview" className="w-full h-full object-cover" />
                                            ) : (
                                                <div className="w-full h-full flex flex-col items-center justify-center text-zinc-700">
                                                    <Film size={24} className="opacity-45 mb-1" />
                                                    <span className="text-[9px] uppercase tracking-wider font-bold">Chưa có</span>
                                                </div>
                                            )}
                                        </div>
                                        <div className="flex-1 w-full space-y-2">
                                            <div className="relative">
                                                <input
                                                    type="file"
                                                    accept="image/*"
                                                    id="posterFileInput"
                                                    onChange={handlePosterChange}
                                                    className="hidden"
                                                />
                                                <label
                                                    htmlFor="posterFileInput"
                                                    className="flex items-center justify-center gap-2 w-full py-3 bg-zinc-950 border border-zinc-800 hover:border-zinc-700 rounded-xl text-xs font-bold text-zinc-400 hover:text-white cursor-pointer transition-all"
                                                >
                                                    <Upload size={16} />
                                                    CHỌN ẢNH ĐẠI DIỆN
                                                </label>
                                            </div>
                                            <p className="text-[10px] text-zinc-500 leading-normal">
                                                Lưu ý: Chỉ chấp nhận ảnh định dạng JPG/PNG dung lượng tối đa 5MB.
                                            </p>
                                            {posterError && (
                                                <p className="text-red-500 text-xs mt-1 font-medium">{posterError}</p>
                                            )}
                                        </div>
                                    </div>
                                </div>

                                <div className="space-y-1.5">
                                    <label className="text-[10px] font-black text-zinc-500 uppercase tracking-widest ml-1">Thể loại</label>
                                    <div className="grid grid-cols-2 sm:grid-cols-3 gap-2 bg-zinc-950 p-4 rounded-xl border border-zinc-800 max-h-40 overflow-y-auto scrollbar-thin">
                                        {Array.isArray(genresData) && genresData.map((genre: any) => (
                                            <label key={genre.id} className="flex items-center gap-2 text-sm text-zinc-300 hover:text-white cursor-pointer select-none">
                                                <input
                                                    type="checkbox"
                                                    checked={genresId.includes(genre.id)}
                                                    onChange={(e) => {
                                                        if (e.target.checked) {
                                                            setGenresId(prev => [...prev, genre.id]);
                                                        } else {
                                                            setGenresId(prev => prev.filter(id => id !== genre.id));
                                                        }
                                                    }}
                                                    className="rounded border-zinc-800 bg-zinc-900 text-red-600 focus:ring-red-600 focus:ring-offset-zinc-900 w-4 h-4 cursor-pointer"
                                                />
                                                <span>{genre.name}</span>
                                            </label>
                                        ))}
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div className="space-y-1.5">
                            <label className="text-[10px] font-black text-zinc-500 uppercase tracking-widest ml-1">Tóm tắt phim (Overview)</label>
                            <textarea
                                value={overview}
                                onChange={(e) => setOverview(e.target.value)}
                                rows={4}
                                required
                                className="w-full bg-zinc-950 border border-zinc-800 rounded-xl px-4 py-3 text-white outline-none focus:border-red-600 transition-all text-sm placeholder:text-zinc-700"
                                placeholder="Viết mô tả ngắn gọn về nội dung phim..."
                            />
                        </div>

                        {/* Actions */}
                        <div className="flex gap-4 pt-4 border-t border-zinc-800">
                            <button
                                type="button"
                                onClick={onClose}
                                className="flex-1 py-3 bg-zinc-800 hover:bg-zinc-700 text-white font-bold rounded-xl transition-all text-sm"
                            >
                                HỦY BỎ
                            </button>
                            <button
                                type="submit"
                                disabled={posterUploading || duplicateChecking || isDuplicate}
                                className="flex-1 bg-red-600 hover:bg-red-700 disabled:bg-zinc-800 disabled:text-zinc-600 text-white font-bold py-3 rounded-xl transition-all text-sm flex items-center justify-center gap-2 shadow-lg shadow-red-950/20"
                            >
                                {posterUploading ? (
                                    <>
                                        <Loader2 className="w-4 h-4 animate-spin" />
                                        ĐANG TẢI ẢNH LÊN...
                                    </>
                                ) : editMovie ? "CẬP NHẬT PHIM" : "THÊM PHIM MỚI"}
                            </button>
                        </div>
                    </form>
                </div>
            </div>

            <AdminPasswordModal
                isOpen={isPassModalOpen}
                title="Xác nhận mật khẩu Admin"
                loading={isPending}
                onClose={() => setIsPassModalOpen(false)}
                onConfirm={handleConfirmPassword}
            />
        </>
    );
};

export default function MovieManage() {
  const queryClient = useQueryClient();
  const [modalState, setModalState] = useState<{isOpen: boolean, movieId: number | null}>({
    isOpen: false,
    movieId: null
  });

  const [isFormModalOpen, setIsFormModalOpen] = useState(false);
  const [editMovie, setEditMovie] = useState<any>(null);

  const { data: movies, isLoading, isError } = useQuery({
    queryKey: ['admin-movies'],
    queryFn: adminService.getMovies,
  });

  const deleteMutation = useMutation({
    mutationFn: ({id, pass}: {id: number, pass: string}) => adminService.deleteMovie(id, pass),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-movies'] });
      toast.success("Đã xóa phim thành công!");
      setModalState({ isOpen: false, movieId: null });
    },
    onError: (error: any) => {
      const msg = error.response?.data || "Có lỗi xảy ra khi xóa phim.";
      toast.error(msg);
    }
  });

  const addMutation = useMutation({
    mutationFn: ({ payload, pass }: { payload: any, pass: string }) => adminService.addMovie(payload, pass),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-movies'] });
      toast.success("Đã thêm phim mới thành công!");
      setIsFormModalOpen(false);
      setEditMovie(null);
    },
    onError: (error: any) => {
      const msg = error.response?.data || "Có lỗi xảy ra khi thêm phim.";
      toast.error(msg);
    }
  });

  const updateMutation = useMutation({
    mutationFn: ({ payload, pass }: { payload: any, pass: string }) => adminService.updateMovie(payload, pass),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-movies'] });
      toast.success("Đã cập nhật phim thành công!");
      setIsFormModalOpen(false);
      setEditMovie(null);
    },
    onError: (error: any) => {
      const msg = error.response?.data || "Có lỗi xảy ra khi cập nhật phim.";
      toast.error(msg);
    }
  });

  const handleDeleteConfirm = (password: string) => {
    if (modalState.movieId) {
      deleteMutation.mutate({ id: modalState.movieId, pass: password });
    }
  };

  const getReleaseYear = (dateStr: string) => {
    if (!dateStr) return "N/A";
    if (dateStr.length >= 4) return dateStr.substring(0, 4);
    return dateStr;
  };

  if (isLoading) return (
    <div className="p-12 space-y-4 animate-pulse bg-[#0a0a0a] min-h-screen">
        <div className="h-8 w-48 bg-zinc-850 rounded-md"></div>
        <div className="h-64 bg-zinc-900/50 rounded-2xl"></div>
    </div>
  );
  
  if (isError) return (
    <div className="p-12 flex flex-col items-center justify-center text-center space-y-4 bg-[#0a0a0a] min-h-screen text-white">
        <div className="p-4 bg-red-500/10 rounded-full text-red-500">
            <AlertTriangle size={48} />
        </div>
        <h2 className="text-xl font-bold">Không thể kết nối Server</h2>
        <p className="text-zinc-500 text-sm max-w-xs">Hãy kiểm tra lại quyền Admin hoặc trạng thái của Backend Service.</p>
    </div>
  );

  return (
    <div className="p-6 md:p-10 bg-[#0a0a0a] min-h-screen text-white">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-8">
        <div>
            <h2 className="text-3xl font-bold bg-gradient-to-r from-white to-zinc-500 bg-clip-text text-transparent">Movie Library</h2>
            <p className="text-zinc-500 text-sm mt-1">Quản lý cơ sở dữ liệu phim và nội dung đa phương tiện</p>
        </div>
        <button
          onClick={() => { setEditMovie(null); setIsFormModalOpen(true); }}
          className="flex items-center gap-2 bg-red-600 hover:bg-red-700 text-white px-6 py-3 rounded-xl font-bold transition-all shadow-lg shadow-red-900/20 hover:-translate-y-0.5 active:scale-95"
        >
          <Plus size={20} />
          THÊM PHIM MỚI
        </button>
      </div>

      <div className="bg-zinc-900/30 border border-zinc-800/80 rounded-2xl overflow-hidden backdrop-blur-sm shadow-2xl">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="bg-zinc-800/30 text-zinc-500 text-[11px] font-black uppercase tracking-widest">
              <th className="px-6 py-5">Thông tin phim</th>
              <th className="px-6 py-5 hidden md:table-cell">Thể loại</th>
              <th className="px-6 py-5 hidden md:table-cell">ID</th>
              <th className="px-6 py-5 text-right">Hành động</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-zinc-800/50">
            {Array.isArray(movies) && movies.length > 0 ? (
              movies.map((item: any) => (
                <tr key={item.id} className="hover:bg-zinc-800/20 transition-all group">
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-4">
                        <div className="relative w-16 h-24 flex-shrink-0">
                            <ImageFallback 
                                src={item.posterPath ? (item.posterPath.startsWith('http') ? item.posterPath : `https://image.tmdb.org/t/p/w200${item.posterPath}`) : "/image_fallback.png"} 
                                className="w-full h-full object-cover rounded-lg shadow-xl border border-zinc-800 group-hover:border-zinc-700 transition-colors" 
                                alt={item.title}
                            />
                        </div>
                        <div className="space-y-1.5 max-w-xs sm:max-w-md md:max-w-lg truncate">
                            <h3 className="font-bold text-zinc-100 group-hover:text-red-500 transition-colors line-clamp-1">{item.title}</h3>
                            <div className="flex items-center gap-2">
                                <span className="text-[10px] bg-zinc-850 text-zinc-400 px-1.5 py-0.5 rounded font-bold uppercase">{item.originalTitle || "Original"}</span>
                                <span className="text-xs text-zinc-500 font-medium">Năm: {getReleaseYear(item.releaseDate)}</span>
                            </div>
                        </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 hidden md:table-cell">
                    <div className="flex flex-wrap gap-1 max-w-[200px]">
                      {Array.isArray(item.genres) && item.genres.length > 0 ? (
                        item.genres.map((g: any) => (
                          <span key={g.id} className="text-[9px] bg-zinc-800 text-zinc-400 px-1.5 py-0.5 rounded border border-zinc-700/30">
                            {g.name}
                          </span>
                        ))
                      ) : (
                        <span className="text-zinc-600 text-xs italic">N/A</span>
                      )}
                    </div>
                  </td>
                  <td className="px-6 py-4 hidden md:table-cell">
                    <span className="text-zinc-600 font-mono text-xs">#{item.id}</span>
                  </td>
                  <td className="px-6 py-4 text-right">
                    <div className="flex justify-end gap-3 opacity-0 group-hover:opacity-100 transition-all translate-x-4 group-hover:translate-x-0">
                      <button
                        onClick={() => { setEditMovie(item); setIsFormModalOpen(true); }}
                        className="flex items-center gap-1 text-zinc-500 hover:text-white transition-colors text-xs font-bold uppercase tracking-tight"
                      >
                        <Edit3 size={16} />
                        Sửa
                      </button>
                      <button 
                        onClick={() => setModalState({ isOpen: true, movieId: item.id })}
                        className="flex items-center gap-1 bg-red-500/10 text-red-500 px-3 py-2 rounded-lg hover:bg-red-500 hover:text-white transition-all text-xs font-bold uppercase tracking-tight"
                      >
                        <Trash2 size={16} />
                        Xóa
                      </button>
                    </div>
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan={4} className="px-6 py-20 text-center">
                  <div className="flex flex-col items-center text-zinc-600">
                    <Search size={48} className="mb-4 opacity-20" />
                    <p className="text-sm italic">Không tìm thấy phim nào trong thư viện.</p>
                  </div>
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      <AdminPasswordModal 
        isOpen={modalState.isOpen}
        title="Xác thực Xóa Phim"
        loading={deleteMutation.isPending}
        onClose={() => setModalState({ isOpen: false, movieId: null })}
        onConfirm={handleDeleteConfirm}
      />

      <MovieFormModal
        isOpen={isFormModalOpen}
        onClose={() => { setIsFormModalOpen(false); setEditMovie(null); }}
        editMovie={editMovie}
        onSubmit={async (payload: any, pass: string) => {
          if (editMovie) {
            await updateMutation.mutateAsync({ payload, pass });
          } else {
            await addMutation.mutateAsync({ payload, pass });
          }
        }}
        isPending={addMutation.isPending || updateMutation.isPending}
      />
    </div>
  );
}
