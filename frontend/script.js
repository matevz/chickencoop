async function getStatus() {
    const response = await fetch("/status");
    const jsonData = await response.json();

    document.getElementById("t").innerHTML = parseFloat(jsonData.temperature).toFixed(2);
    document.getElementById("h").innerHTML = parseFloat(jsonData.humidity).toFixed(2);
    document.getElementById("clock").innerHTML = new Date(jsonData.current_datetime).toISOString();
    document.getElementById("master").innerHTML = jsonData.master ? "Vklopljeno" : "Izklopljeno";
    document.getElementById("door").innerHTML = jsonData.door ? "Odprta" : "Zaprta";
    document.getElementById("light").innerHTML = jsonData.light ? "Prižgana" : "Ugasnjena";
}

// Fetch status every 2 seconds.
window.addEventListener("load", (event) => {
    setInterval(getStatus, 2000);
});