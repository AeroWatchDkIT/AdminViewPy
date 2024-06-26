// Fetch data from API endpoints
async function fetchData() {
  try {
    const [trackingLogResponse, userResponse] = await Promise.all([
      fetch('https://palletsyncapi.azurewebsites.net/TrackingLogs'),
      fetch('https://palletsyncapi.azurewebsites.net/Users')
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
// function prepareTrainingData(trackingLogData, userData) {
//   const trainingData = userData.users.map(user => {
//     const incorrectPalletPlacements = trackingLogData.entities.filter(entry => entry.userId === user.id && entry.palletState === 0).length;
//     return({
//       userId: user.id,
//       incorrectPalletPlacements
//     });
//   });

//   return trainingData;
// }

// Prepare training data
function prepareTrainingData(trackingLogData, userData) {
  const trainingData = {
    inputs: [],
    labels: []
  };

  userData.users.forEach(user => {
    const incorrectPalletPlacements = trackingLogData.entities.filter(entry => entry.userId === user.id && entry.palletState === 0).length;
    trainingData.inputs.push([incorrectPalletPlacements]);
    trainingData.labels.push(user.forkliftCertified ? 1 : 0);
  });

  return trainingData;
}


// Train the model
async function trainModel(trainingData) {
  console.log(JSON.stringify(trainingData))
  const xs = trainingData.inputs;
  const ys = trainingData.labels;
  console.log(JSON.stringify(xs),xs.length)
  console.log(JSON.stringify(ys),ys.length)

  // Define and train the model using TensorFlow.js
  const model = tf.sequential();
  model.add(tf.layers.dense({ units: 1, inputShape: [1] }));

  model.compile({ optimizer: 'sgd', loss: 'meanSquaredError' });
  const xsTensor = tf.tensor2d(xs, [xs.length, 1]);
  const ysTensor = tf.tensor2d(ys, [ys.length, 1]);

  await model.fit(xsTensor, ysTensor, { epochs: 100 });

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
  const predictedValues =predictions.map(prediction => {
    // Check if the predicted value is negative, if so, set it to 0
    const predictedValue = prediction.predictedIncorrectPalletPlacements;
    return predictedValue < 0 ? 0 : predictedValue;
  });

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

// Main function to orchestrate the process
async function main() {
  const { trackingLogData, userData } = await fetchData();
  console.log(trackingLogData,userData)
  const trainingData = prepareTrainingData(trackingLogData, userData);
  console.log(trainingData)
  const model = await trainModel(trainingData);
  const predictions = predict(model, userData);
  console.log(predictions)
  displayBarChart(predictions);
}

// Call the main function to start the process
main();
