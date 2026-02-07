const btn = document.getElementById('mobile-menu-button');
        const sidebar = document.getElementById('sidebar');
        const closeBtn = document.getElementById('close-sidebar');

        // Abrir/Cerrar sidebar
        btn.addEventListener('click', () => {
            sidebar.classList.toggle('-translate-x-full');
        });

        closeBtn.addEventListener('click', () => {
            sidebar.classList.add('-translate-x-full');
        });