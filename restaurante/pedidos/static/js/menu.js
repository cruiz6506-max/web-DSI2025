document.addEventListener("DOMContentLoaded", () => {
  const cartItems = document.getElementById("cart-items");
  const cartTotal = document.getElementById("cart-total");
  const contadorProductos = document.getElementById("contador-productos");
  const carritoBtn = document.querySelector(".carrito");
  const cart = document.querySelector(".cart");
  const checkoutForm = document.getElementById("checkout-form");
  let cartData = {};

  document.querySelectorAll(".add-to-cart").forEach(button => {
    button.addEventListener("click", () => {
      const name = button.dataset.name;
      const price = parseFloat(button.dataset.price);
      if (!cartData[name]) cartData[name] = { price: price, quantity: 0 };
      cartData[name].quantity += 1;
      updateCartDisplay();
    });
  });

  function updateCartDisplay() {
    cartItems.innerHTML = "";
    let total = 0;
    for (const [name, item] of Object.entries(cartData)) {
      const li = document.createElement("li");
      li.textContent = `${name} - $${item.price.toFixed(2)} x${item.quantity}`;
      const removeBtn = document.createElement("button");
      removeBtn.textContent = "×";
      removeBtn.addEventListener("click", () => {
        delete cartData[name];
        updateCartDisplay();
      });
      li.appendChild(removeBtn);
      cartItems.appendChild(li);
      total += item.price * item.quantity;
    }
    cartTotal.textContent = `Total: $${total.toFixed(2)}`;
    contadorProductos.textContent = Object.values(cartData).reduce((sum, i) => sum + i.quantity, 0);
  }

  carritoBtn.addEventListener("click", () => {
    cart.style.display = cart.style.display === "block" ? "none" : "block";
  });

  checkoutForm.addEventListener("submit", function(e){
    e.preventDefault(); // detener envío
    const carritoArray = Object.entries(cartData).map(([nombre, item]) => ({
      nombre: nombre,
      cantidad: item.quantity,
      precio: item.price
    }));
    if(carritoArray.length === 0){
      alert("Tu carrito está vacío");
      return;
    }
    document.getElementById("carrito-json").value = JSON.stringify(carritoArray);
    checkoutForm.submit(); // enviar al backend
  });
});
