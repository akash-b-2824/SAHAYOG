document.addEventListener("DOMContentLoaded", function () {
    // Tab Switching
    const loginTab = document.getElementById("loginTab");
    const registerTab = document.getElementById("registerTab");
    const loginContent = document.getElementById("loginContent");
    const registerContent = document.getElementById("registerContent");

    function switchTab(activeTab, activeContent, inactiveTab, inactiveContent) {
        activeTab.classList.add("active");
        activeContent.classList.remove("hidden");
        inactiveTab.classList.remove("active");
        inactiveContent.classList.add("hidden");
    }

    loginTab.addEventListener("click", function () {
        switchTab(loginTab, loginContent, registerTab, registerContent);
    });

    registerTab.addEventListener("click", function () {
        switchTab(registerTab, registerContent, loginTab, loginContent);
    });

    // User Type Switching
    const farmerBtn = document.getElementById("farmerBtn");
    const laborerBtn = document.getElementById("laborerBtn");
    const skillsGroup = document.getElementById("skillsGroup");

    farmerBtn.addEventListener("click", function () {
        farmerBtn.classList.add("active");
        laborerBtn.classList.remove("active");
        skillsGroup.classList.add("hidden");
    });

    laborerBtn.addEventListener("click", function () {
        laborerBtn.classList.add("active");
        farmerBtn.classList.remove("active");
        skillsGroup.classList.remove("hidden");
    });

    // Form Submissions
    const loginForm = document.getElementById("loginForm");
    const registerForm = document.getElementById("registerForm");

    loginForm.addEventListener("submit", function (e) {
        e.preventDefault();
        const phone = document.getElementById("loginPhone").value;
        const password = document.getElementById("loginPassword").value;

        if (!/^\d{10}$/.test(phone)) {
            alert("Please enter a valid 10-digit phone number");
            return;
        }

        if (password.length < 6) {
            alert("Password must be at least 6 characters long");
            return;
        }

        console.log("Login attempt with:", { phone, password });
        alert("Login successful! (Backend integration needed)");
        loginForm.reset();
    });

    registerForm.addEventListener("submit", function (e) {
        e.preventDefault();
        const name = document.getElementById("name").value;
        const phone = document.getElementById("phone").value;
        const region = document.getElementById("region").value;
        const isLaborer = laborerBtn.classList.contains("active");

        if (!name || !phone || !region) {
            alert("Please fill in all required fields");
            return;
        }

        if (!/^\d{10}$/.test(phone)) {
            alert("Please enter a valid 10-digit phone number");
            return;
        }

        let skills = [];
        if (isLaborer) {
            const skillCheckboxes = document.querySelectorAll(
                'input[name="skill"]:checked'
            );
            skills = Array.from(skillCheckboxes).map((cb) => cb.value);

            if (skills.length === 0) {
                alert("Please select at least one skill");
                return;
            }
        }

        const userData = {
            name,
            phone,
            region,
            userType: isLaborer ? "laborer" : "farmer",
            skills: isLaborer ? skills : undefined,
        };

        console.log("Registration data:", userData);
        alert(
            `Account created successfully!\n\nName: ${name}\nPhone: ${phone}\nType: ${
                isLaborer ? "Laborer" : "Farmer"
            }\n${isLaborer ? "Skills: " + skills.join(", ") : ""}`
        );

        registerForm.reset();
        document
            .querySelectorAll('input[name="skill"]')
            .forEach((cb) => (cb.checked = false));
        switchTab(loginTab, loginContent, registerTab, registerContent);
    });

    // Skill Checkbox Toggle
    document.querySelectorAll(".skill-checkbox").forEach((checkbox) => {
        checkbox.addEventListener("click", function () {
            const input = this.querySelector("input");
            input.checked = !input.checked;
            this.classList.toggle("active", input.checked);
        });
    });
});
