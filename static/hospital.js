document.querySelector('.sidebar').style.display = "none";
document.querySelector('.Ham-btn').addEventListener("click", () => {
    document.querySelector('.sidebar').classList.remove('sidebarGo');
    setTimeout(() => {
        document.querySelector('.sidebar').style.display = "inline";
    },500);
});

document.querySelector('.close-btn').addEventListener("click", () => {
    document.querySelector('.sidebar').classList.add('sidebarGo');
    document.querySelector('.sidebar').style.display = "inline";
});
