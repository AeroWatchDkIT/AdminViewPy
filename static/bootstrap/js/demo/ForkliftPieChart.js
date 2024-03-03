function createPieChart(authorizedUsers, unauthorizedUsers) {
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


// Function to define and train a simple neural network model
async function trainModel(trainingData) {

}

// Fetch training data from the API
fetch('https://localhost:7128/Users')
  .then(response => {
    if (!response.ok) {
      throw new Error('Network response was not ok');
    }
    return response.json();
  })
  .then(async trainingData => {

    // Train the model using the training data
    const model = await trainModel(trainingData);
    

    // Fetch user data from the API
    fetch('https://localhost:7128/Users')
      .then(response => {
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        return response.json();
      })
      .then(data => {
        // Use the trained model to predict authorization for each user

        // Call the function to create the Pie Chart with the predicted data
        createPieChart(authorizedUsers, unauthorizedUsers);
      })
      .catch(error => {
        console.error('Error fetching user data from the API:', error);
      });
  })
  .catch(error => {
    console.error('Error fetching training data from the API:', error);
  });
