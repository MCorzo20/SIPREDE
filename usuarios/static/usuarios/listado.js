
const modal = document.getElementById("modalAula");
const campoTutor = document.getElementById("tutorId");
const nombreTutor = document.getElementById("nombreTutor");
const selectorAula = document.getElementById("aulaId");

function abrirModal(boton) {
    campoTutor.value = boton.dataset.tutorId;
    nombreTutor.textContent = boton.dataset.tutorNombre;

    // Restablecer la selección.
    selectorAula.value = "";

    modal.hidden = false;
    selectorAula.focus();
}

function cerrarModal() {
    modal.hidden = true;
}

modal.addEventListener("click", function (evento) {
    if (evento.target === modal) {
        cerrarModal();
    }
});

document.addEventListener("keydown", function (evento) {
    if (evento.key === "Escape" && !modal.hidden) {
        cerrarModal();
    }
});
