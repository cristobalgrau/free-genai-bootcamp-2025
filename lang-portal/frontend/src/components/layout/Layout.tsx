
import { Navbar } from "./Navbar";
import { Breadcrumbs } from "./Breadcrumbs";

interface LayoutProps {
  children: React.ReactNode;
}

export const Layout = ({ children }: LayoutProps) => {
  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      <Breadcrumbs />
      <main className="max-w-7xl mx-auto px-4 py-8 animate-fadeIn">
        {children}
      </main>
    </div>
  );
};
