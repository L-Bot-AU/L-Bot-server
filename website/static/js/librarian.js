function update_graph(data){
    window.librarianGraph.data.labels = data["dates"];
    window.librarianGraph.data.datasets[0].data = data["values"];
    //alternative:
    // window.librarianGraph.data.datasets = [];
    // window.librarianGraph.data.datasets.push(dataset(data));
    window.librarianGraph.update();
}

function dataset(update){ // most likely won't be used but possibly
    var data = {data: update["data"],
                pointHitRadius: 5,
                HoverBackgroundColor: 'rgba(255, 99, 132, 1)',
                backgroundColor: 'rgba(255, 99, 132, 0.2)',
                borderColor: 'rgba(255, 99, 132, 1)',
                borderWidth: 3
            };
    return data;
}

function hard_code_graph_upd(){ //unnecessary?
    var data = {
        "labels": ["8:00am", "9:00am", "10:00am", "11", "12", "1", "2", "3"],
        "data": [47, 93, 64, 53, 76, 84, 86, 96]
    };
    update_graph(data);
}

function imageDownload() {
    var image = document.createElement('a');
    image.href = window.librarianGraph.toBase64Image();
    image.download = 'graph.png';

    image.click();
}