// Placify Theme Manager

const savedTheme = localStorage.getItem("placify-theme");

if (savedTheme) {
    document.documentElement.setAttribute("data-theme", savedTheme);
}

function setTheme(theme) {
    document.documentElement.setAttribute("data-theme", theme);

    localStorage.setItem("placify-theme", theme);
}