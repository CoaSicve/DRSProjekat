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

            {/* ZA SADA STAVIO SAM OVO OVDE, PROMENITI PAGE ILI NAEKAKO PRIKAZATI PREKO DASHBOARDA */}
            {/* Main content */}
            <div className="dashboard-content">
                
                {/* Left panel */}
                <div className="dashboard-panel">
                    <div className="panel-header">
                        <span>Lista biljaka</span>
                        <button className="panel-add">+</button>
                    </div>

                    <input
                        className="panel-search"
                        placeholder="Pretraga biljaka..."
                    />

                    <table className="dashboard-table">
                        <thead>
                            <tr>
                                <th>Naziv</th>
                                <th>Latinski naziv</th>
                                <th>Jacina</th>
                                <th>Zemlja</th>
                                <th>Stanje</th>
                            </tr>
                        </thead>
                        <tbody>
                            {/* map plants here later */}
                        </tbody>
                    </table>
                </div>

                {/* Right panel */}
                <div className="dashboard-panel">
                    <div className="panel-header">
                        <span>Fiskalni racun</span>
                        <button className="panel-add">+</button>
                    </div>

                    <input
                        className="panel-search"
                        placeholder="Pretraga racuna..."
                    />

                    <table className="dashboard-table">
                        <thead>
                            <tr>
                                <th>Broj racuna</th>
                                <th>Tip prodaje</th>
                                <th>Nacin placanja</th>
                                <th>Iznos (RSD)</th>
                                <th>Datum</th>
                            </tr>
                        </thead>
                        <tbody>
                            {/* map receipts here later */}
                        </tbody>
                    </table>


            </div>
        </div>
    </div>
    );
};