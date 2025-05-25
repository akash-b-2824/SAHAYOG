<?php
// Connection to both databases
$auth_conn = new mysqli("localhost", "root", "", "auth_db");
$labor_conn = new mysqli("localhost", "root", "", "labor_db");

if ($auth_conn->connect_error || $labor_conn->connect_error) {
    die("Connection failed: " . $auth_conn->connect_error . " / " . $labor_conn->connect_error);
}

// Basic sanitation function
function sanitize($conn, $str) {
    return htmlspecialchars(mysqli_real_escape_string($conn, $str));
}

// Determine user type
$type = isset($_POST['type']) ? $_POST['type'] : '';

if ($type === 'farmer') {
    // --- Farmer registration ---
    $name = sanitize($auth_conn, $_POST['name']);
    $adhar = sanitize($auth_conn, $_POST['adhar']);
    $land_size = floatval($_POST['land_size']);
    $land_type = sanitize($auth_conn, $_POST['land_type']);
    $phone = sanitize($auth_conn, $_POST['phone']);
    $password = sanitize($auth_conn, $_POST['password']);
    $re_password = sanitize($auth_conn, $_POST['re_password']);
    $location = sanitize($auth_conn, $_POST['location']);

    if ($password !== $re_password) {
        die("Passwords do not match.");
    }

    $hashed_password = password_hash($password, PASSWORD_DEFAULT);

    $query = "INSERT INTO farmers (name, adhar, land_size, land_type, phone, password, location)
              VALUES ('$name', '$adhar', $land_size, '$land_type', '$phone', '$hashed_password', '$location')";

    if ($auth_conn->query($query) === TRUE) {
        echo "✅ Farmer registered successfully!";
    } else {
        echo "❌ Error: " . $auth_conn->error;
    }

} elseif ($type === 'worker') {
    // --- Laborer registration ---
    $name = sanitize($auth_conn, $_POST['name']);
    $adhar = sanitize($auth_conn, $_POST['adhar']);
    $phone = sanitize($auth_conn, $_POST['phone']);
    $password = sanitize($auth_conn, $_POST['password']);
    $re_password = sanitize($auth_conn, $_POST['re_password']);
    $skills = isset($_POST['skills']) ? $_POST['skills'] : [];
    $age = intval($_POST['age']);
    $gender = sanitize($auth_conn, $_POST['gender']);
    $availability = sanitize($auth_conn, $_POST['availability']);
    $latitude = sanitize($auth_conn, $_POST['latitude']);
    $longitude = sanitize($auth_conn, $_POST['longitude']);
    $language = sanitize($auth_conn, $_POST['language']);
    $experience = intval($_POST['experience']);

    if ($password !== $re_password) {
        die("Passwords do not match.");
    }

    $skills_str = implode(",", array_map(fn($s) => sanitize($auth_conn, $s), $skills));
    $hashed_password = password_hash($password, PASSWORD_DEFAULT);

    // Insert into auth_db.workers
    $query1 = "INSERT INTO workers (name, adhar, phone, password, skills, age, gender, availability, latitude, longitude, language, experience)
               VALUES ('$name', '$adhar', '$phone', '$hashed_password', '$skills_str', $age, '$gender', '$availability', '$latitude', '$longitude', '$language', $experience)";

    // Insert into labor_db.labors
    $query2 = "INSERT INTO labors (name, adhar, phone, skills, age, gender, availability, latitude, longitude, language, experience)
               VALUES ('$name', '$adhar', '$phone', '$skills_str', $age, '$gender', '$availability', '$latitude', '$longitude', '$language', $experience)";

    $success1 = $auth_conn->query($query1);
    $success2 = $labor_conn->query($query2);

    if ($success1 && $success2) {
        echo "✅ Laborer registered successfully!";
    } else {
        echo "❌ Error: " . $auth_conn->error . " / " . $labor_conn->error;
    }

} else {
    echo "❌ Invalid user type.";
}

// Close connections
$auth_conn->close();
$labor_conn->close();
?>
