import React from 'react';
import { motion } from 'framer-motion';
import { Check, X } from 'lucide-react';

interface ApprovalCardProps {
  data: any;
  onDecide: (approved: boolean) => void;
}

const ApprovalCard: React.FC<ApprovalCardProps> = ({ data, onDecide }) => {
  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.2 }}
      className="bg-zinc-800/90 backdrop-blur-xl rounded-2xl p-5 border border-indigo-500/30 shadow-2xl shadow-indigo-500/10 self-start max-w-[90%] w-full"
    >
      <h3 className="text-[15px] font-semibold mb-4 text-white flex items-center gap-2">
        <span className="w-2 h-2 rounded-full bg-indigo-500 animate-pulse"></span>
        Extracted Contact Details
      </h3>
      <div className="text-[14px] text-zinc-300 space-y-3 mb-5 bg-zinc-900/50 p-4 rounded-xl font-mono border border-zinc-800">
        <div className="flex justify-between border-b border-zinc-700/50 pb-2"><span className="text-zinc-500">Name:</span> <span className="font-medium text-white">{data.full_name || 'N/A'}</span></div>
        <div className="flex justify-between border-b border-zinc-700/50 pb-2"><span className="text-zinc-500">Company:</span> <span className="font-medium text-white">{data.company || 'N/A'}</span></div>
        <div className="flex justify-between border-b border-zinc-700/50 pb-2"><span className="text-zinc-500">Email:</span> <span className="font-medium text-indigo-400">{data.email || 'N/A'}</span></div>
        <div className="flex justify-between"><span className="text-zinc-500">Phone:</span> <span className="font-medium text-white">{data.phone || 'N/A'}</span></div>
      </div>
      <div className="flex gap-3">
        <motion.button 
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          onClick={() => onDecide(true)}
          className="flex-1 bg-gradient-to-r from-emerald-500 to-emerald-600 shadow-lg shadow-emerald-500/20 text-white py-2.5 rounded-xl text-sm font-semibold flex items-center justify-center gap-2"
        >
          <Check size={18} /> Approve & Save
        </motion.button>
        <motion.button 
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          onClick={() => onDecide(false)}
          className="flex-1 bg-zinc-700 hover:bg-zinc-600 text-white py-2.5 rounded-xl text-sm font-semibold flex items-center justify-center gap-2 border border-zinc-600"
        >
          <X size={18} /> Reject
        </motion.button>
      </div>
    </motion.div>
  );
};

export default ApprovalCard;
