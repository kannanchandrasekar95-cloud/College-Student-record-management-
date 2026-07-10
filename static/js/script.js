// ============================================================================
// Student Record Management - Client-side JavaScript
// ============================================================================

// Auto-hide flash messages after 4 seconds
document.addEventListener("DOMContentLoaded", function () {
    const flashMessages = document.querySelectorAll(".flash-message");
    flashMessages.forEach(function (msg) {
        setTimeout(function () {
            msg.style.transition = "opacity 0.5s ease";
            msg.style.opacity = "0";
            setTimeout(function () {
                msg.style.display = "none";
            }, 500);
        }, 4000);
    });
});

// Confirm before deleting a student
function confirmDelete(name) {
    return confirm("Are you sure you want to delete student: " + name + "?");
}

// Basic client-side form validation for Add/Edit student forms
function validateForm() {
    const studentId = document.getElementById("student_id");
    const fullName = document.getElementById("full_name");
    const department = document.getElementById("department");
    const year = document.getElementById("year");
    const email = document.getElementById("email");
    const phone = document.getElementById("phone");

    if (!studentId.value.trim() || !fullName.value.trim() || !department.value.trim() ||
        !year.value.trim() || !email.value.trim() || !phone.value.trim()) {
        alert("Please fill in all required fields.");
        return false;
    }

    // Simple email format check
    const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailPattern.test(email.value.trim())) {
        alert("Please enter a valid email address.");
        return false;
    }

    // Phone should contain only digits and be at least 7 characters long
    const phonePattern = /^[0-9]{7,15}$/;
    if (!phonePattern.test(phone.value.trim())) {
        alert("Please enter a valid phone number (digits only, 7-15 digits).");
        return false;
    }

    return true;
}
