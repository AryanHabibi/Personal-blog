const API_BASE_URL = "http://127.0.0.1:8000";

function getToken() {
    return localStorage.getItem("access_token");
}

function saveToken(token) {
    localStorage.setItem("access_token", token);
}

function removeToken() {
    localStorage.removeItem("access_token");
}

function getAuthHeaders() {
    const token = getToken();

    if (!token) {
        return {};
    }

    return {
        Authorization: `Bearer ${token}`,
    };
}

async function apiRequest(
    endpoint,
    {
        method = "GET",
        body = null,
        authenticated = false,
        isFormData = false,
    } = {}
) {
    const headers = {};

    if (!isFormData) {
        headers["Content-Type"] = "application/json";
    }

    if (authenticated) {
        Object.assign(headers, getAuthHeaders());
    }

    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        method,
        headers,
        body: body
            ? isFormData
                ? body
                : JSON.stringify(body)
            : null,
    });

    if (response.status === 204) {
        return null;
    }

    const data = await response.json().catch(() => null);

    if (!response.ok) {
        const message =
            data?.detail ||
            `Request failed with status ${response.status}`;

        throw new Error(message);
    }

    return data;
}

async function loginUser(username, password) {
    const formData = new URLSearchParams();

    formData.append("grant_type", "password");
    formData.append("username", username);
    formData.append("password", password);

    const response = await fetch(`${API_BASE_URL}/auth/login`, {
        method: "POST",
        headers: {
            "Content-Type": "application/x-www-form-urlencoded",
        },
        body: formData,
    });

    const data = await response.json().catch(() => null);

    if (!response.ok) {
        throw new Error(
            data?.detail || "Login failed"
        );
    }

    saveToken(data.access_token);

    return data;
}

async function getCurrentUser() {
    return apiRequest("/auth/me", {
        authenticated: true,
    });
}

function logoutUser() {
    removeToken();
    window.location.href = "login.html";
}