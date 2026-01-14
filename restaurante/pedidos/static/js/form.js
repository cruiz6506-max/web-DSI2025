document
  .getElementById("orderForm")
  .addEventListener("submit", function (event) {
    event.preventDefault(); // Evita el envío del formulario por defecto

    // Obtener los valores del formulario
    const name = document.getElementById("name").value;
    const email = document.getElementById("email").value;
    const phone = document.getElementById("phone").value;
    const burgerType = document.querySelector(
      'input[name="burgerType"]:checked'
    );
    const size = document.getElementById("size").value;
    const extras = document.getElementById("extras").value;

    if (burgerType) {
      alert(
        `Pedido recibido:\nNombre: ${name}\nCorreo: ${email}\nTeléfono: ${phone}\nTipo de Hamburguesa: ${burgerType.value}\nTamaño: ${size}\nExtras: ${extras}`
      );
    } else {
      alert("Por favor, selecciona el tipo de hamburguesa.");
    }
  });
