// Validar longitud del teléfono
document.addEventListener("DOMContentLoaded", function () {
  const form = document.querySelector("form");
  if (!form) return;

  form.addEventListener("submit", function (event) {
    const telefono = document.querySelector("#telefono");
    const nombre = document.querySelector("#nombre");
    const apellido = document.querySelector("#apellido");

    if (telefono.value.length !== 10 || isNaN(telefono.value)) {
      alert("El teléfono debe tener exactamente 10 dígitos numéricos.");
      telefono.focus();
      event.preventDefault();
      return;
    }

    if (nombre.value.trim() === "" || apellido.value.trim() === "") {
      alert("El nombre y el apellido no pueden estar vacíos.");
      event.preventDefault();
      return;
    }
  });

  // Mensaje de confirmación al eliminar
  const deleteLinks = document.querySelectorAll(".btn.delete");
  deleteLinks.forEach(link => {
    link.addEventListener("click", function (e) {
      const confirmed = confirm("¿Estás seguro de que deseas eliminar este catequizado?");
      if (!confirmed) {
        e.preventDefault();
      }
    });
  });
});
