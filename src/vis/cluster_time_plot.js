/*************************************************
*
* LITTLE HELPER METHODS
*
*************************************************/

// returns the height of a node to the furthest leaf
function get_height(node) {
    if (node.children.length == 0) return 0;
    else if (node.children.length == 1) return 1;
    else return Math.max(get_height(node.children[0])+1, get_height(node.children[1])+1);
}


// draws a line
function draw_line(x1, y1, x2, y2) {
    svg.append("line")
        .attr("x1", x1)
        .attr("y1", y1)
        .attr("x2", x2)
        .attr("y2", y2)
        .attr("stroke", "grey")
        .attr("stroke-width", 1)
        .attr("fill", "none");
}

// draws horz line and vert line to reach diagonal points
function draw_two_lines(x1, y1, x2, y2) {
    draw_line(x1, y1, x2, y1);
    draw_line(x2, y1, x2, y2);
}


// Set up colour scale to fill dots according to similarity
var sim_scale = d3.scale.linear()
    .domain([0, 1.1])
    .range([0, 256])
    .nice();




/*************************************************
*
* MAGIC NUMBER DECLARATIONS AND SETTINGS
*
*************************************************/

// SVG properties
var width = 960;
var height = 600;
var padding = 40;

// graph properties
var w = width - padding*2;
var h = height - padding*2;
var x_origin = padding;
var y_origin = padding;

var data;

// create the svg to work with
var svg = d3.select("body").append("svg")
        .attr("width", width)
        .attr("height", height)
        .append("g")
        .attr("transform", "translate(x_origin, y_origin)");


/*************************************************
*
* THIS IS THE MAIN ATTRACTION
*
*************************************************/

console.log("about to open the file...");

d3.json("../json_/cluster_time_test.json", function(error, dataset) {
    if (error) throw error;

    console.log("opened the file");

    data = dataset;
    console.log("data[0]"+ data[0])
    var min_time = data[0].time;
    console.log("Min time: "+min_time);
    var max_time = Math.max.apply(Math,data.map(function(o){return o.time;}));


    console.log("Max time: "+max_time);






});

d3.select(self.frameElement).style("height", height + "px");