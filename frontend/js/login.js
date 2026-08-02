const loginForm = document.getElementById("login-form");
const loginMessage = document.getElementById("login-message");
const loginButton = document.getElementById("login-button");

loginForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    loginMessage.textContent = "";
    loginButton.disabled = true;
    loginButton.textContent = "Logging in...";

    const username = document
        .getElementById("username")
        .value
        .trim();

    const password = document
        .getElementById("password")
        .value;

    try {
        await loginUser(username, password);

        const user = await getCurrentUser();

        loginMessage.style.color = "#16a34a";
        loginMessage.textContent = "Login successful.";

        window.location.href =
            user.role === "admin"
                ? "dashboard.html"
                : "index.html";
    } catch (error) {
        removeToken();

        loginMessage.style.color = "#dc2626";
        loginMessage.textContent = error.message;
    } finally {
        loginButton.disabled = false;
        loginButton.textContent = "Login";
    }
});