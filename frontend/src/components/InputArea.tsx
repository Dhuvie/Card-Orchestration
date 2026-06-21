import React, { useState, useRef } from 'react';
import { Send, Image as ImageIcon, Mic, Square } from 'lucide-react';
import { motion } from 'framer-motion';

interface InputAreaProps {
  onSend: (content: string, type?: 'text' | 'image' | 'audio', file?: File) => void;
  disabled: boolean;
}

const InputArea: React.FC<InputAreaProps> = ({ onSend, disabled }) => {
  const [text, setText] = useState('');
  const [isRecording, setIsRecording] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<BlobPart[]>([]);

  const handleSendText = () => {
    if (!text.trim()) return;
    onSend(text, 'text');
    setText('');
  };

  const handleImageClick = () => {
    if (fileInputRef.current) {
        fileInputRef.current.click();
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
        onSend(file.name, 'image', file);
    }
    // reset
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  const startRecording = async () => {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorderRef.current = new MediaRecorder(stream);
        audioChunksRef.current = [];

        mediaRecorderRef.current.ondataavailable = (event) => {
            if (event.data.size > 0) {
                audioChunksRef.current.push(event.data);
            }
        };

        mediaRecorderRef.current.onstop = () => {
            const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
            const file = new File([audioBlob], "voice_note.webm", { type: 'audio/webm' });
            onSend("Voice Note", 'audio', file);
            stream.getTracks().forEach(track => track.stop());
        };

        mediaRecorderRef.current.start();
        setIsRecording(true);
    } catch (err) {
        console.error("Error accessing microphone:", err);
        alert("Microphone access denied or unavailable.");
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
        mediaRecorderRef.current.stop();
        setIsRecording(false);
    }
  };

  return (
    <div className="flex items-center gap-3 bg-zinc-900/50 p-2 border border-zinc-700/50 rounded-full shadow-inner focus-within:ring-2 focus-within:ring-indigo-500/50 transition-all">
      <input 
        type="file" 
        accept="image/*" 
        className="hidden" 
        ref={fileInputRef} 
        onChange={handleFileChange} 
      />
      
      <motion.button 
        whileTap={{ scale: 0.9 }}
        disabled={disabled || isRecording}
        onClick={handleImageClick}
        className="p-2.5 text-zinc-400 hover:text-white transition-colors rounded-full hover:bg-zinc-800 disabled:opacity-50"
      >
        <ImageIcon size={22} />
      </motion.button>

      {isRecording ? (
        <motion.button 
            whileTap={{ scale: 0.9 }}
            onClick={stopRecording}
            className="p-2.5 text-red-500 animate-pulse transition-colors rounded-full bg-red-500/20"
        >
            <Square size={22} fill="currentColor" />
        </motion.button>
      ) : (
        <motion.button 
            whileTap={{ scale: 0.9 }}
            disabled={disabled}
            onClick={startRecording}
            className="p-2.5 text-zinc-400 hover:text-white transition-colors rounded-full hover:bg-zinc-800 disabled:opacity-50"
        >
            <Mic size={22} />
        </motion.button>
      )}
      
      <input 
        type="text" 
        value={isRecording ? "Recording audio..." : text}
        onChange={e => setText(e.target.value)}
        onKeyDown={e => e.key === 'Enter' && handleSendText()}
        disabled={disabled || isRecording}
        placeholder={disabled ? "Processing your request..." : "Type a message or drop an image..."}
        className="flex-1 bg-transparent text-white px-2 py-2 text-[15px] focus:outline-none disabled:opacity-50 placeholder:text-zinc-500"
      />
      
      <motion.button 
        whileTap={{ scale: 0.9 }}
        disabled={disabled || isRecording || !text.trim()}
        onClick={handleSendText}
        className="p-3 bg-gradient-to-r from-indigo-500 to-purple-600 text-white shadow-md shadow-indigo-500/20 rounded-full disabled:opacity-50 disabled:grayscale transition-all"
      >
        <Send size={18} className="translate-x-[1px]" />
      </motion.button>
    </div>
  );
};

export default InputArea;
