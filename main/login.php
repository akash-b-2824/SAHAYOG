<?php
session_start();

$alert = "";

if ($_SERVER["REQUEST_METHOD"] == "POST") {
    $adhar = $_POST["adhar"];
    $password = $_POST["password"];
    $user_type = $_POST["user_type"];

    if ($user_type === "farmer") {
        $db = new mysqli("localhost", "root", "", "farmer_db");
        $query = "SELECT name, password_hash FROM farmers WHERE adhar = ?";
    } else {
        $db = new mysqli("localhost", "root", "", "auth_db");
        $query = "SELECT password_hash FROM auth WHERE adhar = ?";
    }

    if ($db->connect_error) {
        die("Connection failed: " . $db->connect_error);
    }

    $stmt = $db->prepare($query);
    $stmt->bind_param("s", $adhar);
    $stmt->execute();
    $result = $stmt->get_result();

    if ($row = $result->fetch_assoc()) {
        $hash = $row["password_hash"];
        if (password_verify($password, $hash)) {
            $_SESSION["user_type"] = $user_type;
            $_SESSION["adhar"] = $adhar;

            if ($user_type === "farmer") {
                $_SESSION["user_name"] = $row["name"];
            } else {
                // Get laborer name from labor_db
                $labor_db = new mysqli("localhost", "root", "", "labor_db");
                $stmt2 = $labor_db->prepare("SELECT name FROM laborers WHERE adhar = ?");
                $stmt2->bind_param("s", $adhar);
                $stmt2->execute();
                $res2 = $stmt2->get_result();
                if ($labor = $res2->fetch_assoc()) {
                    $_SESSION["user_name"] = $labor["name"];
                }
                $stmt2->close();
                $labor_db->close();
            }

            header("Location: dashboard.php");
            exit();
        } else {
            $alert = "Invalid password.";
        }
    } else {
        $alert = "Aadhaar number not found.";
    }

    $stmt->close();
    $db->close();
}
?>

<!DOCTYPE html>
<html>
<head>
    <title>Login - SahaYog</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: linear-gradient(to right, #43cea2, #185a9d);
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
        }

        .login-container {
            background: #fff;
            padding: 30px 40px;
            border-radius: 20px;
            box-shadow: 0 8px 20px rgba(0,0,0,0.3);
            width: 400px;
        }

        h2 {
            text-align: center;
            color: #185a9d;
            margin-bottom: 20px;
        }

        input, select {
            width: 100%;
            padding: 12px;
            margin: 10px 0;
            border-radius: 10px;
            border: 1px solid #ccc;
        }

        input[type="submit"] {
            background: #185a9d;
            color: white;
            font-weight: bold;
            cursor: pointer;
            border: none;
        }

        input[type="submit"]:hover {
            background: #0d3c7c;
        }

        .radio-group {
            display: flex;
            justify-content: space-around;
            margin: 10px 0;
        }

        label {
            font-weight: bold;
        }

        .form-footer {
            text-align: center;
            font-size: 12px;
            color: #777;
            margin-top: 10px;
        }
    </style>
</head>
<body>
    <div class="login-container">
        <h2>Login to SahaYog</h2>
        <form method="POST">
            <label>Aadhaar Number:</label>
            <input type="text" name="adhar" required>

            <label>Password:</label>
            <input type="password" name="password" required>

            <label>User Type:</label>
            <div class="radio-group">
                <label><input type="radio" name="user_type" value="farmer" required> Farmer</label>
                <label><input type="radio" name="user_type" value="labor" required> Labor</label>
            </div>

            <input type="submit" value="Login">
        </form>
        <div class="form-footer">
            &copy; 2025 SahaYog Portal
        </div>
    </div>

    <script>
        <?php if (!empty($alert)): ?>
            alert("<?= $alert ?>");
        <?php endif; ?>
    </script>
</body>
</html>
