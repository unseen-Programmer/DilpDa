import Logo from "./Logo";
import NavLinks from "./NavLinks";
import UserActions from "./UserActions";
import MobileMenu from "./MobileMenu";

const Navbar = () => {
  return (
    <header className="fixed top-0 left-0 z-50 w-full px-4 py-5">

      <div className="container-premium">

        <nav
          className="
            glass
            flex
            h-20
            items-center
            justify-between
            rounded-full
            px-8
            shadow-premium
          "
        >
          <Logo />

          <NavLinks />

          <UserActions />

          <MobileMenu />
        </nav>

      </div>

    </header>
  );
};

export default Navbar;