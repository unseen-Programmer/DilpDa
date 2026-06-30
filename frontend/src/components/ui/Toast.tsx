import toast from "react-hot-toast";

export const appToast = {
  error: (message: string) => toast.error(message),
  success: (message: string) => toast.success(message),
};
