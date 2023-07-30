
const forecastCards = document.querySelectorAll('.forecast-card');
forecastCards.forEach(card => {
  card.addEventListener('click', function(event) {
    event.preventDefault();
    const date = card.dataset.date;
    window.location.href = `/forecast/${date}`;
  });
});