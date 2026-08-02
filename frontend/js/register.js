const registerForm =
    document.getElementById("register-form");

const registerMessage =
    document.getElementById("register-message");

const registerButton =
    document.getElementById("register-button");

registerForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    registerMessage.textContent = "";

    registerButton.disabled = true;
    registerButton.textContent = "Creating account...";

    const username = document
        .getElementById("username")
        .value
        .trim();

    const email = document
        .getElementById("email")
        .value
        .trim();

    const password = document
        .getElementById("password")
        .value;

    try {
        await apiRequest("/auth/register", {
            method: "POST",
            body: {
                username,
                email,
                password,
            },
        });

        registerMessage.style.color = "#16a34a";

        registerMessage.textContent =
            "Account created. Redirecting to login...";

        setTimeout(() => {
            window.location.href = "login.html";
        }, 1000);
    } catch (error) {
        registerMessage.style.color = "#dc2626";
        registerMessage.textContent = error.message;
    } finally {
        registerButton.disabled = false;
        registerButton.textContent = "Create account";
    }
});