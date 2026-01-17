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
        setPreviewImage(userData.profileImage);
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

      if (profileImage) {
        const reader = new FileReader();
        reader.onload = async (event) => {
          const base64Image = event.target?.result as string;
          const profileDataWithImage = {
            ...dataToSave,
            profileImage: base64Image,
          };
          await updateProfile(profileDataWithImage);
        };
        reader.readAsDataURL(profileImage);
      } else {
        await updateProfile(dataToSave);
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
    setUser(updatedUser);
    setSuccess("Profile updated successfully!");
    setProfileImage(null);
    setTimeout(() => setSuccess(""), 3000);
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-screen">
        Loading profile...
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 p-4">
      <div className="bg-white rounded-lg shadow-lg p-8 w-full max-w-lg flex flex-col items-center">
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
  <div className="w-24 h-24 border rounded-md flex items-center justify-center overflow-hidden bg-gray-100">
    {previewImage ? (
      <img
        src={previewImage}
        alt="Profile"
        className="max-w-full max-h-full object-contain"
      />
    ) : (
      <span className="text-gray-500 text-xs text-center px-2">
        No Image
      </span>
    )}
  </div>

  <label
    htmlFor="profileImage"
    className="mt-3 cursor-pointer px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 text-sm"
  >
    Upload Image
  </label>

  <input
    id="profileImage"
    type="file"
    accept="image/*"
    onChange={handleImageSelect}
    className="hidden"
  />
</div>

        {/* Form Fields */}
        <div className="w-full max-w-md space-y-4">
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
        <div className="mt-6 w-full max-w-md flex justify-center">
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