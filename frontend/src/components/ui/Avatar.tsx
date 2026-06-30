import { FiUser } from "react-icons/fi";

type AvatarProps = {
  alt?: string;
  initials?: string;
  src?: string;
};

export function Avatar({ alt = "User avatar", initials, src }: AvatarProps) {
  return (
    <div className="grid h-10 w-10 place-items-center overflow-hidden rounded-full bg-brand-primary text-sm font-bold text-white shadow-soft">
      {src ? <img alt={alt} className="h-full w-full object-cover" src={src} /> : initials ?? <FiUser />}
    </div>
  );
}
