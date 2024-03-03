
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


// Function to define and train a neural network model
async function trainModel(trainingData) {
  const model = tf.sequential();
  model.add(tf.layers.dense({ units: 16, inputShape: [2], activation: 'relu' }));
  model.add(tf.layers.dense({ units: 8, activation: 'relu' }));
  model.add(tf.layers.dense({ units: 1, activation: 'sigmoid' }));
  
  model.compile({ optimizer: tf.train.adam(0.01), loss: 'binaryCrossentropy', metrics: ['accuracy'] });

  const inputs = tf.tensor2d(trainingData.inputs);
  const labels = tf.tensor2d(trainingData.labels);

  await model.fit(inputs, labels, { epochs: 50, shuffle: true });

  return model;
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
    // Prepare training data
    const tdata = {
      inputs: trainingData.users.map(user => [user.forkliftCertified ? 1 : 0, user.incorrectPalletPlacements]),
      labels: trainingData.users.map(user => [user.userType === 1 ? 1 : 0]) // userType 1 is authorized, 0 is unauthorized
    };

    // Train the model using the training data
    const model = await trainModel(tdata);

    // Fetch user data from the API
    fetch('https://localhost:7128/Users')
      .then(response => {
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        return response.json();
      })
      .then(data => {
        // Using the trained model to predict authorization for each user
        const inputs = data.users.map(user => [user.forkliftCertified ? 1 : 0, user.incorrectPalletPlacements]);
        const predictions = model.predict(tf.tensor2d(inputs)).dataSync();

        const authorizedUsers = data.users.filter((user, index) => predictions[index] > 0.5);
        const unauthorizedUsers = data.users.filter((user, index) => predictions[index] <= 0.5);

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

