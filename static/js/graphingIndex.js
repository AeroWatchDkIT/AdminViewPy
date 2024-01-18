// chart.js

// Pre-saved forklift data (replace this with your actual data)
const forkliftData = [
    { id: 'F-0007', lastUserId: 'U-0002', lastUser: 'Nikita Fedans', lastPallet: 'P-0003' },
    { id: 'F-0012', lastUserId: 'U-0001', lastUser: 'Kacper Wroblewski', lastPallet: 'P-0003' },
    { id: 'F-0016', lastUserId: 'U-0003', lastUser: 'Teodor Donchev', lastPallet: 'P-0005' },
    { id: 'F-0205', lastUserId: 'U-0003', lastUser: 'Teodor Donchev', lastPallet: 'P-0001' },
    // Add more data as needed
];

// Function to calculate user frequencies and update the chart
function updateChartWithData() {
    const userFrequency = {};
    for (const forklift of forkliftData) {
        const userId = forklift.lastUserId;
        if (!userFrequency[userId]) {
            userFrequency[userId] = 0;
        }
        userFrequency[userId]++;
    }

    const userNames = Object.keys(userFrequency);
    const userCounts = Object.values(userFrequency);

    const ctx = document.getElementById('userFrequencyChart').getContext('2d');
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: userNames,
            datasets: [{
                label: 'Frequency',
                data: userCounts,
                backgroundColor: 'rgba(75, 192, 192, 0.6)',
                borderWidth: 1
            }]
        },
        options: {
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Frequency'
                    }
                }
            }
        }
    });
}

// Call the function to update the chart with pre-saved data
updateChartWithData();
