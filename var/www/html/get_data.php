<?php
header("Content-Type: application/json");

// database settings
$host = "localhost";
$user = "sht35user";
$pass = "By8Hq2Ze";
$db = "sht35db";

// connect
$conn = new mysqli($host, $user, $pass, $db);

if ($conn->connect_error) {
    die(json_encode(["error" => $conn->connect_error]));
}

// fetch last 100 readings
$sql = "SELECT timestamp, temperature, humidity FROM readings ORDER BY id DESC LIMIT 100";
$res = $conn->query($sql);

$data = [];
while ($row = $res->fetch_assoc()) {
    $data[] = $row;
}

echo json_encode($data);
$conn->close();
?>

