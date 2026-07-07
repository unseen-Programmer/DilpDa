    const links = [
  "Home",
  "Restaurants",
  "Menu",
  "About",
  "Contact",
];

const NavLinks = () => {
  return (
    <div className="hidden lg:flex items-center gap-10">
      {links.map((link) => (
        <a
          key={link}
          href="#"
          className="font-medium text-brand-text transition-all duration-300 hover:text-brand-primary"
        >
          {link}
        </a>
      ))}
    </div>
  );
};

export default NavLinks;