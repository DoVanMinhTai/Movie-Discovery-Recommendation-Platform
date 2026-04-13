import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import axios from 'axios';
import { API_ENDPOINTS } from '../../constants/ApiEndpoints';

export default function AIRetraining() {
    const queryClient = useQueryClient();
    const [isTraining, setIsTraining] = useState(false);
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
        refetchInterval: isTraining ? 5000 : false
    });

    const trainMutation = useMutation({
        mutationFn: () => axios.post(API_ENDPOINTS.ADMIN.RETRAIN_AI, {}, {
            headers: authHeaders
        }),
        onSuccess: () => {
            setIsTraining(true);
            queryClient.invalidateQueries({ queryKey: ['ai-status'] });
        }
    });

    if (!token) {
        return <div className="text-sm text-red-400">Missing authentication token. Please sign in again.</div>;
    }

    return (
        <div className="space-y-6">
            <div className="flex justify-between items-center">
                <h2 className="text-xl font-bold">Quản lý Recommendation Model</h2>
                <button
                    onClick={() => trainMutation.mutate()}
                    disabled={isTraining || aiData?.currentJob?.status === 'PENDING'}
                    className={`px-6 py-2 rounded-lg font-bold transition-all ${isTraining ? 'bg-zinc-700 text-zinc-400 cursor-not-allowed' : 'bg-red-600 hover:bg-red-700 text-white shadow-lg shadow-red-900/20'
                        }`}
                >
                    {isTraining ? ' Đang xử lý...' : ' Bắt đầu Training lại'}
                </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                {[
                    { label: 'RMSE (Độ lỗi)', value: aiData?.activeModel?.rmse || '0.00', color: 'text-blue-400' },
                    { label: 'MAE', value: aiData?.activeModel?.mae || '0.00', color: 'text-purple-400' },
                    { label: 'F1-Score', value: aiData?.activeModel?.f1Score || '0.00', color: 'text-green-400' },
                    { label: 'Phiên bản', value: `v${aiData?.activeModel?.version || '1.0'}`, color: 'text-yellow-400' },
                ].map((metric, i) => (
                    <div key={i} className="bg-zinc-900 border border-zinc-800 p-4 rounded-xl">
                        <p className="text-zinc-500 text-xs font-bold uppercase">{metric.label}</p>
                        <p className={`text-2xl font-mono mt-1 ${metric.color}`}>{metric.value}</p>
                    </div>
                ))}
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <div className="lg:col-span-2 bg-zinc-900 border border-zinc-800 rounded-xl overflow-hidden">
                    <div className="p-4 border-b border-zinc-800 bg-zinc-800/30">
                        <h3 className="font-bold text-sm">Lịch sử Training Jobs</h3>
                    </div>
                    <div className="overflow-x-auto">
                        <table className="w-full text-left text-sm">
                            <thead className="text-zinc-500 border-b border-zinc-800">
                                <tr>
                                    <th className="p-4 font-medium">Job ID</th>
                                    <th className="p-4 font-medium">Trạng thái</th>
                                    <th className="p-4 font-medium">Thời gian tạo</th>
                                    <th className="p-4 font-medium">Lỗi (nếu có)</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-zinc-800">
                                {aiData?.recentJobs?.map((job: any) => (
                                    <tr key={job.id} className="hover:bg-zinc-800/50 transition-colors">
                                        <td className="p-4 font-mono text-xs text-zinc-400">{job.id.substring(0, 8)}...</td>
                                        <td className="p-4">
                                            <span className={`px-2 py-1 rounded-full text-[10px] font-bold ${job.status === 'SUCCESS' ? 'bg-green-500/10 text-green-500' :
                                                job.status === 'FAILED' ? 'bg-red-500/10 text-red-500' : 'bg-yellow-500/10 text-yellow-500 animate-pulse'
                                                }`}>
                                                {job.status}
                                            </span>
                                        </td>
                                        <td className="p-4 text-zinc-400 text-xs">{job.createdAt}</td>
                                        <td className="p-4 text-red-400 text-xs truncate max-w-[150px]">{job.errorMessage || '-'}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>

                <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-4 space-y-4">
                    <h3 className="font-bold text-sm">Cấu hình Hiện tại</h3>
                    <div className="space-y-3">
                        <div className="flex justify-between text-xs border-b border-zinc-800 pb-2">
                            <span className="text-zinc-500">Model Name</span>
                            <span className="text-zinc-300">{aiData?.activeModel?.name || 'Recommender_v1'}</span>
                        </div>
                        <div className="flex justify-between text-xs border-b border-zinc-800 pb-2">
                            <span className="text-zinc-500">Path</span>
                            <span className="text-zinc-300 font-mono">/models/latest.pkl</span>
                        </div>
                        <div className="flex justify-between text-xs">
                            <span className="text-zinc-500">Trạng thái</span>
                            <span className="text-green-500 flex items-center gap-1">
                                <span className="w-1.5 h-1.5 bg-green-500 rounded-full animate-pulse"></span>
                                Active
                            </span>
                        </div>
                    </div>
                    <div className="p-3 bg-blue-500/5 border border-blue-500/10 rounded-lg">
                        <p className="text-[10px] text-blue-400 leading-relaxed">
                            Gợi ý: Hãy Retrain model khi số lượng Rating mới vượt quá 1000 lượt để đảm bảo độ chính xác.
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );
}