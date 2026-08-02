const profileMessage =
    document.getElementById("profile-message");

const profileCard =
    document.getElementById("profile-card");

const profileInitial =
    document.getElementById("profile-initial");

const profileUsername =
    document.getElementById("profile-username");

const profileRole =
    document.getElementById("profile-role");

const profileEmail =
    document.getElementById("profile-email");

const profileRoleValue =
    document.getElementById("profile-role-value");

const profileCreatedAt =
    document.getElementById("profile-created-at");

const dashboardLink =
    document.getElementById("dashboard-link");

const logoutButton =
    document.getElementById("logout-button");


function formatDate(value) {
    if (!value) {
        return "Unknown";
    }

    const date = new Date(value);

    if (Number.isNaN(date.getTime())) {
        return "Unknown";
    }

    return date.toLocaleDateString(undefined, {
        year: "numeric",
        month: "long",
        day: "numeric",
    });
}


async function loadProfile() {
    if (!getToken()) {
        window.location.href = "login.html";
        return;
    }

    try {
        const user = await getCurrentUser();

        profileInitial.textContent =
            user.username
                ? user.username.charAt(0).toUpperCase()
                : "U";

        profileUsername.textContent =
            user.username;

        profileRole.textContent =
            user.role === "admin"
                ? "Administrator account"
                : "Regular user account";

        profileEmail.textContent =
            user.email;

        profileRoleValue.textContent =
            user.role;

        profileCreatedAt.textContent =
            formatDate(user.created_at);

        if (user.role === "admin") {
            dashboardLink.classList.remove("hidden");
        }

        profileMessage.textContent = "";
        profileCard.classList.remove("hidden");
    } catch (error) {
        removeToken();
        window.location.href = "login.html";
    }
}


logoutButton.addEventListener(
    "click",
    logoutUser
);


loadProfile();