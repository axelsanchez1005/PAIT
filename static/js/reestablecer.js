// Función para ver/ocultar contraseña
function togglePassword(inputId, btn) {
    const input = document.getElementById(inputId);
    const icon = btn.querySelector('i');
    
    if (input.type === "password") {
        input.type = "text";
        icon.classList.replace('fa-regular', 'fa-solid');
        icon.classList.replace('fa-eye', 'fa-eye-slash');
    } else {
        input.type = "password";
        icon.classList.replace('fa-solid', 'fa-regular');
        icon.classList.replace('fa-eye-slash', 'fa-eye');
    }
}

// Validación de coincidencia
document.getElementById('resetForm').addEventListener('submit', function(e) {
    const pass = document.getElementById('nueva_clave').value;
    const confirm = document.getElementById('confirmar_clave').value;
    const errorMsg = document.getElementById('error-msg');
    const confirmInput = document.getElementById('confirmar_clave');

    if (pass !== confirm) {
        e.preventDefault(); // Detiene el envío
        errorMsg.style.display = 'block';
        confirmInput.style.border = '1px solid #dc3545';
        confirmInput.style.backgroundColor = '#fff2f2';
    } else {
        errorMsg.style.display = 'none';
    }
});