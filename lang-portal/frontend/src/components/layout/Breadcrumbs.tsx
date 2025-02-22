
import { Link, useLocation } from "react-router-dom";
import { ChevronRight } from "lucide-react";

const getBreadcrumbs = (pathname: string) => {
  const paths = pathname.split("/").filter(Boolean);
  return paths.map((path, index) => {
    const url = `/${paths.slice(0, index + 1).join("/")}`;
    return {
      name: path.split("-").map(word => 
        word.charAt(0).toUpperCase() + word.slice(1)
      ).join(" "),
      url,
    };
  });
};

export const Breadcrumbs = () => {
  const location = useLocation();
  const breadcrumbs = getBreadcrumbs(location.pathname);

  if (breadcrumbs.length === 0) return null;

  return (
    <div className="bg-background/50 backdrop-blur-sm border-b">
      <div className="max-w-7xl mx-auto px-4 py-2">
        <div className="flex items-center space-x-2 text-sm text-muted-foreground">
          <Link to="/dashboard" className="hover:text-foreground transition-colors">
            Home
          </Link>
          {breadcrumbs.map((crumb, index) => (
            <div key={crumb.url} className="flex items-center space-x-2">
              <ChevronRight className="h-4 w-4" />
              {index === breadcrumbs.length - 1 ? (
                <span className="text-foreground">{crumb.name}</span>
              ) : (
                <Link
                  to={crumb.url}
                  className="hover:text-foreground transition-colors"
                >
                  {crumb.name}
                </Link>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
