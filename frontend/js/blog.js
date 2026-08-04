const blogPageUser =
    document.getElementById("blog-page-user");

const dashboardLink =
    document.getElementById("dashboard-link");

const logoutButton =
    document.getElementById("logout-button");

const blogMessage =
    document.getElementById("blog-message");

const blogDetails =
    document.getElementById("blog-details");

const blogImage =
    document.getElementById("blog-image");

const blogCategory =
    document.getElementById("blog-category");

const blogAuthor =
    document.getElementById("blog-author");

const blogViews =
    document.getElementById("blog-views");

const blogTitle =
    document.getElementById("blog-title");

const blogDate =
    document.getElementById("blog-date");

const blogContent =
    document.getElementById("blog-content");

const commentForm =
    document.getElementById("comment-form");

const commentContent =
    document.getElementById("comment-content");

const commentButton =
    document.getElementById("comment-button");

const commentMessage =
    document.getElementById("comment-message");

const commentCounter =
    document.getElementById("comment-counter");

const commentsMessage =
    document.getElementById("comments-message");

const commentsContainer =
    document.getElementById("comments-container");


const queryParameters =
    new URLSearchParams(window.location.search);

const blogId =
    queryParameters.get("id");


let currentUser = null;


function formatDate(value) {
    if (!value) {
        return "";
    }

    const date = new Date(value);

    if (Number.isNaN(date.getTime())) {
        return "";
    }

    return date.toLocaleString();
}


function escapeHtml(value) {
    return String(value ?? "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}


async function loadCurrentUserForPage() {
    if (!getToken()) {
        blogPageUser.textContent =
            "Browsing as guest";

        commentForm.classList.add("hidden");
        logoutButton.classList.add("hidden");

        return;
    }

    try {
        currentUser = await getCurrentUser();

        blogPageUser.textContent =
            `Signed in as ${currentUser.username}`;

        logoutButton.classList.remove("hidden");

        if (currentUser.role === "admin") {
            dashboardLink.classList.remove("hidden");
        }
    } catch (error) {
        removeToken();

        currentUser = null;

        blogPageUser.textContent =
            "Browsing as guest";

        commentForm.classList.add("hidden");
        logoutButton.classList.add("hidden");
        dashboardLink.classList.add("hidden");
    }
}


async function loadBlog() {
    if (!blogId) {
        blogMessage.textContent =
            "No blog ID was provided.";

        return;
    }

    try {
        const blog = await apiRequest(
            `/blogs/${blogId}`
        );

        blogTitle.textContent =
            blog.title;

        blogAuthor.textContent =
            `By ${blog.author?.username || "Unknown author"}`;

        blogCategory.textContent =
            blog.category?.name || "Uncategorized";

        blogViews.textContent =
            `${blog.view_count ?? 0} views`;

        blogDate.textContent =
            `Published ${formatDate(blog.created_at)}`;

        blogContent.textContent =
            blog.content;

        if (blog.image_url) {
            blogImage.src =
                `${API_BASE_URL}${blog.image_url}`;

            blogImage.alt =
                blog.title;

            blogImage.classList.remove("hidden");
        } else {
            blogImage.classList.add("hidden");
            blogImage.removeAttribute("src");
        }

        blogMessage.textContent = "";
        blogDetails.classList.remove("hidden");

        document.title =
            `${blog.title} | Blog Management`;
    } catch (error) {
        blogDetails.classList.add("hidden");
        blogMessage.textContent =
            error.message;
    }
}


function canManageComment(comment) {
    if (!currentUser) {
        return false;
    }

    const isOwner =
        comment.user_id === currentUser.id;

    const isAdmin =
        currentUser.role === "admin";

    return isOwner || isAdmin;
}


function createCommentElement(comment) {
    const article =
        document.createElement("article");

    article.className =
        "comment-card";

    const manageButtons =
        canManageComment(comment)
            ? `
                <div class="comment-actions">
                    <button
                        class="small-button"
                        data-edit-comment="${comment.id}"
                        type="button"
                    >
                        Edit
                    </button>

                    <button
                        class="danger-button"
                        data-delete-comment="${comment.id}"
                        type="button"
                    >
                        Delete
                    </button>
                </div>
            `
            : "";

    article.innerHTML = `
        <div class="comment-header">
            <div>
                <strong>
                    ${escapeHtml(
                        comment.user?.username ||
                        "Unknown user"
                    )}
                </strong>

                <p>
                    ${escapeHtml(
                        formatDate(comment.created_at)
                    )}
                </p>
            </div>

            ${manageButtons}
        </div>

        <p class="comment-text">
            ${escapeHtml(comment.content)}
        </p>
    `;

    return article;
}


async function loadComments() {
    if (!blogId) {
        return;
    }

    commentsMessage.textContent =
        "Loading comments...";

    commentsContainer.innerHTML = "";

    try {
        const comments = await apiRequest(
            `/comments/blog/${blogId}`
        );

        if (
            !Array.isArray(comments) ||
            comments.length === 0
        ) {
            commentsMessage.textContent =
                "No comments yet.";

            return;
        }

        commentsMessage.textContent = "";

        comments.forEach((comment) => {
            commentsContainer.appendChild(
                createCommentElement(comment)
            );
        });
    } catch (error) {
        commentsMessage.textContent =
            error.message;
    }
}


function updateCommentCounter() {
    commentCounter.textContent =
        `${commentContent.value.length} / 1000`;
}


commentContent.addEventListener(
    "input",
    updateCommentCounter
);


commentForm.addEventListener(
    "submit",
    async (event) => {
        event.preventDefault();

        if (!currentUser) {
            window.location.href =
                "login.html";

            return;
        }

        const content =
            commentContent.value.trim();

        if (!content) {
            commentMessage.style.color =
                "#dc2626";

            commentMessage.textContent =
                "Comment cannot be empty.";

            return;
        }

        commentButton.disabled = true;
        commentButton.textContent =
            "Posting...";

        commentMessage.textContent = "";

        const formData =
            new FormData();

        formData.append(
            "content",
            content
        );

        try {
            await apiRequest(
                `/comments/blog/${blogId}`,
                {
                    method: "POST",
                    body: formData,
                    authenticated: true,
                    isFormData: true,
                }
            );

            commentContent.value = "";
            updateCommentCounter();

            commentMessage.style.color =
                "#16a34a";

            commentMessage.textContent =
                "Comment added successfully.";

            await loadComments();
        } catch (error) {
            commentMessage.style.color =
                "#dc2626";

            commentMessage.textContent =
                error.message;
        } finally {
            commentButton.disabled = false;
            commentButton.textContent =
                "Add comment";
        }
    }
);


commentsContainer.addEventListener(
    "click",
    async (event) => {
        const editButton =
            event.target.closest(
                "[data-edit-comment]"
            );

        const deleteButton =
            event.target.closest(
                "[data-delete-comment]"
            );

        if (editButton) {
            const commentId =
                editButton.dataset.editComment;

            const currentCard =
                editButton.closest(
                    ".comment-card"
                );

            const currentText =
                currentCard
                    ?.querySelector(
                        ".comment-text"
                    )
                    ?.textContent
                    ?.trim() || "";

            const updatedContent =
                window.prompt(
                    "Enter the updated comment:",
                    currentText
                );

            if (!updatedContent?.trim()) {
                return;
            }

            const formData =
                new FormData();

            formData.append(
                "content",
                updatedContent.trim()
            );

            editButton.disabled = true;
            editButton.textContent =
                "Saving...";

            try {
                await apiRequest(
                    `/comments/${commentId}`,
                    {
                        method: "PUT",
                        body: formData,
                        authenticated: true,
                        isFormData: true,
                    }
                );

                await loadComments();
            } catch (error) {
                alert(error.message);
            }
        }

        if (deleteButton) {
            const commentId =
                deleteButton.dataset.deleteComment;

            const confirmed =
                window.confirm(
                    "Are you sure you want to delete this comment?"
                );

            if (!confirmed) {
                return;
            }

            deleteButton.disabled = true;
            deleteButton.textContent =
                "Deleting...";

            try {
                await apiRequest(
                    `/comments/${commentId}`,
                    {
                        method: "DELETE",
                        authenticated: true,
                    }
                );

                await loadComments();
            } catch (error) {
                alert(error.message);

                deleteButton.disabled = false;
                deleteButton.textContent =
                    "Delete";
            }
        }
    }
);


logoutButton.addEventListener(
    "click",
    logoutUser
);


async function initializeBlogPage() {
    if (!blogId) {
        blogMessage.textContent =
            "No blog ID was provided.";

        commentsMessage.textContent = "";

        return;
    }

    await loadCurrentUserForPage();

    await Promise.all([
        loadBlog(),
        loadComments(),
    ]);
}


initializeBlogPage();