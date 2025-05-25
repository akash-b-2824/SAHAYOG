<?php
$auth_conn = new mysqli("localhost", "root", "", "auth_db");

if ($auth_conn->connect_error) {
    die("Connection failed: " . $auth_conn->connect_error);
}

$adhar = mysqli_real_escape_string($auth_conn, $_POST['adhar']);
$password = $_POST['password'];

// Helper function
function tryLogin($conn, $table, $adhar, $password) {
    $query = "SELECT * FROM $table WHERE adhar = '$adhar'";
    $result = $conn->query($query);

    if ($result->num_rows === 1) {
        $user = $result->fetch_assoc();
        if (password_verify($password, $user['password'])) {
            return ['success' => true, 'user' => $user, 'role' => $table];
        } else {
            return ['success' => false, 'error' => "Invalid password"];
        }
    }
    return ['success' => false, 'error' => "User not found"];
}

// Try farmers first
$login = tryLogin($auth_conn, 'farmers', $adhar, $password);

if (!$login['success']) {
    // Try workers
    $login = tryLogin($auth_conn, 'workers', $adhar, $password);
}

if ($login['success']) {
    session_start();
    $_SESSION['user'] = $login['user'];
    $_SESSION['role'] = $login['role'];
    echo '<p style="font-family:Arial, sans-serif; font-size:16px; background:#f0f9f0; padding:12px 20px; border:1px solid #c6e6c6; border-radius:8px; color:#2f855a; display:inline-block;">✅ <span style="font-weight:600; color:#2f855a;">Login successful!</span>' . $login['role'];
    header("Location: dashboard.html"); // Uncomment this if you want redirect
} else {
    echo "❌ Login failed: " . $login['error'];
}

$auth_conn->close();
?>
