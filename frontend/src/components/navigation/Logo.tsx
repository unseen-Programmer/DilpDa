import { UtensilsCrossed } from "lucide-react";

const Logo = () => {
  return (
    <div className="flex items-center gap-3 cursor-pointer">
      <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-brand-primary text-white shadow-lg">
        <UtensilsCrossed size={24} />
      </div>

      <div>
        <h1 className="text-2xl font-bold text-brand-text">
          DilpDa
        </h1>

        <p className="text-xs uppercase tracking-[4px] text-brand-muted">
          Campus Food
        </p>
      </div>
    </div>
  );
};

export default Logo;