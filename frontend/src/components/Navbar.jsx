import { History, LogOut, PlusCircle } from "lucide-react";
import { Link, useLocation, useNavigate } from "react-router-dom";

import Button from "./Button";
import { useAuth } from "../context/AuthContext";

function Navbar() {
  const navigate = useNavigate();
  const location = useLocation();
  const { logout, user } = useAuth();

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  return (
    <header className="sticky top-0 z-20 border-b border-slate-700/60 bg-slate-950/70 backdrop-blur-xl">
      <div className="mx-auto flex w-full max-w-6xl items-center justify-between px-6 py-4">
        <Link to="/dashboard" className="flex items-center gap-2">
          <span className="rounded-lg bg-gradient-to-r from-fuchsia-500 to-violet-500 px-2.5 py-1 text-sm font-bold text-white">
            PR
          </span>
          <span className="text-lg font-semibold tracking-tight text-slate-100">PRism AI</span>
        </Link>

        <div className="flex items-center gap-3">
          <Link
            to="/dashboard"
            className={`inline-flex items-center gap-1 rounded-lg px-3 py-2 text-sm transition ${
              location.pathname === "/dashboard" ? "bg-slate-800 text-white" : "text-slate-300 hover:bg-slate-800"
            }`}
          >
            <History size={16} />
            Dashboard
          </Link>

          <Link to="/review">
            <Button className="px-3" variant="secondary">
              <PlusCircle size={16} />
              New Review
            </Button>
          </Link>

          <div className="hidden text-right sm:block">
            <p className="text-xs text-slate-400">Signed in as</p>
            <p className="text-sm text-slate-100">{user?.email}</p>
          </div>

          <Button variant="ghost" onClick={handleLogout} className="px-3 text-slate-300">
            <LogOut size={16} />
          </Button>
        </div>
      </div>
    </header>
  );
}

export default Navbar;
