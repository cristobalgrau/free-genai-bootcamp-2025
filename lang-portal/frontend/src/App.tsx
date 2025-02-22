
import { ThemeProvider } from "@/components/theme-provider";
import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { Layout } from "./components/layout/Layout";

// Page imports
import Dashboard from "./pages/Dashboard";
import StudyActivities from "./pages/StudyActivities";
import StudyActivity from "./pages/StudyActivity";
import Words from "./pages/Words";
import Word from "./pages/Word";
import Groups from "./pages/Groups";
import Group from "./pages/Group";
import Sessions from "./pages/Sessions";
import Settings from "./pages/Settings";
import NotFound from "./pages/NotFound";

const queryClient = new QueryClient();

const App = () => {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider defaultTheme="light" storageKey="japanese-theme">
        <BrowserRouter>
          <Layout>
            <Routes>
              <Route path="/" element={<Navigate to="/dashboard" replace />} />
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/study-activities" element={<StudyActivities />} />
              <Route path="/study-activities/:id" element={<StudyActivity />} />
              <Route path="/words" element={<Words />} />
              <Route path="/words/:id" element={<Word />} />
              <Route path="/groups" element={<Groups />} />
              <Route path="/groups/:id" element={<Group />} />
              <Route path="/sessions" element={<Sessions />} />
              <Route path="/settings" element={<Settings />} />
              <Route path="*" element={<NotFound />} />
            </Routes>
          </Layout>
        </BrowserRouter>
        <Toaster />
        <Sonner />
      </ThemeProvider>
    </QueryClientProvider>
  );
};

export default App;
