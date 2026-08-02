const pageUserMessage =
    document.getElementById("page-user-message");

const createBlogForm =
    document.getElementById("create-blog-form");

const createBlogButton =
    document.getElementById("create-blog-button");

const createBlogMessage =
    document.getElementById("create-blog-message");

const categorySelect =
    document.getElementById("category-id");

const logoutButton =
    document.getElementById("logout-button");


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
    } catch {
        removeToken();
        window.location.href = "login.html";
        return null;
    }
}


async function loadCategories() {
    try {
        const data = await apiRequest("/categories");
        const categories = extractItems(data);

        categorySelect.innerHTML =
            '<option value="">Choose a category</option>';

        categories.forEach((category) => {
            const option = document.createElement("option");

            option.value = category.id;
            option.textContent = category.name;

            categorySelect.appendChild(option);
        });

        if (categories.length === 0) {
            categorySelect.innerHTML =
                '<option value="">No categories available</option>';

            createBlogButton.disabled = true;
        }
    } catch (error) {
        categorySelect.innerHTML =
            '<option value="">Could not load categories</option>';

        createBlogMessage.textContent = error.message;
        createBlogButton.disabled = true;
    }
}


createBlogForm.addEventListener(
    "submit",
    async (event) => {
        event.preventDefault();

        createBlogMessage.textContent = "";
        createBlogButton.disabled = true;
        createBlogButton.textContent = "Creating...";

        const formData = new FormData();

        formData.append(
            "title",
            document.getElementById("title").value.trim()
        );

        formData.append(
            "content",
            document.getElementById("content").value.trim()
        );

        formData.append(
            "category_id",
            categorySelect.value
        );

        const imageInput =
            document.getElementById("image");

        if (imageInput.files.length > 0) {
            formData.append(
                "image",
                imageInput.files[0]
            );
        }

        try {
            const blog = await apiRequest("/blogs", {
                method: "POST",
                body: formData,
                authenticated: true,
                isFormData: true,
            });

            createBlogMessage.style.color = "#16a34a";
            createBlogMessage.textContent =
                "Blog created successfully.";

            setTimeout(() => {
                window.location.href =
                    `blog.html?id=${blog.id}`;
            }, 700);
        } catch (error) {
            createBlogMessage.style.color = "#dc2626";
            createBlogMessage.textContent = error.message;
        } finally {
            createBlogButton.disabled = false;
            createBlogButton.textContent = "Create blog";
        }
    }
);


logoutButton.addEventListener(
    "click",
    logoutUser
);


async function initializePage() {
    const admin = await requireAdmin();

    if (admin) {
        await loadCategories();
    }
}


initializePage();