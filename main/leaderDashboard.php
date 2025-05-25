<?php
$alert = "";
$redirect = false;

// Connect to labor_db
$labor_db = new mysqli("localhost", "root", "", "labor_db");
if ($labor_db->connect_error) {
    die("Connection to labor_db failed: " . $labor_db->connect_error);
}

// Connect to auth_db
$auth_db = new mysqli("localhost", "root", "", "auth_db");
if ($auth_db->connect_error) {
    die("Connection to auth_db failed: " . $auth_db->connect_error);
}

if ($_SERVER["REQUEST_METHOD"] == "POST" && $_POST["type"] === "worker") {
    $name = $_POST["name"];
    $adhar = $_POST["adhar"];
    $phone = $_POST["phone"];
    $password = $_POST["password"];
    $re_password = $_POST["re_password"];
    $age = $_POST["age"];
    $gender = $_POST["gender"];
    $language = $_POST["language"];
    $latitude = $_POST["latitude"];
    $longitude = $_POST["longitude"];
    $skills = implode(";", $_POST["skills"]);
    $availability = $_POST["availability"] === "Available" ? 1 : 0;
    $experience = $_POST["experience"];

    if ($password !== $re_password) {
        $alert = "Passwords do not match!";
    } else {
        $password_hash = password_hash($password, PASSWORD_DEFAULT);

        // Check for duplicate Aadhaar in labor_db
        $stmt = $labor_db->prepare("SELECT id FROM laborers WHERE adhar = ?");
        $stmt->bind_param("s", $adhar);
        $stmt->execute();
        $stmt->store_result();

        if ($stmt->num_rows > 0) {
            $alert = "Aadhaar number already registered!";
        } else {
            $stmt->close();

            // Insert into laborers table
            $stmt = $labor_db->prepare("INSERT INTO laborers (name, adhar, phone, skills, age, gender, language, latitude, longitude, available, experience) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)");
            $stmt->bind_param("ssssisssdii", $name, $adhar, $phone, $skills, $age, $gender, $language, $latitude, $longitude, $availability, $experience);

            if ($stmt->execute()) {
                $stmt->close();

                // Insert into auth_db.auth
                $stmt_auth = $auth_db->prepare("INSERT INTO auth (adhar, password_hash) VALUES (?, ?)");
                $stmt_auth->bind_param("ss", $adhar, $password_hash);

                if ($stmt_auth->execute()) {
                    $alert = "Registration successful!";
                    $redirect = true;
                } else {
                    $alert = "Error saving credentials: " . $stmt_auth->error;
                }

                $stmt_auth->close();
            } else {
                $alert = "Database error: " . $stmt->error;
            }
        }

        $stmt->close();
    }

    $labor_db->close();
    $auth_db->close();
}
?>

<!DOCTYPE html>
<html>
<head>
    <title>Laborer Registration - SahaYog</title>
    <link rel="stylesheet" href="labor-dashboard.css">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
</head>
<body>
    <div class="form-container">
        <?php if ($alert): ?>
            <div class="alert <?php echo $redirect ? 'alert-success' : 'alert-error'; ?>">
                <?php echo $alert; ?>
            </div>
        <?php endif; ?>

        <form method="post" class="registration-form">
            <input type="hidden" name="type" value="worker">
            <h2>Laborer Registration</h2>

            <div class="form-group">
                <label for="name">Full Name</label>
                <input type="text" id="name" name="name" placeholder="Enter your full name" required>
            </div>

            <div class="form-group">
                <label for="adhar">Aadhaar Number</label>
                <input type="text" id="adhar" name="adhar" placeholder="Enter your Aadhaar number" pattern="[0-9]{12}" required>
                <div class="validation-message">Must be 12 digits</div>
            </div>

            <div class="form-group">
                <label for="phone">Phone Number</label>
                <input type="tel" id="phone" name="phone" placeholder="Enter your phone number" pattern="[0-9]{10}" required>
                <div class="validation-message">Must be 10 digits</div>
            </div>

            <div class="form-group">
                <label for="password">Password</label>
                <input type="password" id="password" name="password" placeholder="Create a password" required>
            </div>

            <div class="form-group">
                <label for="re_password">Confirm Password</label>
                <input type="password" id="re_password" name="re_password" placeholder="Re-enter your password" required>
            </div>

            <div class="form-group">
                <label>Skills</label>
                <div class="skills-container">
                    <label class="skill-checkbox">
                        <input type="checkbox" name="skills[]" value="Ploughing"> Ploughing
                    </label>
                    <label class="skill-checkbox">
                        <input type="checkbox" name="skills[]" value="Sowing"> Sowing
                    </label>
                    <label class="skill-checkbox">
                        <input type="checkbox" name="skills[]" value="Harvesting"> Harvesting
                    </label>
                    <label class="skill-checkbox">
                        <input type="checkbox" name="skills[]" value="Irrigation"> Irrigation
                    </label>
                    <label class="skill-checkbox">
                        <input type="checkbox" name="skills[]" value="Packing"> Packing
                    </label>
                </div>
            </div>

            <div class="form-group">
                <label for="age">Age</label>
                <input type="number" id="age" name="age" placeholder="Enter your age" min="18" max="70" required>
            </div>

            <div class="form-group">
                <label for="gender">Gender</label>
                <div class="custom-select">
                    <select id="gender" name="gender" required>
                        <option value="" disabled selected>Select gender</option>
                        <option value="Male">Male</option>
                        <option value="Female">Female</option>
                        <option value="Other">Other</option>
                    </select>
                </div>
            </div>

            <div class="form-group">
                <label for="availability">Availability</label>
                <div class="custom-select">
                    <select id="availability" name="availability" required>
                        <option value="" disabled selected>Select availability</option>
                        <option value="Available">Available</option>
                        <option value="Not Available">Not Available</option>
                    </select>
                </div>
            </div>

            <div class="form-group">
                <label for="latitude">Latitude</label>
                <input type="text" id="latitude" name="latitude" placeholder="Enter your latitude" required>
            </div>

            <div class="form-group">
                <label for="longitude">Longitude</label>
                <input type="text" id="longitude" name="longitude" placeholder="Enter your longitude" required>
            </div>

            <div class="form-group">
                <label for="language">Language</label>
                <input type="text" id="language" name="language" placeholder="Enter your preferred language" required>
            </div>

            <div class="form-group">
                <label for="experience">Years of Experience</label>
                <input type="number" id="experience" name="experience" placeholder="Enter years of experience" min="0" required>
            </div>

            <button type="submit" class="submit-btn">Register</button>
        </form>

        <div class="form-footer">
            &copy; 2025 SahaYog Portal
        </div>
    </div>

    <script>
        // Form validation
        const form = document.querySelector('.registration-form');
        const password = document.getElementById('password');
        const rePassword = document.getElementById('re_password');

        form.addEventListener('submit', function(e) {
            if (password.value !== rePassword.value) {
                e.preventDefault();
                alert('Passwords do not match!');
            }
        });

        // Get location coordinates
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(function(position) {
                document.getElementById('latitude').value = position.coords.latitude;
                document.getElementById('longitude').value = position.coords.longitude;
            });
        }
    </script>
</body>
</html>