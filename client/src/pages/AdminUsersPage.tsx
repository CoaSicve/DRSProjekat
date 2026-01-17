import React, { useEffect, useState } from "react";
import { UserDTO } from "../models/users/UserDTO";
import { UserAPI } from "../api/users/UserAPI";
import { useAuth } from "../hooks/useAuthHook";
import { useNavigate } from "react-router-dom";

const userAPI = new UserAPI();

export const AdminUsersPage: React.FC = () => {
  const [users, setUsers] = useState<UserDTO[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>("");
  const [editingUserId, setEditingUserId] = useState<number | null>(null);
  const [selectedRole, setSelectedRole] = useState<string>("");
  const { token, user } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (!token || user?.role !== "ADMIN") {
      navigate("/dashboard");
      return;
    }

    fetchUsers();
  }, [token, user, navigate]);

  const fetchUsers = async () => {
    try {
      setLoading(true);
      setError("");
      const fetchedUsers = await userAPI.getAllUsers(token!);
      setUsers(fetchedUsers);
    } catch (err: any) {
      setError(err?.response?.data?.error || "Failed to load users");
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteUser = async (userId: number) => {
    if (!window.confirm("Are you sure you want to delete this user?")) return;

    try {
      await userAPI.deleteUser(token!, userId);
      setUsers(users.filter((u) => u.id !== userId));
    } catch (err: any) {
      setError(err?.response?.data?.error || "Failed to delete user");
    }
  };

  const handleChangeRole = async (userId: number, newRole: string) => {
    try {
      const updatedUser = await userAPI.updateUserRole(token!, userId, newRole);
      setUsers(users.map((u) => (u.id === userId ? updatedUser : u)));
      setEditingUserId(null);
      setSelectedRole("");
    } catch (err: any) {
      setError(err?.response?.data?.error || "Failed to update role");
    }
  };

  if (loading) return <div className="p-4">Loading users...</div>;

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-6">Manage Users</h1>

      {error && (
        <div
          className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded"
        >
          {error}
        </div>
      )}

      <div className="overflow-x-auto bg-white rounded-lg shadow">
        <table className="w-full border-collapse">
          <thead>
            <tr className="bg-gray-100 border-b">
              <th className="px-6 py-3 text-left font-semibold">ID</th>
              <th className="px-6 py-3 text-left font-semibold">Name</th>
              <th className="px-6 py-3 text-left font-semibold">Email</th>
              <th className="px-6 py-3 text-left font-semibold">Role</th>
              <th className="px-6 py-3 text-left font-semibold">Actions</th>
            </tr>
          </thead>
          <tbody>
            {users.map((userItem) => (
              <tr key={userItem.id} className="border-b hover:bg-gray-50">
                <td className="px-6 py-4">{userItem.id}</td>
                <td className="px-6 py-4">
                  {userItem.name} {userItem.lastName}
                </td>
                <td className="px-6 py-4">{userItem.email}</td>
                <td className="px-6 py-4">
                  {editingUserId === userItem.id ? (
                    <select
                      value={selectedRole}
                      onChange={(e) => setSelectedRole(e.target.value)}
                      className="px-2 py-1 border rounded"
                    >
                      <option value="">Select role...</option>
                      <option value="USER">USER</option>
                      <option value="MANAGER">MANAGER</option>
                    </select>
                  ) : (
                    <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded text-sm">
                      {userItem.role}
                    </span>
                  )}
                </td>
                <td className="px-6 py-4 space-x-2">
                  {editingUserId === userItem.id ? (
                    <>
                      <button
                        onClick={() =>
                          handleChangeRole(userItem.id, selectedRole)
                        }
                        className="px-3 py-1 bg-green-500 text-white rounded text-sm hover:bg-green-600"
                      >
                        Save
                      </button>
                      <button
                        onClick={() => setEditingUserId(null)}
                        className="px-3 py-1 bg-gray-500 text-white rounded text-sm hover:bg-gray-600"
                      >
                        Cancel
                      </button>
                    </>
                  ) : (
                    <>
                      <button
                        onClick={() => {
                          setEditingUserId(userItem.id);
                          setSelectedRole(userItem.role);
                        }}
                        className="px-3 py-1 bg-blue-500 text-white rounded text-sm hover:bg-blue-600"
                      >
                        Edit Role
                      </button>
                      <button
                        onClick={() => handleDeleteUser(userItem.id)}
                        className="px-3 py-1 bg-red-500 text-white rounded text-sm hover:bg-red-600"
                      >
                        Delete
                      </button>
                    </>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {users.length === 0 && !error && (
        <div className="text-center py-8 text-gray-500">No users found</div>
      )}
    </div>
  );
};
