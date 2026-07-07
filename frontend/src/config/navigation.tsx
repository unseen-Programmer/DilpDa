import { FiBarChart2, FiCreditCard, FiGrid, FiHome, FiPackage, FiSearch, FiShoppingBag, FiTruck, FiUsers } from "react-icons/fi";

export const customerNavItems = [
  { icon: <FiHome />, label: "Home", to: "/app" },
  { icon: <FiShoppingBag />, label: "Menu", to: "/app/menu" },
  { icon: <FiSearch />, label: "Search", to: "/app/search" },
  { icon: <FiPackage />, label: "Orders", to: "/app/orders" },
  { icon: <FiCreditCard />, label: "Pay Later", to: "/app/pay-later" },
];

export const restaurantOwnerNavItems = [
  { icon: <FiGrid />, label: "Overview", to: "/owner" },
  { icon: <FiPackage />, label: "Orders", to: "/owner/orders" },
  { icon: <FiBarChart2 />, label: "Insights", to: "/owner/insights" },
];

export const deliveryNavItems = [
  { icon: <FiTruck />, label: "Assignments", to: "/delivery" },
  { icon: <FiPackage />, label: "History", to: "/delivery/history" },
  { icon: <FiCreditCard />, label: "Earnings", to: "/delivery/earnings" },
];

export const adminNavItems = [
  { icon: <FiBarChart2 />, label: "Dashboard", to: "/admin" },
  { icon: <FiUsers />, label: "Users", to: "/admin/users" },
  { icon: <FiGrid />, label: "Operations", to: "/admin/operations" },
];
