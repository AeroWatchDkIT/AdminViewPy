// Function to create the Pie Chart
function createPieChart(data) {
  var authorizedUsers = data.users.filter(function (user) {
    return user.forkliftCertified;
  });

  var unauthorizedUsers = data.users.filter(function (user) {
    return user.forkliftCertified;
  });

  var ctx = document.getElementById("forkliftPieChart");
  var userPieChart = new Chart(ctx, {
    type: 'pie',
    data: {
      labels: ["Authorized Users", "Unauthorized users"],
      datasets: [{
        data: [authorizedUsers.length, unauthorizedUsers.length],
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

// Fetch data from the API
fetch('https://localhost:7128/Users')
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
