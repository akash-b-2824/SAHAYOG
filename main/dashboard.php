<?php
session_start();
if (!isset($_SESSION['user_name'])) {
    header("Location: login.php");
    exit();
}
?>

<!DOCTYPE html>
<html>
<head>
    <title>Dashboard - SahaYog</title>
</head>
<body>
    <h1>Welcome, <?php echo htmlspecialchars($_SESSION['user_name']); ?>!</h1>
    <p>You are logged in as a <?php echo $_SESSION['user_type']; ?>.</p>
    <p>Your Aadhaar: <?php echo $_SESSION['adhar']; ?></p>
    <a href="logout.php">Logout</a>
</body>
</html>
