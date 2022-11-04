var md = null;

function send() {
    let to = $("#to").val();
    let message = $("#content").val();
    to = to.split(";").map(x => x.trim()).filter(x => x.length > 0);
    console.log(to);

    $.ajax({
        url: "/api/new",
        type: "POST",
        data: JSON.stringify({ to: to, message: message }),
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        success: function () {
            alert("success");
        },
        error: function (data) {
            if(data.status == 201){
                window.location.replace("/");
                return;
            }
            $("#error").show();
            $("#error").text(data.responseText);
        }
    });
}

function updatePreview(value) {
    let clean = DOMPurify.sanitize(value, { USE_PROFILES: { html: true } });
    $("#preview").html(md.render(clean));
}

$().ready(function () {
    md = window.markdownit();
    $("#error").hide();
    $("#send").click(send);
    $("#content").on("input", function () {
        updatePreview($(this).val());
    });
});