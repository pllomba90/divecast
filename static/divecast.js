

const forecastCards = document.querySelectorAll('.forecast-card');
forecastCards.forEach(card => {
  card.addEventListener('click', function(event) {
    event.preventDefault();
    const date = card.dataset.date;
    fetch(`/forecast/${date}`)
      .then(response => {
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        window.location.href = response.url;
      })
      .catch(error => {
        console.error('Error:', error);
      });
  });
});
