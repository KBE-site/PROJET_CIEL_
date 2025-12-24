const advancedForm = document.getElementById("advanced-form");
const advancedCheckbox = document.getElementById("checkbox-advanced-mode");

if (!advancedForm || !advancedCheckbox) {
    console.error("Advanced elements not found");
}

advancedForm.style.display = "none";

advancedCheckbox.addEventListener("change", () => {
    const enabled = advancedCheckbox.checked;
    advancedForm.style.display = enabled ? "flex" : "none";
});
