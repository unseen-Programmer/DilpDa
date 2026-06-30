import { createSlice, type PayloadAction } from "@reduxjs/toolkit";

type CartSummary = {
  itemCount: number;
  totalPayable: string;
};

const initialState: CartSummary = {
  itemCount: 0,
  totalPayable: "0.00",
};

const cartSlice = createSlice({
  name: "cart",
  initialState,
  reducers: {
    setCartSummary(state, action: PayloadAction<CartSummary>) {
      state.itemCount = action.payload.itemCount;
      state.totalPayable = action.payload.totalPayable;
    },
    resetCartSummary(state) {
      state.itemCount = 0;
      state.totalPayable = "0.00";
    },
  },
});

export const { resetCartSummary, setCartSummary } = cartSlice.actions;
export default cartSlice.reducer;
