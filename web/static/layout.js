const socket = io();
const objContent = document.getElementById("obj-content");
const statusText = document.getElementById("status-text");
const altEl = document.getElementById("alt");
const azEl = document.getElementById("az");
const target = document.getElementById("target");

socket.on("connect", () => {
    console.log("Connected to server");
});

if (!objContent || !statusText || !altEl || !azEl || !target) {
    console.error("Missing DOM elements");
}

socket.on("status_update", (data) => {
    if (data.status === "POINTING") {
        objContent.style.display = "flex";
        target.textContent = `Target: ${data.target}`;
    } else {
        objContent.style.display = "none";
        altEl.textContent = "";
        azEl.textContent = "";
    }

    if (data.established) {
        statusText.textContent = "Established";
    } else {
        statusText.textContent = data.status;
    }
});

socket.on("coord_update", (data) => {
    if (objContent.style.display === "none") return;

    altEl.textContent = `ALT: ${data.alt}°`;
    azEl.textContent = `AZ: ${data.az}°`;
});
