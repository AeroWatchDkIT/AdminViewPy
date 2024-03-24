// Fetch data from API endpoints
async function fetchData() {
  try {
    const [trackingLogResponse, userResponse] = await Promise.all([
      fetch('https://localhost:7128/TrackingLogs'),
      fetch('https://localhost:7128/users')
    ]);
    
    if (!trackingLogResponse.ok || !userResponse.ok) {
      throw new Error('Network response was not ok');
    }
    
    const [trackingLogData, userData] = await Promise.all([
      trackingLogResponse.json(),
      userResponse.json()
    ]);
    
    return { trackingLogData, userData };
  } catch (error) {
    console.error('Error fetching data:', error);
  }
}

// Prepare training data
function prepareTrainingData(trackingLogData, userData) {
  const trainingData = [];

  userData.users.forEach(user => {
    const incorrectPalletPlacements = trackingLogData.entities.filter(entry => entry.userId === user.id && entry.palletState === 0).length;
    trainingData.push({
      userId: user.id,
      incorrectPalletPlacements
    });
  });

  return trainingData;
}

// Train the model
async function trainModel(trainingData) {
  return model;
}

// Make predictions using the trained model
function predict(model, userData) {
  const predictions = userData.users.map(user => {
    const input = tf.tensor2d([[user.incorrectPalletPlacements]]);
    const prediction = model.predict(input).dataSync()[0];
    return { userId: user.id, predictedIncorrectPalletPlacements: prediction };
  });
  return predictions;
}

// Display results in a bar chart
function displayBarChart(predictions) {
  const userIds = predictions.map(prediction => prediction.userId);
  const predictedValues = predictions.map(prediction => prediction.predictedIncorrectPalletPlacements);

  const ctx = document.getElementById('barChart').getContext('2d');
  const barChart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: userIds,
      datasets: [{
        label: 'Predicted Incorrect Pallet Placements',
        data: predictedValues,
        backgroundColor: 'rgba(54, 162, 235, 0.5)',
        borderColor: 'rgba(54, 162, 235, 1)',
        borderWidth: 1
      }]
    },
    options: {
      scales: {
        yAxes: [{
          ticks: {
            beginAtZero: true
          }
        }]
      }
    }
  });
}


