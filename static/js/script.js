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