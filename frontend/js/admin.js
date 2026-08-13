const API_BASE_URL = "https://sentinel-gdnk.onrender.com";

const loginForm = document.getElementById("login-form");
const loginMessage = document.getElementById("login-message");


if (loginForm) {
    loginForm.addEventListener("submit", async (event) => {
        event.preventDefault();

        const username = document
            .getElementById("username")
            .value
            .trim();

        const password = document
            .getElementById("password")
            .value;

        if (!username || !password) {
            showMessage("Please enter both username and password.");
            return;
        }

        showMessage("Authenticating...", false);

        try {
            const response = await fetch(
                `${API_BASE_URL}/api/admin/login`,
                {
                    method: "POST",

                    headers: {
                        "Content-Type": "application/json"
                    },

                    credentials: "include",

                    body: JSON.stringify({
                        username,
                        password
                    })
                }
            );

            const result = await response.json();

            if (!response.ok) {
                throw new Error(
                    result.detail || "Authentication failed."
                );
            }

            window.location.href = "dashboard.html";

        } catch (error) {
            console.error("Login error:", error);

            showMessage(
                error.message || "Unable to authenticate."
            );
        }
    });
}


function showMessage(message, isError = true) {
    if (!loginMessage) {
        return;
    }

    loginMessage.textContent = message;

    loginMessage.style.color = isError
        ? "var(--danger)"
        : "var(--text-secondary)";
}