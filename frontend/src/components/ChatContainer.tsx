import React, { useState } from 'react';
import { useChatStore } from '../store/chatStore';
import MessageList from './MessageList';
import InputArea from './InputArea';
import ApprovalCard from './ApprovalCard';
import { motion } from 'framer-motion';
import { Sparkles } from 'lucide-react';

export interface Message {
  id: string;
  sender: 'user' | 'agent';
  content: string;
  isApprovalRequest?: boolean;
  extractedData?: any;
}

const ChatContainer: React.FC = () => {
  const { sessionId, isProcessing, setProcessing } = useChatStore();
  const [messages, setMessages] = useState<Message[]>([
    { id: '1', sender: 'agent', content: 'Welcome to the CRM Digitization Platform. I am ready to process your visiting cards.' }
  ]);
  const [awaitingApproval, setAwaitingApproval] = useState(false);

  const handleSendMessage = async (content: string, type: 'text' | 'image' | 'audio' = 'text', file?: File) => {
    const newMsg: Message = { 
        id: Date.now().toString(), 
        sender: 'user', 
        content: type === 'text' ? content : `[Uploaded ${type}] ${file?.name || content}` 
    };
    setMessages(prev => [...prev, newMsg]);
    setProcessing(true);

    try {
      const formData = new FormData();
      if (type === 'text') {
          formData.append('message', content);
      } else if (file) {
          formData.append('file', file);
      } else {
          // Fallback if no file is actually provided but type is image/audio
          formData.append('message', `${type}:${content}`);
      }

      const response = await fetch(`http://localhost:8000/api/chat/${sessionId}`, {
        method: 'POST',
        body: formData
      });
      const data = await response.json();
      
      const agentMsg: Message = { id: (Date.now() + 1).toString(), sender: 'agent', content: data.response };
      
      if (data.state?.confirmation_status === 'pending') {
        agentMsg.isApprovalRequest = true;
        agentMsg.extractedData = data.state.extracted_contact;
        setAwaitingApproval(true);
      } else {
        setAwaitingApproval(false);
      }
      setMessages(prev => [...prev, agentMsg]);
    } catch (e) {
      setMessages(prev => [...prev, { id: Date.now().toString(), sender: 'agent', content: 'Error connecting to backend.' }]);
    } finally {
      setProcessing(false);
    }
  };

  const handleApproval = (approved: boolean) => {
    handleSendMessage(approved ? "Yes, approve" : "No, reject", "text");
    setAwaitingApproval(false);
  };

  return (
    <motion.div 
      initial={{ opacity: 0, y: 30 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
      className="w-full max-w-3xl h-[85vh] bg-surface backdrop-blur-2xl rounded-3xl shadow-2xl flex flex-col overflow-hidden border border-white/10 ring-1 ring-black/5"
    >
      <div className="p-5 bg-white/5 border-b border-white/5 flex justify-between items-center backdrop-blur-md">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center shadow-lg">
            <Sparkles size={20} className="text-white" />
          </div>
          <div>
            <h1 className="font-semibold text-lg text-white tracking-tight">CRM Orchestration System</h1>
            <p className="text-xs text-indigo-300 font-medium">Optical & Audio Parsing Enabled</p>
          </div>
        </div>
        <div className="px-3 py-1.5 rounded-full bg-zinc-800/50 border border-white/5 flex items-center gap-2">
          <div className={`w-2 h-2 rounded-full ${isProcessing ? 'bg-amber-500 animate-ping' : 'bg-emerald-500'}`}></div>
          <span className="text-xs text-zinc-400 font-mono tracking-wider">{sessionId.slice(0, 8)}</span>
        </div>
      </div>
      
      <div className="flex-1 overflow-y-auto p-6 flex flex-col">
        <MessageList messages={messages} />
        {awaitingApproval && messages[messages.length - 1]?.extractedData && (
          <ApprovalCard data={messages[messages.length - 1].extractedData} onDecide={handleApproval} />
        )}
      </div>

      <div className="p-5 bg-white/5 border-t border-white/5 backdrop-blur-md">
        <InputArea onSend={handleSendMessage} disabled={awaitingApproval || isProcessing} />
      </div>
    </motion.div>
  );
};

export default ChatContainer;
