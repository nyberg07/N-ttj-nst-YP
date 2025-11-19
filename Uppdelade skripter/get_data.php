<?php
header("Content-Type: application/json"); // Sätt content-typ till JSON för att klienten ska veta att vi skickar JSON-data

// databasinställningar
$host = "localhost";           // Databasvärd
$user = "sht35user";           // Databas användarnamn
$pass = "By8Hq2Ze";            // Databas lösenord
$db = "sht35db";               // Databas namn

// anslut till databasen
$conn = new mysqli($host, $user, $pass, $db); // Skapa en ny MySQL-anslutning

if ($conn->connect_error) {                      // Kolla om anslutningen misslyckades
    die(json_encode(["error" => $conn->connect_error])); // Avsluta och skicka felmeddelande som JSON
}

// hämta de senaste 100 mätningarna
$sql = "SELECT timestamp, temperature, humidity FROM readings ORDER BY id DESC LIMIT 100"; // SQL-fråga för senaste 100 rader
$res = $conn->query($sql);                     // Kör SQL-frågan

$data = [];                                    // Skapa tom array för datan
while ($row = $res->fetch_assoc()) {           // Loopar igenom alla rader i resultatet
    $data[] = $row;                            // Lägg till varje rad i arrayen
}

echo json_encode($data);                        // Skicka ut hela datan som JSON
$conn->close();                                 // Stäng databasanslutningen
?>

