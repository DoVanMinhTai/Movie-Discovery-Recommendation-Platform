import { useEffect, useState } from 'react';
import { getAuthData } from '../../common/auth/AuthUtils';
import { getMyProfile } from '../../modules/profile/service/ProfileService';
import { 
    User, 
    Mail, 
    Calendar, 
    Settings, 
    LogOut, 
    Trash2, 
    Film, 
    ShieldCheck,
    ChevronRight,
    Heart
} from 'lucide-react';

export default function Profile() {
    const auth = getAuthData();
    const [loading, setLoading] = useState(true);
    const [userData, setUserData] = useState<any>(null);

    useEffect(() => {
        getMyProfile()
            .then((data) => {
                setUserData(data);
            })
            .catch(err => console.error("Lỗi:", err))
            .finally(() => setLoading(false));
    }, []);

    if (loading) return (
        <div className="min-h-screen bg-[#141414] flex items-center justify-center">
            <div className="animate-spin rounded-full h-10 w-10 border-t-2 border-red-600"></div>
        </div>
    );

    return (
        <div className="min-h-screen bg-[#141414] text-zinc-100 selection:bg-red-600/30">
            <div className="h-64 w-full bg-gradient-to-b from-red-900/20 via-[#141414] to-[#141414] absolute top-0 left-0 z-[-1]" />

            <div className="relative max-w-5xl mx-auto pt-32 pb-20 px-6">

                <div className="flex items-center gap-4 mb-12">
                    <h1 className="text-4xl font-black tracking-tight uppercase">Tài khoản</h1>
                    <div className="h-[1px] flex-1 bg-zinc-800 mt-2"></div>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">

                    <div className="lg:col-span-1 space-y-6">
                        <div className="bg-[#181818] border border-white/5 rounded-2xl p-8 flex flex-col items-center text-center shadow-2xl relative overflow-hidden group">
                            <div className="absolute top-0 left-0 w-full h-1 bg-red-600"></div>
                            
                            <div className="relative mb-6">
                                <img 
                                    src="https://upload.wikimedia.org/wikipedia/commons/0/0b/Netflix-avatar.png" 
                                    alt="Avatar" 
                                    className="w-28 h-28 rounded-xl object-cover shadow-2xl group-hover:scale-105 transition-transform duration-500"
                                />
                                <button className="absolute -bottom-2 -right-2 p-2 bg-zinc-800 rounded-lg border border-zinc-700 hover:bg-zinc-700 transition shadow-lg">
                                    <Settings size={16} />
                                </button>
                            </div>

                            <h2 className="text-2xl font-bold mb-1">{userData?.fullName || "Người dùng"}</h2>
                            <p className="text-red-500 text-xs font-black tracking-widest uppercase mb-6 flex items-center gap-1.5">
                                <ShieldCheck size={14} /> {userData?.role}
                            </p>

                            <div className="w-full space-y-4 text-left border-t border-white/5 pt-6">
                                <div className="flex items-center gap-3 text-zinc-400">
                                    <Mail size={16} />
                                    <span className="text-sm truncate">{userData?.email}</span>
                                </div>
                                <div className="flex items-center gap-3 text-zinc-400">
                                    <Calendar size={16} />
                                    <span className="text-sm">Gia nhập: {userData?.joinedDate || "2024"}</span>
                                </div>
                            </div>
                        </div>

                        <div className="bg-[#181818] border border-white/5 rounded-2xl p-6 flex justify-around items-center">
                            <div className="text-center">
                                <p className="text-xs text-zinc-500 uppercase font-bold mb-1">Đã xem</p>
                                <p className="text-xl font-black text-white">128</p>
                            </div>
                            <div className="h-8 w-[1px] bg-zinc-800"></div>
                            <div className="text-center">
                                <p className="text-xs text-zinc-500 uppercase font-bold mb-1">Yêu thích</p>
                                <p className="text-xl font-black text-white">42</p>
                            </div>
                        </div>
                    </div>

                    <div className="lg:col-span-2 space-y-6">
 
                        <section className="bg-[#181818] border border-white/5 rounded-2xl p-8 relative overflow-hidden">
                            <div className="flex items-center justify-between mb-8">
                                <div className="flex items-center gap-3">
                                    <div className="p-2 bg-red-600/10 rounded-lg text-red-600">
                                        <Film size={20} />
                                    </div>
                                    <h3 className="text-xl font-bold">Gu phim của bạn</h3>
                                </div>
                                <button className="text-xs font-bold text-red-500 hover:text-red-400 transition">CẬP NHẬT</button>
                            </div>

                            <div className="flex flex-wrap gap-3">
                                {userData?.preferences?.length > 0 ? (
                                    userData.preferences.map((genre: any, index: number) => (
                                        <div 
                                            key={index} 
                                            className="group flex items-center gap-2 px-5 py-2.5 bg-zinc-800/50 hover:bg-red-600 transition-all duration-300 rounded-full border border-white/5 cursor-default"
                                        >
                                            <span className="text-sm font-semibold text-zinc-300 group-hover:text-white">{genre}</span>
                                        </div>
                                    ))
                                ) : (
                                    <div className="w-full py-8 text-center border border-dashed border-zinc-800 rounded-2xl">
                                        <p className="text-zinc-500 text-sm">Bạn chưa chọn thể loại yêu thích nào.</p>
                                    </div>
                                )}
                            </div>
                        </section>

                        <section className="bg-[#181818] border border-white/5 rounded-2xl overflow-hidden text-sm">
                            <button className="w-full flex items-center justify-between p-5 hover:bg-white/5 transition-colors group">
                                <div className="flex items-center gap-4 text-zinc-300">
                                    <Heart size={18} className="group-hover:text-red-600 transition" />
                                    <span>Danh sách phim yêu thích của tôi</span>
                                </div>
                                <ChevronRight size={16} className="text-zinc-600" />
                            </button>
                            <div className="h-[1px] bg-white/5 mx-5"></div>
                            <button className="w-full flex items-center justify-between p-5 hover:bg-white/5 transition-colors group">
                                <div className="flex items-center gap-4 text-zinc-300">
                                    <Settings size={18} />
                                    <span>Thay đổi mật khẩu & Bảo mật</span>
                                </div>
                                <ChevronRight size={16} className="text-zinc-600" />
                            </button>
                        </section>

                        <div className="flex flex-col sm:flex-row gap-4 pt-4 px-2">
                            <button className="flex items-center justify-center gap-2 px-6 py-3 bg-red-600/10 text-red-600 hover:bg-red-600 hover:text-white transition-all rounded-xl font-bold text-sm">
                                <LogOut size={18} /> Đăng xuất
                            </button>
                            <button className="flex items-center justify-center gap-2 px-6 py-3 text-zinc-500 hover:text-white transition-all font-semibold text-sm">
                                <Trash2 size={18} /> Xóa tài khoản
                            </button>
                        </div>
                    </div>

                </div>
            </div>
        </div>
    );
}