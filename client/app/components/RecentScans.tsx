import React from 'react';
import Link from 'next/link';
import { Clock, CheckCircle2, AlertCircle, Loader2 } from 'lucide-react';

interface Scan {
  id: string;
  target: {
    name: string;
    url: string;
  };
  status: 'completed' | 'failed' | 'in_progress';
  startedAt: string;
  completedAt?: string;
}

interface RecentScansProps {
  scans: Scan[];
}

const RecentScans: React.FC<RecentScansProps> = ({ scans }) => {
  const getStatusIcon = (status: Scan['status']) => {
    switch (status) {
      case 'completed':
        return <CheckCircle2 size={16} className="text-[#10b981]" />; // success-500
      case 'failed':
        return <AlertCircle size={16} className="text-[#ef4444]" />; // error-500
      case 'in_progress':
        return <Loader2 size={16} className="text-[#0ea5e9] animate-spin" />; // primary-500
    }
  };

  const getStatusText = (status: Scan['status']) => {
    switch (status) {
      case 'completed':
        return 'Completed';
      case 'failed':
        return 'Failed';
      case 'in_progress':
        return 'In Progress';
    }
  };

  return (
    <div className="bg-[#1e293b] rounded-lg border border-[#334155] overflow-hidden">
      <div className="p-4 border-b border-[#334155]">
        <h2 className="text-[#f1f5f9] font-medium">Recent Scans</h2>
      </div>
      
      <div className="divide-y divide-[#334155]">
        {scans.map((scan) => (
          <div key={scan.id} className="p-4 hover:bg-[#334155]/50 transition-colors">
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2">
                {getStatusIcon(scan.status)}
                <span className="text-[#cbd5e1] text-sm">
                  {getStatusText(scan.status)}
                </span>
              </div>
              <div className="flex items-center gap-2 text-[#94a3b8] text-sm">
                <Clock size={14} />
                <span>
                  {new Date(scan.startedAt).toLocaleDateString()}
                </span>
              </div>
            </div>
            
            <div className="mb-2">
              <h3 className="text-[#f8fafc] font-medium">{scan.target.name}</h3>
              <p className="text-[#94a3b8] text-sm">{scan.target.url}</p>
            </div>
            
            {scan.status === 'completed' && (
              <Link
                href={`/results/${scan.id}`}
                className="text-[#38bdf8] hover:text-[#7dd3fc] text-sm font-medium"
              >
                View Results
              </Link>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default RecentScans;