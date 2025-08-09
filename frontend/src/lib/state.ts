import { create } from 'zustand';
import { devtools } from 'zustand/middleware';

import type { SessionUser } from '@/queries/internal/internalSchemas';

interface State {
  user: SessionUser | null | undefined;
  setUser: (user: SessionUser | null) => void;
}

export const useStore = create<State>()(
  devtools((set) => ({
    user: undefined,
    setUser: (user) => set({ user }, false, 'setUser'),
  })),
);
