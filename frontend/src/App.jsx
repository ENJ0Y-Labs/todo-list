import { Navigate, Route, Routes } from "react-router-dom";
import { useAuth } from "./context/AuthContext";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Dashboard from "./pages/Dashboard";

function AuthGate({ children, publicOnly = false }) {
  const { user, checkingAuth } = useAuth();

  if (checkingAuth) {
    return (
      <div className="spinner-page">
        <span className="spinner" aria-label="Checking authentication" />
      </div>
    );
  }

  if (publicOnly && user) return <Navigate to="/dashboard" replace />;
  if (!publicOnly && !user) return <Navigate to="/login" replace />;

  return children;
}

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Navigate to="/dashboard" replace />} />
      <Route path="/login" element={<AuthGate publicOnly><Login /></AuthGate>} />
      <Route path="/register" element={<AuthGate publicOnly><Register /></AuthGate>} />
      <Route path="/dashboard" element={<AuthGate><Dashboard /></AuthGate>} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
