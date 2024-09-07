document.getElementById("library-log-btn").addEventListener("click", function() {
    document.getElementById("library-log").style.display = "block";
    document.getElementById("exit-log").style.display = "none";
});

document.getElementById("exit-log-btn").addEventListener("click", function() {
    document.getElementById("exit-log").style.display = "block";
    document.getElementById("library-log").style.display = "none";
});
