var md = window.markdownit();

function renderMessage() {
    let id = window.location.pathname.split("/")[2];

    $.get("/api/messages/" + id, function (data) {
        let clean = DOMPurify.sanitize(data.message, { USE_PROFILES: { html: true } });
        $("#message").html(md.render(clean));
    });
}

function deleteMessage() {
    let id = window.location.pathname.split("/")[2];

    $.ajax({
        url: "/api/messages/" + id,
        type: "DELETE",
        success: function () {
            window.location.replace("/");
        },
        error: function (data) {
            
        }
    });
}

function hardDeleteMessage() {
    let id = window.location.pathname.split("/")[2];
    
    $.ajax({
        url: "/api/messages/hard/" + id,
        type: "DELETE",
        success: function () {
            window.location.replace("/");
        },
        error: function (data) {
            console.error(data.responseText);
        }
    });
}

function isOwner(cb) {
    let id = window.location.pathname.split("/")[2];
    $.get("/api/messages/owned/" + id , function (data) {
        if (data == "True") {
            cb(true);
        } else {
            cb(false);
        }
    });
}


$().ready(function () {
    renderMessage();
    $("#delete").click(deleteMessage);
    $("#hard-delete").click(hardDeleteMessage);

    isOwner(function (isOwner) {
        if (isOwner) {
            $("#delete").show();
            $("#hard-delete").show();
        } else {
            $("#delete").show();
            $("#delete").text("Delete");
            $("#hard-delete").hide();
        }
    });
});
