import { Navigate, Route, Routes } from "react-router-dom";
import { useAuth } from "./contexts/Auth";
import Layout from "./components/Layout";
import AuthPage from "./pages/Auth";
import Overview from "./pages/Overview";
import Applications from "./pages/Applications";
import Tracker from "./pages/Tracker";
import CalendarPage from "./pages/Calendar";
import Companies from "./pages/Companies";
import Notes from "./pages/Notes";
import Telegram from "./pages/Telegram";
import Recovery from "./pages/Recovery";
import Profile from "./pages/Profile";

function Protected() {
  const { user, loading } = useAuth();
  if (loading) return <p className="p-8 text-center">Memuat…</p>;
  return user ? <Layout /> : <Navigate to="/login" replace />;
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<AuthPage mode="login" />} />
      <Route path="/register" element={<AuthPage mode="register" />} />
      <Route path="/forgot-password" element={<Recovery mode="forgot" />} />
      <Route path="/reset-password" element={<Recovery mode="reset" />} />
      <Route element={<Protected />}>
        <Route path="/" element={<Overview />} />
        <Route path="/applications" element={<Applications />} />
        <Route path="/tracker" element={<Tracker />} />
        <Route path="/calendar" element={<CalendarPage />} />
        <Route path="/companies" element={<Companies />} />
        <Route path="/notes" element={<Notes />} />
        <Route path="/telegram" element={<Telegram />} />
        <Route path="/profile" element={<Profile />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
