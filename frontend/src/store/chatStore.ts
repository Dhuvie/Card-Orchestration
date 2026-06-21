import { create } from 'zustand'

interface ChatState {
  sessionId: string
  setSessionId: (id: string) => void
  isProcessing: boolean
  setProcessing: (status: boolean) => void
}

export const useChatStore = create<ChatState>((set) => ({
  sessionId: 'S-' + Math.floor(Math.random() * 10000),
  setSessionId: (id) => set({ sessionId: id }),
  isProcessing: false,
  setProcessing: (status) => set({ isProcessing: status }),
}))
