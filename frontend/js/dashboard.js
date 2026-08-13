const API_BASE_URL = "https://sentinel-gdnk.onrender.com";

const recordsBody = document.getElementById("records-body");
const recordCount = document.getElementById("record-count");
const refreshButton = document.getElementById("refresh-button");
const logoutButton = document.getElementById("logout-button");
const dashboardMessage = document.getElementById("dashboard-message");


document.addEventListener("DOMContentLoaded", () => {
    loadDashboardData();
});


async function loadDashboardData() {

    showDashboardMessage("Loading records...", false);

    try {
        const response = await fetch(
            `${API_BASE_URL}/api/admin/data`,
            {
                method: "GET",
                credentials: "include"
            }
        );

        if (response.status === 401) {
            redirectToLogin();
            return;
        }

        const result = await response.json();

        if (!response.ok) {
            throw new Error(
                result.detail || "Unable to retrieve records."
            );
        }

        renderRecords(result.records || []);

        if (recordCount) {
            recordCount.textContent = result.count ?? 0;
        }

        showDashboardMessage(
            `Loaded ${result.count ?? 0} record(s).`,
            false
        );

    } catch (error) {

        console.error("Dashboard error:", error);

        showDashboardMessage(
            error.message || "Unable to load dashboard data."
        );
    }
}


function renderRecords(records) {

    if (!recordsBody) {
        return;
    }

    recordsBody.innerHTML = "";

    if (!records.length) {

        const row = document.createElement("tr");

        row.innerHTML = `
            <td colspan="14" class="empty-state">
                No records available.
            </td>
        `;

        recordsBody.appendChild(row);

        return;
    }


    records.forEach((record) => {

        const row = document.createElement("tr");

        const latitude = record.Latitude || "";
        const longitude = record.Longitude || "";

        let mapButton = "";

        if (latitude && longitude) {

            const mapsUrl =
                `https://www.google.com/maps?q=${encodeURIComponent(
                    `${latitude},${longitude}`
                )}`;

            mapButton = `
                <a
                    href="${mapsUrl}"
                    target="_blank"
                    rel="noopener noreferrer"
                    class="map-button"
                >
                    Show in Maps
                </a>
            `;
        } else {
            mapButton = `
                <span class="status-badge">
                    No location
                </span>
            `;
        }


        row.innerHTML = `
            <td>${escapeHTML(record.ID)}</td>

            <td>${escapeHTML(record.Timestamp)}</td>

            <td>${escapeHTML(record.Name)}</td>

            <td>${escapeHTML(record.Email)}</td>

            <td>${escapeHTML(record.Phone)}</td>

            <td>${escapeHTML(record.IPv4)}</td>

            <td>${escapeHTML(record.IPv6)}</td>

            <td>${escapeHTML(record.Network)}</td>

            <td>${escapeHTML(record.Browser)}</td>

            <td>${escapeHTML(record.OS)}</td>

            <td>${escapeHTML(record.Device)}</td>

            <td>${escapeHTML(latitude)}</td>

            <td>${escapeHTML(longitude)}</td>

            <td>${mapButton}</td>
        `;

        recordsBody.appendChild(row);
    });
}


function escapeHTML(value) {

    if (value === null || value === undefined) {
        return "";
    }

    const div = document.createElement("div");

    div.textContent = String(value);

    return div.innerHTML;
}


async function logout() {

    try {

        const response = await fetch(
            `${API_BASE_URL}/api/admin/logout`,
            {
                method: "POST",
                credentials: "include"
            }
        );

        if (response.ok) {
            redirectToLogin();
            return;
        }

        if (response.status === 401) {
            redirectToLogin();
            return;
        }

        throw new Error("Logout failed.");

    } catch (error) {

        console.error("Logout error:", error);

        showDashboardMessage(
            "Unable to log out. Please try again."
        );
    }
}


function redirectToLogin() {
    window.location.href = "admin.html";
}


function showDashboardMessage(
    message,
    isError = true
) {

    if (!dashboardMessage) {
        return;
    }

    dashboardMessage.textContent = message;

    dashboardMessage.style.color = isError
        ? "var(--danger)"
        : "var(--text-secondary)";
}


if (refreshButton) {
    refreshButton.addEventListener(
        "click",
        loadDashboardData
    );
}


if (logoutButton) {
    logoutButton.addEventListener(
        "click",
        logout
    );
}