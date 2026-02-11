import React, { useEffect, useState } from "react";
import { UserDTO } from "../models/users/UserDTO";
import { UserAPI } from "../api/users/UserAPI";
import { useAuth } from "../hooks/useAuthHook";

const userAPI = new UserAPI();

export const UserProfilePage: React.FC = () => {
  const [user, setUser] = useState<UserDTO | null>(null);
  const [formData, setFormData] = useState({
    name: "",
    lastName: "",
    gender: "",
    dateOfBirth: "",
    state: "",
    street: "",
    number: "",
  });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string>("");
  const [success, setSuccess] = useState<string>("");
  const [profileImage, setProfileImage] = useState<File | null>(null);
  const [previewImage, setPreviewImage] = useState<string>("");
  const { token, user: authUser } = useAuth();
  const serverBase = import.meta.env.VITE_GATEWAY_URL.replace(/\/api\/v1$/, "");

  const resolveImageUrl = (url: string) => {
    if (url.startsWith("http://") || url.startsWith("https://")) {
      return url;
    }
    return `${serverBase}${url}`;
  };

  useEffect(() => {
    if (token && authUser) {
      fetchUserProfile();
    }
  }, [token, authUser]);

  const fetchUserProfile = async () => {
    try {
      setLoading(true);
      setError("");
      const userData = await userAPI.getUserById(token!, authUser!.id);
      setUser(userData);
      setFormData({
        name: userData.name,
        lastName: userData.lastName,
        gender: userData.gender || "",
        dateOfBirth: userData.dateOfBirth || "",
        state: userData.state || "",
        street: userData.street || "",
        number: userData.number || "",
      });
      if (userData.profileImage) {
        setPreviewImage(resolveImageUrl(userData.profileImage));
      }
    } catch (err: any) {
      setError(err?.response?.data?.error || "Failed to load profile");
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>
  ) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
    setError("");
  };

  const handleImageSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setProfileImage(file);
      const reader = new FileReader();
      reader.onload = (event) => {
        setPreviewImage(event.target?.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleSaveProfile = async () => {
    try {
      setSaving(true);
      setError("");
      setSuccess("");

      let dataToSave = Object.fromEntries(
        Object.entries(formData).map(([key, value]) => [
          key,
          value === "" ? undefined : value,
        ])
      );

      const updatedUser = await updateProfile(dataToSave);

      if (profileImage) {
        const userWithImage = await userAPI.uploadProfileImage(
          token!,
          authUser!.id,
          profileImage
        );
        setUser(userWithImage);
        if (userWithImage.profileImage) {
          setPreviewImage(resolveImageUrl(userWithImage.profileImage));
        }
      } else {
        setUser(updatedUser);
      }
    } catch (err: any) {
      setError(err?.response?.data?.error || "Failed to save profile");
    } finally {
      setSaving(false);
    }
  };

  const updateProfile = async (data: any) => {
    const updatedUser = await userAPI.updateUserProfile(
      token!,
      authUser!.id,
      data
    );
    setSuccess("Profile updated successfully!");
    setProfileImage(null);
    setTimeout(() => setSuccess(""), 3000);
    return updatedUser;
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-screen">
        Loading profile...
      </div>
    );
  }

  return (
    <div
      style={{
        minHeight: "100vh",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        padding: "40px 16px",
        background: "var(--win11-bg)",
      }}
    >
      <div
        style={{
          width: "520px",
          maxWidth: "92vw",
          padding: "32px 28px",
          borderRadius: "16px",
          background: "var(--win11-card-bg)",
          border: "1px solid var(--win11-divider)",
          boxShadow: "var(--win11-shadow-medium)",
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
        }}
      >
        <h1 className="text-3xl font-bold mb-6 text-center">My Profile</h1>

        {error && (
          <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded w-full text-center">
            {error}
          </div>
        )}
        {success && (
          <div className="mb-4 p-3 bg-green-100 border border-green-400 text-green-700 rounded w-full text-center">
            {success}
          </div>
        )}
<div className="mb-8 flex flex-col items-center">
  <div
    style={{
      width: "72px",
      height: "72px",
      borderRadius: "50%",
      border: "1px solid var(--win11-divider)",
      background: "rgba(255, 255, 255, 0.08)",
      overflow: "hidden",
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
    }}
  >
    {previewImage ? (
      <img
        src={previewImage}
        alt="Profile"
        style={{ width: "100%", height: "100%", objectFit: "cover" }}
      />
    ) : (
      <span className="text-gray-500 text-xs text-center px-2">
        No Image
      </span>
    )}
  </div>

  <button
    onClick={() => document.getElementById("profileImage")?.click()}
    className="mt-3 cursor-pointer px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 text-sm"
    style={{ display: "inline-flex", alignItems: "center", justifyContent: "center", marginBottom: "12px", marginTop: "12px" }}
  >
    {previewImage ? "Edit Profile Picture" : "Upload Image"}
  </button>

  <input
    id="profileImage"
    type="file"
    accept="image/*"
    onChange={handleImageSelect}
    style={{ display: "none" }}
  />
</div>

        {/* Form Fields */}
        <div
          style={{
            width: "100%",
            maxWidth: "420px",
            display: "grid",
            gridTemplateColumns: "repeat(2, minmax(0, 1fr))",
            columnGap: "20px",
            rowGap: "18px",
          }}
        >
          <div>
            <label className="block text-sm font-medium mb-1">First Name</label>
            <input
              type="text"
              name="name"
              value={formData.name}
              onChange={handleInputChange}
              className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Last Name</label>
            <input
              type="text"
              name="lastName"
              value={formData.lastName}
              onChange={handleInputChange}
              className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Gender</label>
            <select
              name="gender"
              value={formData.gender}
              onChange={handleInputChange}
              className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">Select gender...</option>
              <option value="Male">Male</option>
              <option value="Female">Female</option>
              <option value="Other">Other</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Date of Birth</label>
            <input
              type="date"
              name="dateOfBirth"
              value={formData.dateOfBirth}
              onChange={handleInputChange}
              className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">State</label>
            <input
              type="text"
              name="state"
              value={formData.state}
              onChange={handleInputChange}
              className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Street</label>
            <input
              type="text"
              name="street"
              value={formData.street}
              onChange={handleInputChange}
              className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Street Number</label>
            <input
              type="text"
              name="number"
              value={formData.number}
              onChange={handleInputChange}
              className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Role</label>
            <input
              type="text"
              value={user?.role}
              disabled
              className="w-full px-4 py-2 border rounded-lg bg-gray-100 cursor-not-allowed"
            />
          </div>
        </div>

        {/* Save Button */}
        <div
          style={{ width: "50%", maxWidth: "420px", paddingTop: "30px" }}
          className="mt-8 flex justify-center"
        >
          <button
            onClick={handleSaveProfile}
            disabled={saving}
            className="w-full px-6 py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:bg-gray-400 font-semibold"
          >
            {saving ? "Saving..." : "Save Changes"}
          </button>
          </div>
        </div>
      </div>
  );
};