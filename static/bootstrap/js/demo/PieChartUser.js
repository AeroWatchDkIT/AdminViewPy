// Assuming you have already included Chart.js in your project
function createPieChart(correctPlacements, incorrectPlacements) {
  var ctx = document.getElementById("forkliftPieChart");
  var forkliftPieChart = new Chart(ctx, {
      type: 'pie',
      data: {
          labels: ["Incorrect Placements", "Correct Pallets"],
          datasets: [{
              data: [correctPlacements, incorrectPlacements],
              backgroundColor: ['#4e73df', '#1cc88a'],
              hoverBackgroundColor: ['#2e59d9', '#17a673'],
              hoverBorderColor: "rgba(234, 236, 244, 1)",
          }],
      },
      options: {
          maintainAspectRatio: false,
          tooltips: {
              backgroundColor: "rgb(255,255,255)",
              bodyFontColor: "#858796",
              borderColor: '#dddfeb',
              borderWidth: 1,
              xPadding: 15,
              yPadding: 15,
              displayColors: false,
              caretPadding: 10,
          },
          legend: {
              display: true,
              position: 'bottom',
          },
      },
  });
}

document.addEventListener('DOMContentLoaded', function() {
  const chartPieDiv = document.querySelector('.chart-pie');
  const correctPlacement = parseInt(chartPieDiv.getAttribute('data-correct-pallet-placement'), 10);
  const incorrectPlacement = parseInt(chartPieDiv.getAttribute('data-incorrect-pallet-placement'), 10);

  createPieChart(correctPlacement, incorrectPlacement);
});

// Fetch data from the API
fetch('https://palletsyncapi.azurewebsites.net/Forklifts')
  .then(response => {
    if (!response.ok) {
      throw new Error('Network response was not ok');
    }
    return response.json();
  })
  .then(data => {
    // Call the function to create the Pie Chart with the fetched data
    createPieChart(data);
  })
  .catch(error => {
    console.error('Error fetching data from the API:', error);
  });
