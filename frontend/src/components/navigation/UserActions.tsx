import { Moon, Search } from "lucide-react";

const UserActions = () => {
  return (
    <div className="hidden lg:flex items-center gap-4">

      <button className="rounded-full p-3 hover:bg-brand-primary/10 transition">
        <Search size={20} />
      </button>

      <button className="rounded-full p-3 hover:bg-brand-primary/10 transition">
        <Moon size={20} />
      </button>

      <button className="rounded-xl border border-brand-primary px-5 py-2 text-brand-primary hover:bg-brand-primary hover:text-white transition">
        Login
      </button>

      <button className="rounded-xl bg-brand-primary px-5 py-2 text-white hover:bg-brand-secondary transition">
        Sign Up
      </button>

    </div>
  );
};

export default UserActions;