function verDetalles(idEquipo) {
    fetch(`/api/equipo/${idEquipo}`)
        .then(res => res.json())
        .then(data => {
            document.getElementById('modalNombre').innerText = data.nombre;
            document.getElementById('modalIdea').innerText = data.idea;
            // Llenar lista de miembros...
            modal.show();
        });
}