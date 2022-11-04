// Borrowed from https://stackoverflow.com/questions/3426404/create-a-hexadecimal-colour-based-on-a-string-with-javascript
var stringToColour = function (str) {
    var hash = 0;
    for (var i = 0; i < str.length; i++) {
        hash = str.charCodeAt(i) + ((hash << 5) - hash);
    }
    var colour = '#';
    for (var i = 0; i < 3; i++) {
        var value = (hash >> (i * 8)) & 0xFF;
        colour += ('00' + value.toString(16)).substr(-2);
    }
    return colour;
}

var blackOrWhite = function (hex) {
    if (hex.indexOf('#') === 0) {
        hex = hex.slice(1);
    }
    // convert 3-digit hex to 6-digits.
    if (hex.length === 3) {
        hex = hex[0] + hex[0] + hex[1] + hex[1] + hex[2] + hex[2];
    }
    if (hex.length !== 6) {
        throw new Error('Invalid HEX color.');
    }
    var r = parseInt(hex.slice(0, 2), 16),
        g = parseInt(hex.slice(2, 4), 16),
        b = parseInt(hex.slice(4, 6), 16);
    return (r * 0.299 + g * 0.587 + b * 0.114) > 186
        ? '#000000'
        : '#FFFFFF';
}

function viewMessage(id) {
    window.location.replace("/message/" + id);
}

function toDateTime(secs) {
    var t = new Date(1970, 0, 1); // Epoch
    t.setSeconds(secs);
    return t;
}

function renderMessage(message) {
    let clean = DOMPurify.sanitize(message.message, { USE_PROFILES: { html: true } });
    iconColor = stringToColour(message.sender);
    let to = message.to.join(", ");
    let time = toDateTime(message.datetime).toLocaleDateString();
    return `
    <div class="message  d-flex text-muted pt-3 align-items-center" onclick="viewMessage(${message.id})">
        <svg class="bd-placeholder-img mb-3 flex-shrink-0 me-2 rounded" width="32" height="32"
            xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Placeholder: 32x32"
            preserveAspectRatio="xMidYMid slice" focusable="false">
            <title>${message["sender"]}</title>
            <rect width="100%" height="100%" fill="${iconColor}"></rect>
            <text x="50%" y="50%" fill="${blackOrWhite(iconColor)}" dominant-baseline="middle" text-anchor="middle">${message["sender"].charAt(0).toUpperCase()}</text>
        </svg>
        <p class="pb-3 mb-0 small lh-sm border-bottom text-truncate w-100">
            <strong class="d-block text-gray-dark">${message["sender"]} -> ${to}</strong>
            ${clean}
        </p>
        <p class="pb-3 mb-0 small ">
            ${time}
        </p>
    </div>
    `
}

function updateMessages() {
    $.get("/api/messages", function (data) {
        $("#inbox").html("");
        data.sort((a,b) => b.datetime - a.datetime).forEach(message => {
            $("#inbox").append(renderMessage(message));
        });
        if (data.length > 0) {
            $("#inbox-no-message").hide();
        } else {
            $("#inbox-no-message").show();
        }
    });

    $.get("/api/messages/sent", function (data) {
        $("#sent").html("");
        data.sort((a,b) => b.datetime - a.datetime).forEach(message => {
            $("#sent").append(renderMessage(message));
        });
        if (data.length > 0) {
            $("#sent-no-message").hide();
        }
        else {
            $("#sent-no-message").show();
        }
    });
}

document.addEventListener("DOMContentLoaded", function () {
    updateMessages();
});

// repeat every 5 seconds
setInterval(updateMessages, 5000);