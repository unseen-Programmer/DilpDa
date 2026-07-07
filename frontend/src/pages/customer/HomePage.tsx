import { CategoryGrid } from "../../components/home/CategoryGrid";
import { Hero } from "../../components/home/Hero";
import { OfferBanner } from "../../components/home/OfferBanner";
import { PopularFoods } from "../../components/home/PopularFoods";
import { RestaurantInfo } from "../../components/home/RestaurantInfo";
import { Testimonials } from "../../components/home/Testimonials";

export function HomePage() {
  return (
    <div className="grid gap-14">
      <Hero />
      <CategoryGrid />
      <PopularFoods />
      <OfferBanner />
      <RestaurantInfo />
      <Testimonials />
    </div>
  );
}
