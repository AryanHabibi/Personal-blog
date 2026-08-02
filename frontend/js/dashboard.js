const adminWelcome =
    document.getElementById("admin-welcome");

const dashboardMessage =
    document.getElementById("dashboard-message");

const blogsTableBody =
    document.getElementById("blogs-table-body");

const totalBlogs =
    document.getElementById("total-blogs");

const totalCategories =
    document.getElementById("total-categories");

const logoutButton =
    document.getElementById("logout-button");

const categoryForm =
    document.getElementById("category-form");

const categoryNameInput =
    document.getElementById("category-name");

const categoryButton =
    document.getElementById("category-button");

const categoryMessage =
    document.getElementById("category-message");

const categoriesContainer =
    document.getElementById("categories-container");


function extractItems(data) {
    if (Array.isArray(data)) {
        return data;
    }

    if (Array.isArray(data?.items)) {
        return data.items;
    }

    return [];
}


function escapeHtml(value) {
    return String(value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}


async function requireAdmin() {
    try {
        const user = await getCurrentUser();

        if (user.role !== "admin") {
            window.location.href = "index.html";
            return null;
        }

        adminWelcome.textContent =
            `Welcome, ${user.username}. You are signed in as admin.`;

        return user;
    } catch (error) {
        removeToken();
        window.location.href = "login.html";
        return null;
    }
}


function createBlogRow(blog) {
    const row = document.createElement("tr");

    const title =
        escapeHtml(blog.title || "Untitled");

    const author =
        escapeHtml(
            blog.author?.username || "Unknown"
        );

    const category =
        escapeHtml(
            blog.category?.name || "Uncategorized"
        );

    const views =
        Number.isFinite(blog.view_count)
            ? blog.view_count
            : 0;

    row.innerHTML = `
        <td>${title}</td>

        <td>${author}</td>

        <td>${category}</td>

        <td>${views}</td>

        <td class="table-actions">
            <a
                class="small-link"
                href="blog.html?id=${blog.id}"
            >
                View
            </a>

            <a
                class="small-link"
                href="edit-blog.html?id=${blog.id}"
            >
                Edit
            </a>

            <button
                class="danger-button"
                data-blog-id="${blog.id}"
                type="button"
            >
                Delete
            </button>
        </td>
    `;

    return row;
}


function createCategoryItem(category) {
    const item = document.createElement("div");

    item.className = "category-item";

    item.innerHTML = `
        <span>
            ${escapeHtml(category.name)}
        </span>

        <button
            class="danger-button"
            data-category-id="${category.id}"
            type="button"
        >
            Delete
        </button>
    `;

    return item;
}


async function loadBlogs() {
    dashboardMessage.textContent =
        "Loading blogs...";

    blogsTableBody.innerHTML = "";

    try {
        const data = await apiRequest(
            "/blogs?page=1&page_size=100"
        );

        const blogs = extractItems(data);

        totalBlogs.textContent =
            data?.total_items ?? blogs.length;

        if (blogs.length === 0) {
            dashboardMessage.textContent =
                "No blogs found.";

            return;
        }

        dashboardMessage.textContent = "";

        blogs.forEach((blog) => {
            blogsTableBody.appendChild(
                createBlogRow(blog)
            );
        });
    } catch (error) {
        dashboardMessage.textContent =
            error.message;
    }
}


async function loadCategories() {
    categoryMessage.textContent = "";
    categoriesContainer.innerHTML = "";

    try {
        const data = await apiRequest(
            "/categories"
        );

        const categories = extractItems(data);

        totalCategories.textContent =
            categories.length;

        if (categories.length === 0) {
            categoriesContainer.textContent =
                "No categories found.";

            return;
        }

        categories.forEach((category) => {
            categoriesContainer.appendChild(
                createCategoryItem(category)
            );
        });
    } catch (error) {
        categoryMessage.style.color = "#dc2626";
        categoryMessage.textContent =
            error.message;
    }
}


async function loadDashboardData() {
    await Promise.all([
        loadBlogs(),
        loadCategories(),
    ]);
}


blogsTableBody.addEventListener(
    "click",
    async (event) => {
        const deleteButton =
            event.target.closest("[data-blog-id]");

        if (!deleteButton) {
            return;
        }

        const blogId =
            deleteButton.dataset.blogId;

        const confirmed = window.confirm(
            "Are you sure you want to delete this blog?"
        );

        if (!confirmed) {
            return;
        }

        deleteButton.disabled = true;
        deleteButton.textContent = "Deleting...";

        try {
            await apiRequest(
                `/blogs/${blogId}`,
                {
                    method: "DELETE",
                    authenticated: true,
                }
            );

            await loadBlogs();
        } catch (error) {
            alert(error.message);

            deleteButton.disabled = false;
            deleteButton.textContent = "Delete";
        }
    }
);


categoryForm.addEventListener(
    "submit",
    async (event) => {
        event.preventDefault();

        const categoryName =
            categoryNameInput.value.trim();

        if (!categoryName) {
            categoryMessage.style.color =
                "#dc2626";

            categoryMessage.textContent =
                "Category name is required.";

            return;
        }

        categoryMessage.textContent = "";
        categoryButton.disabled = true;
        categoryButton.textContent = "Adding...";

        try {
            await apiRequest(
                "/categories",
                {
                    method: "POST",
                    authenticated: true,
                    body: {
                        name: categoryName,
                    },
                }
            );

            categoryNameInput.value = "";

            categoryMessage.style.color =
                "#16a34a";

            categoryMessage.textContent =
                "Category created successfully.";

            await loadCategories();
        } catch (error) {
            categoryMessage.style.color =
                "#dc2626";

            categoryMessage.textContent =
                error.message;
        } finally {
            categoryButton.disabled = false;
            categoryButton.textContent =
                "Add category";
        }
    }
);


categoriesContainer.addEventListener(
    "click",
    async (event) => {
        const deleteButton =
            event.target.closest(
                "[data-category-id]"
            );

        if (!deleteButton) {
            return;
        }

        const categoryId =
            deleteButton.dataset.categoryId;

        const confirmed = window.confirm(
            "Delete this category?"
        );

        if (!confirmed) {
            return;
        }

        deleteButton.disabled = true;
        deleteButton.textContent = "Deleting...";

        try {
            await apiRequest(
                `/categories/${categoryId}`,
                {
                    method: "DELETE",
                    authenticated: true,
                }
            );

            await Promise.all([
                loadCategories(),
                loadBlogs(),
            ]);
        } catch (error) {
            alert(error.message);

            deleteButton.disabled = false;
            deleteButton.textContent = "Delete";
        }
    }
);


logoutButton.addEventListener(
    "click",
    logoutUser
);


async function initializeDashboard() {
    const admin = await requireAdmin();

    if (!admin) {
        return;
    }

    await loadDashboardData();
}


initializeDashboard();