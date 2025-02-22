
import { cn } from "@/lib/utils";
import { Link, useLocation } from "react-router-dom";

const navItems = [
  { name: "Dashboard", path: "/dashboard" },
  { name: "Study Activities", path: "/study-activities" },
  { name: "Words", path: "/words" },
  { name: "Word Groups", path: "/groups" },
  { name: "Sessions", path: "/sessions" },
  { name: "Settings", path: "/settings" },
];

export const Navbar = () => {
  const location = useLocation();

  return (
    <nav className="bg-background border-b">
      <div className="max-w-7xl mx-auto px-4">
        <div className="flex h-16 items-center justify-between">
          <div className="flex items-center">
            <Link to="/dashboard" className="flex items-center space-x-2">
              <span className="text-2xl font-bold text-japanese-primary">漢字</span>
              <span className="text-lg font-medium">Learn</span>
            </Link>
          </div>
          <div className="flex items-center space-x-4">
            {navItems.map((item) => (
              <Link
                key={item.path}
                to={item.path}
                className={cn(
                  "px-3 py-2 rounded-md text-sm font-medium transition-colors",
                  location.pathname === item.path
                    ? "bg-primary text-primary-foreground"
                    : "text-foreground/60 hover:text-foreground hover:bg-accent"
                )}
              >
                {item.name}
              </Link>
            ))}
          </div>
        </div>
      </div>
    </nav>
  );
};
