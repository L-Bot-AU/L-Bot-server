function gen_graph() {
    var ctx = document.getElementById("librarian-graph").getContext("2d");
    var data = {
        "labels": ["8:00am", "9:00am", "10:00am"],
        "data": [4, 10, 6]
    }

    window.librarianGraph = new Chart(ctx, {
        type: "line",
        data: {
            labels: data["labels"],
            datasets: [{
                data: data["data"],
                pointHitRadius: 5,
                HoverBackgroundColor: [
                    "rgba(255, 99, 132, 1)",
                    "rgba(54, 162, 235, 1)",
                    "rgba(85, 214, 64, 1)",
                    "rgba(75, 192, 192, 1)",
                    "rgba(153, 102, 255, 1)",
                    "rgba(255, 159, 64, 1)"
                ],
                backgroundColor: [
                    "rgba(255, 99, 132, 0.2)",
                    "rgba(54, 162, 235, 0.2)",
                    "rgba(85, 214, 64, 0.2)",
                    "rgba(75, 192, 192, 0.2)",
                    "rgba(153, 102, 255, 0.2)",
                    "rgba(255, 159, 64, 0.2)"
                ],
                borderColor: [
                    "rgba(255, 99, 132, 1)",
                    "rgba(54, 162, 235, 1)",
                    "rgba(85, 214, 64, 1)",
                    "rgba(75, 192, 192, 1)",
                    "rgba(153, 102, 255, 1)",
                    "rgba(255, 159, 64, 1)"
                ],
                borderWidth: 3
            }],
        },
        options: {
            legend: {
                display: false,
            },
            scales: {
                yAxes: [{
                    ticks: {
                        beginAtZero: true,
                        max: 100,
                    }
                }]
            }
        }
    });
}