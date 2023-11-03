function toggleItems(categoryId) {
  const items = document.getElementById(categoryId + 'Items');
  items.classList.toggle('hidden');
}
function updateLiveDate() {
  let currentDate = new Date();
  let options = {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day:'numeric',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      timeZoneName: 'short',
      hour12: false
  };
  let formattedDate = currentDate.toLocaleDateString(undefined, options);
  document.getElementById('current-date').innerHTML = formattedDate;
}

setInterval(updateLiveDate, 1000);
updateLiveDate();


let all_selector = document.getElementById("all_selector");

if (all_selector) {
    all_selector.addEventListener('change', function() {
        if (this.checked) {
            const checkboxes = document.querySelectorAll('input[name="selected_transactions"]');
            checkboxes.forEach(checkbox => checkbox.checked = true);
        } else {
            const checkboxes = document.querySelectorAll('input[name="selected_transactions"]');
            checkboxes.forEach(checkbox => checkbox.checked = false);
        }
    });
}

  // let table = document.getElementById("supervisor_deposits");
  // let totalPrice = 0, priceCell, priceValue;
  // for (var i = 1; i < table.rows.length - 1; i++) {
  //     priceCell = table.rows[i].cells[2].textContent.replace(/,/g, "")
  //     priceValue = parseFloat(priceCell);
  //     if (!isNaN(priceValue)) {
  //         totalPrice += priceValue;
  //     }
  // }
  // var formattedCurrency = new Intl.NumberFormat(undefined, {
  //     style: "currency",
  //     currency: "GMD" // Change to the desired currency code (e.g., "EUR", "JPY", "GBP")
  // }).format(totalPrice);
  // document.getElementById("total-amount").innerHTML = formattedCurrency;