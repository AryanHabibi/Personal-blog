const welcomeMessage =
    document.getElementById("welcome-message");

const dashboardLink =
    document.getElementById("dashboard-link");

const createBlogLink =
    document.getElementById("create-blog-link");

const loginLink =
    document.getElementById("login-link");

const registerLink =
    document.getElementById("register-link");

const logoutButton =
    document.getElementById("logout-button");

const searchInput =
    document.getElementById("search-input");

const searchButton =
    document.getElementById("search-button");

const categoriesMessage =
    document.getElementById("categories-message");

const categoriesContainer =
    document.getElementById("categories-container");

const clearCategoryButton =
    document.getElementById("clear-category-button");

const featuredSection =
    document.getElementById("featured-section");

const featuredBlogContainer =
    document.getElementById("featured-blog-container");

const articlesTitle =
    document.getElementById("articles-title");

const articlesCount =
    document.getElementById("articles-count");

const blogsLoading =
    document.getElementById("blogs-loading");

const blogsEmpty =
    document.getElementById("blogs-empty");

const blogsMessage =
    document.getElementById("blogs-message");

const blogsContainer =
    document.getElementById("blogs-container");

const pagination =
    document.getElementById("pagination");

const paginationMessage =
    document.getElementById("pagination-message");

const previousPageButton =
    document.getElementById("previous-page-button");

const nextPageButton =
    document.getElementById("next-page-button");

const currentYear =
    document.getElementById("current-year");

const profileLink =
    document.getElementById("profile-link");    

const state = {
    currentUser: null,
    page: 1,
    pageSize: 6,
    totalPages: 0,
    search: "",
    categoryId: null,
    categoryName: "",
};


function escapeHtml(value) {
    return String(value ?? "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}


function formatDate(value) {
    if (!value) {
        return "";
    }

    const date = new Date(value);

    if (Number.isNaN(date.getTime())) {
        return "";
    }

    return date.toLocaleDateString(undefined, {
        year: "numeric",
        month: "short",
        day: "numeric",
    });
}


function truncateText(value, length = 150) {
    const text = String(value ?? "").trim();

    if (text.length <= length) {
        return text;
    }

    return `${text.slice(0, length).trim()}...`;
}


function extractItems(data) {
    if (Array.isArray(data)) {
        return data;
    }

    if (Array.isArray(data?.items)) {
        return data.items;
    }

    return [];
}


async function loadCurrentUser() {
    if (!getToken()) {
        welcomeMessage.textContent =
            "Browse freely or create an account to join the discussion.";

        profileLink.classList.add("hidden");
        dashboardLink.classList.add("hidden");
        createBlogLink.classList.add("hidden");
        logoutButton.classList.add("hidden");

        loginLink.classList.remove("hidden");
        registerLink.classList.remove("hidden");

        return;
    }

    try {
        state.currentUser = await getCurrentUser();

        welcomeMessage.textContent =
            `Welcome back, ${state.currentUser.username}.`;

        profileLink.classList.remove("hidden");
        logoutButton.classList.remove("hidden");

        loginLink.classList.add("hidden");
        registerLink.classList.add("hidden");

        if (state.currentUser.role === "admin") {
            dashboardLink.classList.remove("hidden");
            createBlogLink.classList.remove("hidden");
        } else {
            dashboardLink.classList.add("hidden");
            createBlogLink.classList.add("hidden");
        }
    } catch (error) {
        removeToken();
        state.currentUser = null;

        welcomeMessage.textContent =
            "Browse freely or create an account to join the discussion.";

        profileLink.classList.add("hidden");
        dashboardLink.classList.add("hidden");
        createBlogLink.classList.add("hidden");
        logoutButton.classList.add("hidden");

        loginLink.classList.remove("hidden");
        registerLink.classList.remove("hidden");
    }
}


function createCategoryButton(category) {
    const button = document.createElement("button");

    button.type = "button";
    button.className = "category-chip";
    button.dataset.categoryId = category.id;
    button.dataset.categoryName = category.name;
    button.textContent = category.name;

    if (
        String(state.categoryId) ===
        String(category.id)
    ) {
        button.classList.add("active");
    }

    return button;
}


async function loadCategories() {
    categoriesMessage.textContent =
        "Loading categories...";

    categoriesContainer.innerHTML = "";

    try {
        const data = await apiRequest("/categories");
        const categories = extractItems(data);

        if (categories.length === 0) {
            categoriesMessage.textContent =
                "No categories are available yet.";

            return;
        }

        categoriesMessage.textContent = "";

        categories.forEach((category) => {
            categoriesContainer.appendChild(
                createCategoryButton(category)
            );
        });
    } catch (error) {
        categoriesMessage.textContent =
            error.message;
    }
}


function createFeaturedBlog(blog) {
    const article = document.createElement("article");

    article.className = "featured-blog-card";

    const imageHtml = blog.image_url
        ? `
            <a
                class="featured-image-wrapper"
                href="blog.html?id=${blog.id}"
            >
                <img
                    class="featured-image"
                    src="${API_BASE_URL}${blog.image_url}"
                    alt="${escapeHtml(blog.title)}"
                >
            </a>
        `
        : `
            <a
                class="featured-image-wrapper featured-placeholder"
                href="blog.html?id=${blog.id}"
            >
                <span>Featured story</span>
            </a>
        `;

    article.innerHTML = `
        ${imageHtml}

        <div class="featured-content">
            <span class="blog-category-badge">
                ${escapeHtml(
                    blog.category?.name || "Uncategorized"
                )}
            </span>

            <h3>
                <a href="blog.html?id=${blog.id}">
                    ${escapeHtml(blog.title)}
                </a>
            </h3>

            <p>
                ${escapeHtml(
                    truncateText(blog.content, 230)
                )}
            </p>

            <div class="blog-card-footer">
                <span>
                    By
                    ${escapeHtml(
                        blog.author?.username || "Unknown"
                    )}
                </span>

                <span>
                    ${formatDate(blog.created_at)}
                </span>

                <span>
                    ${blog.view_count ?? 0} views
                </span>
            </div>

            <a
                class="read-more-link"
                href="blog.html?id=${blog.id}"
            >
                Read featured article →
            </a>
        </div>
    `;

    return article;
}


function createBlogCard(blog) {
    const article = document.createElement("article");

    article.className = "modern-blog-card";

    const imageHtml = blog.image_url
        ? `
            <a
                class="blog-card-image-link"
                href="blog.html?id=${blog.id}"
            >
                <img
                    class="blog-card-image"
                    src="${API_BASE_URL}${blog.image_url}"
                    alt="${escapeHtml(blog.title)}"
                    loading="lazy"
                >
            </a>
        `
        : `
            <a
                class="blog-card-image-link blog-card-placeholder"
                href="blog.html?id=${blog.id}"
            >
                <span>Blog article</span>
            </a>
        `;

    article.innerHTML = `
        ${imageHtml}

        <div class="modern-blog-content">
            <div class="blog-card-top">
                <span class="blog-category-badge">
                    ${escapeHtml(
                        blog.category?.name || "Uncategorized"
                    )}
                </span>

                <span class="blog-view-count">
                    ${blog.view_count ?? 0} views
                </span>
            </div>

            <h3>
                <a href="blog.html?id=${blog.id}">
                    ${escapeHtml(blog.title)}
                </a>
            </h3>

            <p class="blog-excerpt">
                ${escapeHtml(
                    truncateText(blog.content)
                )}
            </p>

            <div class="blog-card-footer">
                <span>
                    By
                    ${escapeHtml(
                        blog.author?.username || "Unknown"
                    )}
                </span>

                <span>
                    ${formatDate(blog.created_at)}
                </span>
            </div>

            <a
                class="read-more-link"
                href="blog.html?id=${blog.id}"
            >
                Read article →
            </a>
        </div>
    `;

    return article;
}


function updateActiveCategory() {
    const buttons =
        categoriesContainer.querySelectorAll(
            "[data-category-id]"
        );

    buttons.forEach((button) => {
        const isActive =
            String(button.dataset.categoryId) ===
            String(state.categoryId);

        button.classList.toggle(
            "active",
            isActive
        );
    });

    clearCategoryButton.classList.toggle(
        "hidden",
        !state.categoryId
    );
}


function updateSectionTitle() {
    if (state.search && state.categoryName) {
        articlesTitle.textContent =
            `Results for "${state.search}" in ${state.categoryName}`;

        return;
    }

    if (state.search) {
        articlesTitle.textContent =
            `Results for "${state.search}"`;

        return;
    }

    if (state.categoryName) {
        articlesTitle.textContent =
            `${state.categoryName} articles`;

        return;
    }

    articlesTitle.textContent =
        "Recent articles";
}


function updatePagination() {
    if (state.totalPages <= 1) {
        pagination.classList.add("hidden");
        return;
    }

    pagination.classList.remove("hidden");

    paginationMessage.textContent =
        `Page ${state.page} of ${state.totalPages}`;

    previousPageButton.disabled =
        state.page <= 1;

    nextPageButton.disabled =
        state.page >= state.totalPages;
}


async function loadBlogs() {
    blogsLoading.classList.remove("hidden");
    blogsEmpty.classList.add("hidden");
    blogsMessage.textContent = "";
    blogsContainer.innerHTML = "";
    featuredBlogContainer.innerHTML = "";
    featuredSection.classList.add("hidden");
    pagination.classList.add("hidden");

    updateSectionTitle();

    const query = new URLSearchParams({
        page: String(state.page),
        page_size: String(state.pageSize),
    });

    if (state.search) {
        query.set("search", state.search);
    }

    if (state.categoryId) {
        query.set(
            "category_id",
            String(state.categoryId)
        );
    }

    try {
        const data = await apiRequest(
            `/blogs?${query.toString()}`
        );

        const blogs = extractItems(data);

        const totalItems =
            data?.total_items ?? blogs.length;

        state.totalPages =
            data?.total_pages ??
            (blogs.length > 0 ? 1 : 0);

        articlesCount.textContent =
            `${totalItems} ${
                totalItems === 1
                    ? "article"
                    : "articles"
            }`;

        blogsLoading.classList.add("hidden");

        if (blogs.length === 0) {
            blogsEmpty.classList.remove("hidden");
            updatePagination();
            return;
        }

        const [featuredBlog, ...remainingBlogs] =
            blogs;

        if (state.page === 1 && featuredBlog) {
            featuredSection.classList.remove(
                "hidden"
            );

            featuredBlogContainer.appendChild(
                createFeaturedBlog(featuredBlog)
            );
        }

        const blogsForGrid =
            state.page === 1
                ? remainingBlogs
                : blogs;

        blogsForGrid.forEach((blog) => {
            blogsContainer.appendChild(
                createBlogCard(blog)
            );
        });

        updatePagination();
    } catch (error) {
        blogsLoading.classList.add("hidden");

        blogsMessage.textContent =
            error.message;
    }
}


function submitSearch() {
    state.search =
        searchInput.value.trim();

    state.page = 1;

    loadBlogs();
}


searchButton.addEventListener(
    "click",
    submitSearch
);


searchInput.addEventListener(
    "keydown",
    (event) => {
        if (event.key === "Enter") {
            submitSearch();
        }
    }
);


categoriesContainer.addEventListener(
    "click",
    (event) => {
        const button = event.target.closest(
            "[data-category-id]"
        );

        if (!button) {
            return;
        }

        state.categoryId =
            button.dataset.categoryId;

        state.categoryName =
            button.dataset.categoryName;

        state.page = 1;

        updateActiveCategory();
        loadBlogs();
    }
);


clearCategoryButton.addEventListener(
    "click",
    () => {
        state.categoryId = null;
        state.categoryName = "";
        state.page = 1;

        updateActiveCategory();
        loadBlogs();
    }
);


previousPageButton.addEventListener(
    "click",
    () => {
        if (state.page <= 1) {
            return;
        }

        state.page -= 1;

        loadBlogs();

        window.scrollTo({
            top: 500,
            behavior: "smooth",
        });
    }
);


nextPageButton.addEventListener(
    "click",
    () => {
        if (state.page >= state.totalPages) {
            return;
        }

        state.page += 1;

        loadBlogs();

        window.scrollTo({
            top: 500,
            behavior: "smooth",
        });
    }
);


logoutButton.addEventListener(
    "click",
    logoutUser
);


async function initializePage() {
    currentYear.textContent =
        new Date().getFullYear();

    await Promise.all([
        loadCurrentUser(),
        loadCategories(),
    ]);

    await loadBlogs();
}


initializePage();