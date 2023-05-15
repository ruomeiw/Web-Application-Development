"use strict"

function loadPosts() {
    let currentPage = window.location.href
    console.log("current page is: " + currentPage)
    $.ajax({
        url: (currentPage.includes("global") || currentPage == "http://3.80.210.145/") ? "socialnetwork/get-global" : "socialnetwork/get-follower",
        dataType: "json",
        success: updateList,
        error: updateError
    });
}

function updateError(xhr) {
    if (xhr.status == 0) {
        displayError("Cannot connect to server")
        return
    }

    if (!xhr.getResponseHeader('content-type') == 'application/json') {
        displayError("Received status=" + xhr.status)
        return
    }

    let response = JSON.parse(xhr.responseText)
    if (response.hasOwnProperty('error')) {
        displayError(response.error)
        return
    }

    displayError(response)
}

function displayError(message) {
    $("#error").html(message);
}

function updateList(response) {
    $(response['posts']).each(function () {
        let currentPostID = this.id
        let post_comments = []
        $(response['comments']).each(function () {
            let currentCommentID = "id_comment_div_" + this.id
            if (document.getElementById(currentCommentID) == null) {
                if (this.post_id == currentPostID) {
                    post_comments.push(this)
                }
            }
        })
        $("#my-posts-go-here").append(makePostHTML(this, post_comments))
    })
}

function makeNewCommentBoxHTML(post) {
    let commentInputBoxHTML = document.createElement("div")
    commentInputBoxHTML.setAttribute("class", "id_comment_div")

    let commentLabel = document.createElement("label")
    commentLabel.innerHTML = "Comment: "
    commentLabel.setAttribute("for", "id_comment_input_text_" + post.id)

    let commentInput = document.createElement("input")
    commentInput.setAttribute("type", "text")
    commentInput.setAttribute("id", "id_comment_input_text_" + post.id)
    commentInput.setAttribute("class", "id_comment_input_text")
    commentInput.setAttribute("name", "comment_text")

    let commentSubmitButton = document.createElement("button")
    commentSubmitButton.setAttribute("type", "submit")
    commentSubmitButton.setAttribute("id", "id_comment_button_" + post.id)
    commentSubmitButton.setAttribute("class", "id_comment_button")
    commentSubmitButton.innerHTML = "Submit"
    commentSubmitButton.setAttribute("onClick", "addComment(this.id)")


    commentInputBoxHTML.append(commentLabel, commentInput, commentSubmitButton)

    return commentInputBoxHTML
}

function makeProfileLinkHTML(post) {
    let profileLinkHTML = document.createElement("a")
    profileLinkHTML.setAttribute("href", "other/" + post.user_id)
    profileLinkHTML.setAttribute("id", "id_post_profile_" + post.id)
    profileLinkHTML.setAttribute("class", "id_post_profile")
    profileLinkHTML.innerHTML = post.fname + " " + post.lname

    return profileLinkHTML
}

function makeCommentProfileLinkHTML(comment) {
    let profileLinkHTML = document.createElement("a")
    profileLinkHTML.setAttribute("href", "other/" + comment.user_id)
    profileLinkHTML.setAttribute("id", "id_comment_profile_" + comment.id)
    profileLinkHTML.setAttribute("class", "id_comment_profile")
    profileLinkHTML.innerHTML = comment.fname + " " + comment.lname

    return profileLinkHTML
}

function makeDateTimeHTML(post) {
    let dateTimeHTML = document.createElement("span")
    dateTimeHTML.setAttribute("class", "id_post_date_time")
    dateTimeHTML.setAttribute("id", "id_post_date_time_" + post.id)
    dateTimeHTML.innerHTML = post.date_time

    return dateTimeHTML
}

function makeCommentDateTimeHTML(comment) {
    let dateTimeHTML = document.createElement("span")
    dateTimeHTML.setAttribute("class", "id_comment_date_time")
    dateTimeHTML.setAttribute("id", "id_comment_date_time_" + comment.id)
    dateTimeHTML.innerHTML = comment.date_time

    return dateTimeHTML
}

function makePostHTML(post, post_comments) {
    let currentPostHTMLID = "id_post_div_" + post.id
    let postHTML
    if (document.getElementById(currentPostHTMLID) == null) {
        postHTML = document.createElement("div")
    } else {
        postHTML = document.getElementById(currentPostHTMLID)
    }

    let postTextHTML = document.createElement("span")
    postTextHTML.setAttribute("class", "id_post_text")
    postTextHTML.setAttribute("id", "id_post_text_" + post.id)
    postTextHTML.innerHTML = post.text

    postHTML.setAttribute("class", "id_post_div")
    postHTML.setAttribute("id", currentPostHTMLID)

    if (document.getElementById(currentPostHTMLID) == null) {
        let postCommentHTML = document.createElement("div")
        postCommentHTML.setAttribute("id", "my-comments-go-here-for-post-" + post.id)
        postCommentHTML.setAttribute("class", "my-comments-go-here")

        postCommentHTML = makeCommentHTML(postCommentHTML, post_comments)
        postHTML.append("Post by ", makeProfileLinkHTML(post), " - ", postTextHTML, " - ", makeDateTimeHTML(post), postCommentHTML, makeNewCommentBoxHTML(post))
    } else {
        let postCommentHTML = document.createElement("div")
        postCommentHTML.setAttribute("class", "id_comment_div")
        let temp = makeCommentHTML(postCommentHTML, post_comments)
        postCommentHTML = temp
        if (postCommentHTML.innerText != '') {
            postHTML.children[3].insertBefore(postCommentHTML, postHTML.children[3].firstChild)
        }
    }
    return postHTML
}

function makeCommentHTML(postCommentHTML, post_comments) {
    for (let i = 0; i < post_comments.length; i++) {
        let currentComment = post_comments[i]
        let currentCommentID = "id_comment_div_" + currentComment.id
        if (document.getElementById(currentCommentID) == null) {
            let commentTextHTML = document.createElement("span")
            commentTextHTML.setAttribute("id", "id_comment_text_" + currentComment.id)
            commentTextHTML.setAttribute("class", "id_comment_text")
            commentTextHTML.innerHTML = currentComment.comment_text

            let commentHTML = document.createElement("div")
            commentHTML.setAttribute("id", "id_comment_div_" + currentComment.id)
            commentHTML.setAttribute("class", "id_comment_div")
            commentHTML.append("Comment by ", makeCommentProfileLinkHTML(currentComment), " - ", commentTextHTML, " -- ", makeCommentDateTimeHTML(currentComment))

            if (postCommentHTML.classList.contains("id_comment_div")) {
                postCommentHTML.setAttribute("id", "id_comment_div_" + currentComment.id)
                postCommentHTML.append("Comment by ", makeCommentProfileLinkHTML(currentComment), " - ", commentTextHTML, " -- ", makeCommentDateTimeHTML(currentComment))
            } else {
                $(postCommentHTML).append(commentHTML)
            }
        }
    }
    return postCommentHTML
}

function addComment(button_id) {
    let post_id = button_id.match(/(\d+)/)[0]
    let commentTextElement = document.getElementById("id_comment_input_text_" + post_id)
    let commentTextValue = commentTextElement.value

    $.ajax({
        url: "socialnetwork/add-comment",
        type: "POST",
        data: "comment_text=" + commentTextValue + "&post_id=" + post_id + "&csrfmiddlewaretoken=" + getCSRFToken(),
        dataType: "json",
        success: updateList,
        error: updateError
    });

    commentTextElement.value = ""
}

function sanitize(s) {
    return s.replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
}

function getCSRFToken() {
    let cookies = document.cookie.split(";")
    for (let i = 0; i < cookies.length; i++) {
        let c = cookies[i].trim()
        if (c.startsWith("csrftoken=")) {
            return c.substring("csrftoken=".length, c.length)
        }
    }
    return "unknown"
}