import { createSlice, type PayloadAction } from "@reduxjs/toolkit";

type ThemeMode = "light" | "dark";

type NotificationState = {
  theme: ThemeMode;
  unreadCount: number;
};

const initialState: NotificationState = {
  theme: "light",
  unreadCount: 0,
};

const notificationSlice = createSlice({
  name: "notification",
  initialState,
  reducers: {
    setTheme(state, action: PayloadAction<ThemeMode>) {
      state.theme = action.payload;
      document.documentElement.classList.toggle("dark", action.payload === "dark");
    },
    toggleTheme(state) {
      state.theme = state.theme === "light" ? "dark" : "light";
      document.documentElement.classList.toggle("dark", state.theme === "dark");
    },
    setUnreadCount(state, action: PayloadAction<number>) {
      state.unreadCount = action.payload;
    },
  },
});

export const { setTheme, setUnreadCount, toggleTheme } = notificationSlice.actions;
export default notificationSlice.reducer;
