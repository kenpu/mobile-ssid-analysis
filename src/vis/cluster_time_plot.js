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
var width = 960;    //this will be overwritten
var height = 600;
var padding = 40;

// graph properties
var w = width - padding*2;  //this will be overwritten
var h = height - padding*2;
var x_origin = padding;
var y_origin = padding;

var x_scale = 6;
var dot_radius = Math.round(x_scale/2);
var stroke_width = 1;


var data;




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

    /***********************************************
    *
    * SET UP TIME STUFF
    *
    ***********************************************/
    var min_time = data[0].time;
    var max_time = Math.max.apply(Math,data.map(function(o){return o.time;}));

    console.log("Min time: "+min_time);
    console.log("Max time: "+max_time);

    // Set up timeline scale which is the vertical axis
    var time_scale = d3.scale.linear()
        .domain([min_time, max_time])
        .range([h,0]);

    var yAxis = d3.svg.axis()
        .scale(time_scale)
        .orient("left");



    /***********************************************
    *
    * SET UP NUMBER OF READINGS STUFF
    *
    ***********************************************/
    var min_num = data[0].readings;
    var max_num = data[data.length-1].readings;

    console.log("Min readings: "+min_num);
    console.log("Max readings: "+max_num);

    w = (max_num - min_num) * x_scale;
    width = w + 2*padding;

    // Set up timeline scale which is the vertical axis
    var num_scale = d3.scale.linear()
        .domain([min_num, max_num])
        .range([0,w]);

    var xAxis = d3.svg.axis()
        .scale(num_scale)
        .orient("bottom");


    /***********************************************
    *
    * SET UP SVG AND ADD AXIS
    *
    ***********************************************/

    var svg = d3.select("body").append("svg")
        .attr("width", width)
        .attr("height", height)
        .append("g")
        .attr("transform", "translate( x_origin , y_origin)");

    svg.append("g")
        .attr("class", "axis")
        .attr("transform", "translate(" + x_origin + "," + y_origin + ")")
        .call(yAxis);

    svg.append("g")
        .attr("class", "axis")
        .attr("transform", "translate(" + x_origin + "," + (y_origin+h) + ")")
        .call(xAxis);



    //This is the accessor function we talked about above
    var lineFunction = d3.svg.line()
        .x(function(d) { return x_origin + num_scale(d.readings); })
        .y(function(d) { return y_origin + time_scale(d.time); })
        .interpolate("linear");

    //The line SVG Path we draw
    var lineGraph = svg.append("path")
        .attr("d", lineFunction(data))
        .attr("stroke", "blue")
        .attr("stroke-width", stroke_width)
        .attr("fill", "none");

    svg.selectAll("circle")
        .data(data)
        .enter()
        .append("circle")
        .attr("cx", function(d) { return x_origin + num_scale(d.readings); })
        .attr("cy", function(d) { return y_origin + time_scale(d.time); })
        .attr("r", dot_radius)
        .on("mouseover", function(d) {
            var x_pos = x_origin + num_scale(d.readings) + dot_radius + 5;
            var y_pos = y_origin + time_scale(d.time) - 70;
            var msg = "Readings: " + d.readings + "<br>"
                + "Time: " + d.time;

            d3.select("#tooltip")
                .style("left", x_pos+"px")
                .style("top", y_pos+"px")
                .select("#value")
                .html(msg);
            d3.select("#tooltip").classed("hidden", false);
        })
        .on("mouseout", function () {
            d3.select("#tooltip").classed("hidden", true);
        });

});

d3.select(self.frameElement).style("height", height + "px");