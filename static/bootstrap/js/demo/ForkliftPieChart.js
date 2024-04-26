  // Set new default font family and font color to mimic Bootstrap's default styling
(Chart.defaults.global.defaultFontFamily = "Nunito"),
'-apple-system,system-ui,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif';
Chart.defaults.global.defaultFontColor = "#858796";

function createPieChart(authorizedUsers, unauthorizedUsers) {
var ctx = document.getElementById("forkliftPieChart");
var userPieChart = new Chart(ctx, {
  type: "pie",
  data: {
    labels: ["Authorized Users", "Unauthorized users"],
    datasets: [
      {
        data: [authorizedUsers.length, unauthorizedUsers.length],
        backgroundColor: ["#4e73df", "#1cc88a"],
        hoverBackgroundColor: ["#2e59d9", "#17a673"],
        hoverBorderColor: "rgba(234, 236, 244, 1)",
      },
    ],
  },
  options: {
    maintainAspectRatio: false,
    tooltips: {
      backgroundColor: "rgb(255,255,255)",
      bodyFontColor: "#858796",
      borderColor: "#dddfeb",
      borderWidth: 1,
      xPadding: 15,
      yPadding: 15,
      displayColors: false,
      caretPadding: 10,
    },
    legend: {
      display: true,
      position: "bottom",
    },
  },
});
}

// Function to define and train a neural network model
async function trainModel(trainingData) {
const model = tf.sequential();
model.add(
  tf.layers.dense({ units: 16, inputShape: [1], activation: "relu" })
);
model.add(tf.layers.dense({ units: 8, activation: "relu" }));
model.add(tf.layers.dense({ units: 1, activation: "sigmoid" }));

model.compile({
  optimizer: tf.train.adam(0.01),
  loss: "binaryCrossentropy",
  metrics: ["accuracy"],
});

const inputs = tf.tensor2d(trainingData.inputs);
const labels = tf.tensor2d(trainingData.labels);

await model.fit(inputs, labels, { epochs: 50, shuffle: true });

return model;
}

// Fetch data from the API
fetch("https://palletsyncapi.azurewebsites.net/Users")
.then((response) => {
  if (!response.ok) {
    throw new Error("Network response was not ok");
  }
  return response.json();
})
.then(async (data) => {
  // Prepare training data

  const tdata = {
    inputs: data.users.map((user) => [user.incorrectPalletPlacements]),
    labels: data.users.map((user) => [
      user.incorrectPalletPlacements > 5
        ? 0
        : user.forkliftCertified
        ? 1
        : 0,
    ]), // Predict not certified if incorrectPalletPlacements > 4
  };


  // Train the model using the training data
  const model = await trainModel(tdata);

  console.log(tdata);
  // Using the trained model to predict authorization for each user
  // Using the trained model to predict authorization for each user
  const inputs = data.users.map((user) => [user.incorrectPalletPlacements]);
  console.log("Inputs:", inputs); // Log input data
  const predictions = model.predict(tf.tensor2d(inputs)).dataSync();
  console.log("Predictions:", predictions); // Log predictions

  const authorizedUsers = [];
  const unauthorizedUsers = [];
  inputs.forEach((prediction, index) => {
    if (prediction > 0.5) {
      authorizedUsers.push(data.users[index]);
    } else {
      unauthorizedUsers.push(data.users[index]);
    }
  });

  console.log(authorizedUsers.length,unauthorizedUsers.length);

  // Call the function to create the Pie Chart with the predicted data
  createPieChart(authorizedUsers, unauthorizedUsers);
})
.catch((error) => {
  console.error("Error fetching data from the API:", error);
});