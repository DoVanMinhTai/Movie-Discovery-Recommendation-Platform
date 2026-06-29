import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import axios from 'axios';
import { API_ENDPOINTS } from '../../constants/ApiEndpoints';
import { Brain, Database, Search, RefreshCw, CheckCircle, AlertCircle, Clock, Sparkles, Info } from 'lucide-react';

export default function AIRetraining() {
    const queryClient = useQueryClient();
    const [isTraining, setIsTraining] = useState(false);
    const [isUpdatingRecs, setIsUpdatingRecs] = useState(false);
    const token = localStorage.getItem("token");
    const authHeaders = { Authorization: `Bearer ${token}` };

    const { data: aiData } = useQuery({
        queryKey: ['ai-status'],
        queryFn: async () => {
            const res = await axios.get(API_ENDPOINTS.ADMIN.AI_STATUS, {
                headers: authHeaders
            });
            return res.data;
        },
        refetchInterval: (isTraining || isUpdatingRecs) ? 5000 : false
    });

    const trainMutation = useMutation({
        mutationFn: () => axios.post(API_ENDPOINTS.RECOMMENDATION.CF.UPDATE_RECOMMENDATIONS, {}, {
            headers: authHeaders
        }),
        onSuccess: () => {
            setIsTraining(true);
            queryClient.invalidateQueries({ queryKey: ['ai-status'] });
        }
    });

    const updateRecsMutation = useMutation({
        mutationFn: () => axios.post(API_ENDPOINTS.ADMIN.UPDATE_RECOMMENDATIONS, {}, {
            headers: authHeaders
        }),
        onSuccess: () => {
            setIsUpdatingRecs(true);
            queryClient.invalidateQueries({ queryKey: ['ai-status'] });
            alert("Đã bắt đầu tiến trình cập nhật Similarity Matrix & Elasticsearch!");
        },
        onSettled: () => {
            setTimeout(() => setIsUpdatingRecs(false), 2000);
        }
    });

    if (!token) {
        return <div className="text-sm text-red-400 p-12 text-center">Missing authentication token. Please sign in again.</div>;
    }

    return (
        <div className="space-y-8 p-6 bg-[#0a0a0a] min-h-screen text-white">
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                <div>
                    <h2 className="text-3xl font-bold bg-gradient-to-r from-white to-zinc-500 bg-clip-text text-transparent">
                        AI Model Management
                    </h2>
                    <p className="text-zinc-500 text-sm mt-1">Điều khiển và huấn luyện hệ thống gợi ý thông minh</p>
                </div>
                
                <div className="flex flex-wrap gap-3">
                    <button
                        onClick={() => updateRecsMutation.mutate()}
                        disabled={isUpdatingRecs || aiData?.currentJob?.status === 'PENDING'}
                        className={`flex items-center gap-2 px-5 py-2.5 rounded-lg font-bold transition-all border ${
                            isUpdatingRecs 
                            ? 'bg-blue-500/10 border-blue-500/50 text-blue-400 cursor-not-allowed' 
                            : 'bg-zinc-900 border-zinc-700 hover:border-blue-500 text-zinc-300 hover:text-blue-400'
                        }`}
                    >
                        <RefreshCw size={18} className={isUpdatingRecs ? "animate-spin" : ""} />
                        {isUpdatingRecs ? 'Đang cập nhật...' : 'Cập nhật Similarity & ES'}
                    </button>

                    <button
                        onClick={() => trainMutation.mutate()}
                        disabled={isTraining || aiData?.currentJob?.status === 'PENDING'}
                        className={`flex items-center gap-2 px-6 py-2.5 rounded-lg font-bold transition-all ${
                            isTraining 
                            ? 'bg-zinc-800 text-zinc-500 cursor-not-allowed' 
                            : 'bg-red-600 hover:bg-red-700 text-white shadow-lg shadow-red-900/40 hover:-translate-y-0.5'
                        }`}
                    >
                        <Brain size={18} />
                        {isTraining ? 'Đang Re-train...' : 'Retrain Full Model'}
                    </button>
                </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                {[
                    { label: 'RMSE (Độ lỗi)', value: aiData?.activeModel?.rmse || '0.00', color: 'text-blue-400', icon: AlertCircle },
                    { label: 'MAE', value: aiData?.activeModel?.mae || '0.00', color: 'text-purple-400', icon: CheckCircle },
                    { label: 'F1-Score', value: aiData?.activeModel?.f1Score || '0.00', color: 'text-green-400', icon: Sparkles },
                    { label: 'Phiên bản', value: `v${aiData?.activeModel?.version || '1.0'}`, color: 'text-yellow-400', icon: Clock },
                ].map((metric, i) => (
                    <div key={i} className="bg-zinc-900/50 border border-zinc-800/50 p-5 rounded-2xl hover:border-zinc-700 transition-colors group">
                        <div className="flex justify-between items-start mb-2">
                            <p className="text-zinc-500 text-[10px] font-black uppercase tracking-widest">{metric.label}</p>
                            <metric.icon size={14} className="text-zinc-600 group-hover:text-zinc-400 transition-colors" />
                        </div>
                        <p className={`text-3xl font-mono font-bold ${metric.color}`}>{metric.value}</p>
                    </div>
                ))}
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Jobs Table */}
                <div className="lg:col-span-2 bg-zinc-900/30 border border-zinc-800/80 rounded-2xl overflow-hidden backdrop-blur-sm">
                    <div className="p-5 border-b border-zinc-800/80 flex items-center justify-between bg-zinc-800/20">
                        <div className="flex items-center gap-2">
                            <Database size={18} className="text-zinc-400" />
                            <h3 className="font-bold text-sm">Lịch sử Hoạt động Hệ thống</h3>
                        </div>
                    </div>
                    <div className="overflow-x-auto">
                        <table className="w-full text-left text-sm">
                            <thead className="text-zinc-500 bg-zinc-900/50">
                                <tr>
                                    <th className="p-4 font-semibold text-[11px] uppercase tracking-wider">Tác vụ</th>
                                    <th className="p-4 font-semibold text-[11px] uppercase tracking-wider">Trạng thái</th>
                                    <th className="p-4 font-semibold text-[11px] uppercase tracking-wider">Bắt đầu lúc</th>
                                    <th className="p-4 font-semibold text-[11px] uppercase tracking-wider text-right">Chi tiết</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-zinc-800/50">
                                {aiData?.recentJobs?.map((job: any) => (
                                    <tr key={job.id} className="hover:bg-zinc-800/30 transition-colors group">
                                        <td className="p-4 flex items-center gap-2">
                                            <div className="w-1.5 h-1.5 rounded-full bg-blue-500 shadow-[0_0_8px_rgba(59,130,246,0.5)]"></div>
                                            <span className="font-medium text-zinc-300">
                                                {job.jobType === 'UPDATE_RECS' ? 'Cập nhật Similarity' : 'Retrain Model'}
                                            </span>
                                        </td>
                                        <td className="p-4">
                                            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-[10px] font-bold ${
                                                job.status === 'SUCCESS' ? 'bg-green-500/10 text-green-400 border border-green-500/20' :
                                                job.status === 'FAILED' ? 'bg-red-500/10 text-red-400 border border-red-500/20' : 
                                                'bg-yellow-500/10 text-yellow-400 border border-yellow-500/20 animate-pulse'
                                            }`}>
                                                {job.status}
                                            </span>
                                        </td>
                                        <td className="p-4 text-zinc-500 text-xs font-mono">{job.createdAt}</td>
                                        <td className="p-4 text-right">
                                            <button className="text-zinc-600 group-hover:text-zinc-300 transition-colors">
                                                <Info size={16} />
                                            </button>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>

                {/* Configuration Sidebar */}
                <div className="space-y-6">
                    <div className="bg-zinc-900/30 border border-zinc-800/80 rounded-2xl p-6 space-y-6 backdrop-blur-sm">
                        <div className="flex items-center gap-2 mb-2">
                            <Search size={18} className="text-red-500" />
                            <h3 className="font-bold text-sm">Kiến trúc Hybrid Search</h3>
                        </div>
                        
                        <div className="space-y-4">
                            <div className="flex justify-between items-center text-xs p-3 rounded-lg bg-zinc-800/30 border border-zinc-800">
                                <span className="text-zinc-500">Collaborative Filtering</span>
                                <span className="text-green-400 font-bold uppercase text-[9px]">Sẵn sàng</span>
                            </div>
                            <div className="flex justify-between items-center text-xs p-3 rounded-lg bg-zinc-800/30 border border-zinc-800">
                                <span className="text-zinc-500">Elasticsearch Vector</span>
                                <span className="text-green-400 font-bold uppercase text-[9px]">Connected</span>
                            </div>
                            <div className="flex justify-between items-center text-xs p-3 rounded-lg bg-zinc-800/30 border border-zinc-800">
                                <span className="text-zinc-500">SBERT Embeddings</span>
                                <span className="text-blue-400 font-mono">v3.0.0</span>
                            </div>
                        </div>

                        <div className="p-4 bg-red-500/5 border border-red-500/10 rounded-xl">
                            <h4 className="text-[11px] font-black text-red-500 uppercase mb-2 tracking-widest">Lưu ý quan trọng</h4>
                            <p className="text-[10px] text-zinc-400 leading-relaxed">
                                Nút **"Cập nhật Similarity & ES"** sẽ chạy offline scripts để tính toán lại ma trận tương quan phim-phim và đồng bộ dữ liệu sang Elasticsearch Bonsai. Thao tác này không làm gián đoạn hệ thống.
                            </p>
                        </div>
                    </div>

                    <div className="bg-gradient-to-br from-red-600/10 to-transparent border border-red-500/10 rounded-2xl p-6 relative overflow-hidden group">
                        <div className="absolute -right-4 -bottom-4 opacity-5 group-hover:scale-110 transition-transform">
                            <RefreshCw size={120} />
                        </div>
                        <h3 className="font-bold text-sm mb-2">Trạng thái Model</h3>
                        <div className="flex items-center gap-2 text-green-500 text-sm font-bold">
                            <span className="relative flex h-2 w-2">
                                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
                                <span className="relative inline-flex rounded-full h-2 w-2 bg-green-500"></span>
                            </span>
                            Hệ thống đang hoạt động
                        </div>
                        <p className="text-xs text-zinc-500 mt-2">Đã được tối ưu hóa cho độ trễ 5ms.</p>
                    </div>
                </div>
            </div>
        </div>
    );
}
