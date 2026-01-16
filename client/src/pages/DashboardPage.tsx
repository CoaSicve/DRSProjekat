import { IUserAPI } from "../api/users/IUserAPI";
import React from "react";
import { DashboardNavbar } from "../components/dashboard/navbar/Navbar";

type DashboardPageProps = {
    userAPI: IUserAPI;
};

export const DashboardPage: React.FC<DashboardPageProps> = ({ userAPI }) => {
    return (
        <div className="dashboard-root">
            {/* Top navbar */}
            <DashboardNavbar userAPI={userAPI} />
           
        </div>
    );
};