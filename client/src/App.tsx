import { Route, Routes } from "react-router-dom";
import { useEffect } from "react";
import { AuthPage } from "./pages/AuthPage";
import { IAuthAPI } from "./api/auth/IAuthAPI";
import { AuthAPI } from "./api/auth/AuthAPI";
import { UserAPI } from "./api/users/UserAPI";
import { IUserAPI } from "./api/users/IUserAPI";
import { ProtectedRoute } from "./components/protected_route/ProtectedRoute";
import { DashboardPage } from "./pages/DashboardPage";
import { AdminUsersPage } from "./pages/AdminUsersPage";
import { UserProfilePage } from "./pages/UserProfilePage";

const auth_api: IAuthAPI = new AuthAPI();
const user_api: IUserAPI = new UserAPI();

function App() {
  useEffect(() => {
    console.log("App rendered");
  }, []);

  return (
    <>
      <Routes>
        <Route path="/" element={<AuthPage authAPI={auth_api} />} />
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute requiredRole="admin,user,manager">
              <DashboardPage userAPI={user_api} />
            </ProtectedRoute>
          }
        />
        <Route
          path="/admin/users"
          element={
            <ProtectedRoute requiredRole="admin">
              <AdminUsersPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/profile"
          element={
            <ProtectedRoute requiredRole="user,manager">
              <UserProfilePage />
            </ProtectedRoute>
          }
        />
      </Routes>
    </>
  );
}

export default App;
