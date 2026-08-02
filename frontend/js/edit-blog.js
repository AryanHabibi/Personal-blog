const pageUserMessage =
    document.getElementById("page-user-message");

const pageMessage =
    document.getElementById("page-message");

const editBlogSection =
    document.getElementById("edit-blog-section");

const editBlogForm =
    document.getElementById("edit-blog-form");

const editBlogMessage =
    document.getElementById("edit-blog-message");

const updateBlogButton =
    document.getElementById("update-blog-button");

const titleInput =
    document.getElementById("title");

const contentInput =
    document.getElementById("content");

const categorySelect =
    document.getElementById("category-id");

const imageInput =
    document.getElementById("image");

const currentImageSection =
    document.getElementById("current-image-section");

const currentImage =
    document.getElementById("current-image");

const viewBlogLink =
    document.getElementById("view-blog-link");

const logoutButton =
    document.getElementById("logout-button");


const queryParameters =
    new URLSearchParams(window.location.search);

const blogId =
    queryParameters.get("id");


let currentBlog = null;


function extractItems(data) {
    if (Array.isArray(data)) {
        return data;
    }

    if (Array.isArray(data?.items)) {
        return data.items;
    }

    return [];
}


async function requireAdmin() {
    try {
        const user = await getCurrentUser();

        if (user.role !== "admin") {
            window.location.href = "index.html";
            return null;
        }

        pageUserMessage.textContent =
            `Signed in as ${user.username}`;

        return user;
    } catch (error) {
        removeToken();
        window.location.href = "login.html";
        return null;
    }
}


async function loadCategories(selectedCategoryId) {
    const data = await apiRequest("/categories");
    const categories = extractItems(data);

    categorySelect.innerHTML =
        '<option value="">Choose a category</option>';

    categories.forEach((category) => {
        const option = document.createElement("option");

        option.value = String(category.id);
        option.textContent = category.name;

        if (
            selectedCategoryId !== null &&
            String(category.id) === String(selectedCategoryId)
        ) {
            option.selected = true;
        }

        categorySelect.appendChild(option);
    });

    if (categories.length === 0) {
        categorySelect.innerHTML =
            '<option value="">No categories available</option>';

        updateBlogButton.disabled = true;
    }
}


async function loadBlog() {
    if (!blogId) {
        pageMessage.textContent =
            "No blog ID was provided.";

        return;
    }

    try {
        currentBlog = await apiRequest(`/blogs/${blogId}`);

        titleInput.value = currentBlog.title;
        contentInput.value = currentBlog.content;

        await loadCategories(currentBlog.category_id);

        if (currentBlog.image_url) {
            currentImage.src =
                `${API_BASE_URL}${currentBlog.image_url}`;

            currentImageSection.classList.remove("hidden");
        }

        viewBlogLink.href =
            `blog.html?id=${currentBlog.id}`;

        viewBlogLink.classList.remove("hidden");

        pageMessage.textContent = "";
        editBlogSection.classList.remove("hidden");
    } catch (error) {
        pageMessage.textContent = error.message;
    }
}


editBlogForm.addEventListener(
    "submit",
    async (event) => {
        event.preventDefault();

        editBlogMessage.textContent = "";
        updateBlogButton.disabled = true;
        updateBlogButton.textContent = "Saving...";

        const formData = new FormData();

        formData.append(
            "title",
            titleInput.value.trim()
        );

        formData.append(
            "content",
            contentInput.value.trim()
        );

        formData.append(
            "category_id",
            categorySelect.value
        );

        if (imageInput.files.length > 0) {
            formData.append(
                "image",
                imageInput.files[0]
            );
        }

        try {
            const updatedBlog = await apiRequest(
                `/blogs/${blogId}`,
                {
                    method: "PUT",
                    body: formData,
                    authenticated: true,
                    isFormData: true,
                }
            );

            editBlogMessage.style.color = "#16a34a";
            editBlogMessage.textContent =
                "Blog updated successfully.";

            setTimeout(() => {
                window.location.href =
                    `blog.html?id=${updatedBlog.id}`;
            }, 700);
        } catch (error) {
            editBlogMessage.style.color = "#dc2626";
            editBlogMessage.textContent = error.message;
        } finally {
            updateBlogButton.disabled = false;
            updateBlogButton.textContent = "Save changes";
        }
    }
);


logoutButton.addEventListener(
    "click",
    logoutUser
);


async function initializeEditPage() {
    const admin = await requireAdmin();

    if (admin) {
        await loadBlog();
    }
}


initializeEditPage();