let firstCall = true;

async function getStatus() {
    const response = await fetch("/status");
    const jsonData = await response.json();

    document.getElementById("t").innerHTML = parseFloat(jsonData.temperature).toFixed(2);
    document.getElementById("h").innerHTML = parseFloat(jsonData.humidity).toFixed(2);
    document.getElementById("clock").innerHTML = new Date(jsonData.current_datetime).toISOString();
    document.getElementById("master").innerHTML = jsonData.master ? "Vklopljeno" : "Izklopljeno";
    document.getElementById("door").innerHTML = jsonData.door ? "Odprta" : "Zaprta";
    document.getElementById("light").innerHTML = jsonData.light ? "Prižgana" : "Ugasnjena";

    document.getElementById("schedule_sunrise").innerHTML = new Date(jsonData.schedule_sunrise).toISOString();
    document.getElementById("schedule_sunset").innerHTML = new Date(jsonData.schedule_sunset).toISOString();
    if (firstCall) {
        document.getElementById("schedule_city").value = jsonData.schedule_city;
        document.getElementById("schedule_door_open").checked = jsonData.schedule_door_open;
        document.getElementById("schedule_door_close").checked = jsonData.schedule_door_close;
        document.getElementById("schedule_door_open_offset").value = jsonData.schedule_door_open_offset;
        document.getElementById("schedule_door_close_offset").value = jsonData.schedule_door_close_offset;
        firstCall=false;
    }
}

// Fetch status every 2 seconds.
window.addEventListener("load", (event) => {
    setInterval(getStatus, 2000);
});