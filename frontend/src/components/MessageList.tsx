import React, { useEffect, useRef } from 'react';
import { Message } from './ChatContainer';
import { motion, AnimatePresence } from 'framer-motion';

const MessageList: React.FC<{ messages: Message[] }> = ({ messages }) => {
  const endRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  return (
    <div className="flex flex-col gap-4 overflow-y-auto pr-2 pb-4">
      <AnimatePresence>
        {messages.map(msg => (
          <motion.div 
            key={msg.id} 
            initial={{ opacity: 0, y: 15, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, scale: 0.9 }}
            transition={{ type: 'spring', stiffness: 400, damping: 25 }}
            className={`flex w-full ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div className={`max-w-[85%] p-4 rounded-3xl shadow-md ${
              msg.sender === 'user' 
                ? 'bg-gradient-to-br from-primary to-purple-600 text-white rounded-br-sm' 
                : 'bg-zinc-800/80 backdrop-blur-md border border-zinc-700/50 text-zinc-100 rounded-bl-sm'
            }`}>
              <p className="whitespace-pre-wrap text-[15px] leading-relaxed">{msg.content}</p>
            </div>
          </motion.div>
        ))}
      </AnimatePresence>
      <div ref={endRef} />
    </div>
  );
};

export default MessageList;
