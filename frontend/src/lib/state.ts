import { create } from 'zustand';
import { devtools } from 'zustand/middleware';

import type { DiscordUser } from '@/queries/internal/internalSchemas';

interface State {
  user: DiscordUser | null | undefined;
  setUser: (user: DiscordUser | null) => void;
}

export const useStore = create<State>()(
  devtools((set) => ({
    user: undefined,
    setUser: (user) => set({ user }, false, 'setUser'),
  })),
);
