import { FiMoon, FiSun } from "react-icons/fi";

import { useAppDispatch, useAppSelector } from "../../store/hooks";
import { toggleTheme } from "../../store/slices/notificationSlice";
import { Button } from "../ui";

export function ThemeToggle() {
  const dispatch = useAppDispatch();
  const theme = useAppSelector((state) => state.notification.theme);
  const isDark = theme === "dark";

  return (
    <Button
      aria-label="Toggle theme"
      icon={isDark ? <FiSun /> : <FiMoon />}
      onClick={() => dispatch(toggleTheme())}
      size="sm"
      variant="secondary"
    >
      {isDark ? "Light" : "Dark"}
    </Button>
  );
}
