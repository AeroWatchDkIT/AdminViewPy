// Function to create the Pie Chart
function createPieChart(data) {
  var onShelfCount = data.entities.filter(function (entity) {
    return entity.place.startsWith("S-");
  }).length;

  var onFloorCount = data.entities.filter(function (entity) {
    return entity.place === "On Floor";
  }).length;

  var onForkliftCount = data.entities.filter(function (entity) {
    return entity.place.includes("Forklift");
  }).length;

  var missingCount = data.entities.filter(function (entity) {
    return entity.place === "Missing";
  }).length;

  var ctx = document.getElementById("forkliftPieChart");
  var forkliftPieChart = new Chart(ctx, {
    type: 'pie',
    data: {
      labels: ["On Shelf", "On Floor",  "On Forklift", "Missing"],
      datasets: [{
        data: [onShelfCount, onFloorCount, onForkliftCount, missingCount],
        backgroundColor: ['#4e73df', '#1cc88a', '#f6c23e', '#e74a3b'],
        hoverBackgroundColor: ['#2e59d9', '#17a673', '#f6c23e', '#e74a3b'],
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

// Fetch data from the API
fetch('https://palletsyncapi.azurewebsites.net/PalletStatuses')
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
