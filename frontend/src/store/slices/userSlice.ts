import { createSlice, type PayloadAction } from "@reduxjs/toolkit";

type UserProfile = {
  id: number;
  email: string;
  firstName?: string;
  lastName?: string;
  phoneNumber?: string;
};

type UserState = {
  profile: UserProfile | null;
  isLoading: boolean;
};

const initialState: UserState = {
  profile: null,
  isLoading: false,
};

const userSlice = createSlice({
  name: "user",
  initialState,
  reducers: {
    setUserProfile(state, action: PayloadAction<UserProfile>) {
      state.profile = action.payload;
    },
    clearUserProfile(state) {
      state.profile = null;
    },
    setUserLoading(state, action: PayloadAction<boolean>) {
      state.isLoading = action.payload;
    },
  },
});

export const { clearUserProfile, setUserLoading, setUserProfile } = userSlice.actions;
export default userSlice.reducer;
