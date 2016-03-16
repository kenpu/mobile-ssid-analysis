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

var root;    // root node of json data
var nodes = [];   // stores cx, cy, similarity, name

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

d3.json("../json_/hierarchy.json", function(error, data) {
    if (error) throw error;

    root = data;

    console.log("root.start: "+root.start);
    console.log("root.end: "+root.end);

    var root_height = get_height(root);
    console.log("root height: " + root_height);

    console.log("root total readings: " + root.total);

    // Set up timeline scale
    var time_scale = d3.time.scale()
        .domain([new Date(root.start), new Date(root.end)])
        .range([0,w]);

    var xAxis = d3.svg.axis()
        .scale(time_scale)
        .orient("bottom");

    svg.append("g")
        .attr("class", "axis")
        .attr("transform", "translate(" + x_origin + "," + (y_origin+h) + ")")
        .call(xAxis);

    // Set up size scale to fill dots according to total number of readings
    var total_reading_scale = d3.scale.linear()
        .domain([1, root.total+1])
        .range([2, Math.round(h/(root_height*1.75))])
        .nice();

    // Set up tree height scale
    var y_scale = d3.scale.linear()
        .domain([0,root_height])
        .range([h,0])
        .nice();

    // recursively draws nodes and links
    function draw_hierarchy_structure(node) {
        var node_start, node_end = -1, cx, cy;

        if (node.children.length == 2) {
            node_start = time_scale(new Date(node.start));
            node_end = time_scale(new Date(node.end));
            cx = x_origin + node_start + Math.round((node_end-node_start)/2);
        } else {
            node_start = time_scale(new Date(node.start));
            cx = x_origin + node_start;
        }

        cy = y_origin + y_scale(get_height(node));

        if (node.children.length > 0 ) {

            //draw left child line or only child line
            var left_child = draw_hierarchy_structure(node.children[0]);
            draw_two_lines(cx, cy, left_child.x, left_child.y);

            //if there is a second child, then draw that line too
            if (node.children.length == 2) {
                var right_child = draw_hierarchy_structure(node.children[1]);
                draw_two_lines(cx, cy, right_child.x, right_child.y);
            }

        }

        //build up nodes array for easy drawing of the circles and interactivity after the fact
        nodes.push({
            "name": node.name,
            "cx": cx, "cy": cy,
            "similarity": node.similarity,
            "total": node.total,
            "r": total_reading_scale(node.total),
            "start": time_scale(new Date(node.start)),
            "end": time_scale(new Date(node.end))});

        return { "x" : cx, "y" : cy };
    } //end recursive node drawing function

    draw_hierarchy_structure(root);


    svg.selectAll("circle")
        .data(nodes)
        .enter()
        .append("circle")
        .attr("fill", function(d) {
            var colour_value = Math.round(sim_scale(d.similarity));
            return "rgb(" + colour_value + ",0," + colour_value + ")";
        })
        .attr("cx", function(d) { return d.cx; })
        .attr("cy", function(d) { return d.cy; })
        .attr("r", function(d) { return d.r; })
        .on("mouseover", function(d) {
            var x_pos = d.cx + d.r + 5;
            var y_pos = d.cy - 70;
            var msg = "ID: " + d.name + "<br>"
                + "Similarity: " + d.similarity.toFixed(4) + "<br>"
                + "Total Readings: " + d.total + "<br>";

            d3.select("#tooltip")
                .style("left", x_pos+"px")
                .style("top", y_pos+"px")
                .select("#value")
                .html(msg);
            d3.select("#tooltip").classed("hidden", false);

            //highlight the timeline
            var t_left = d.start + x_origin;
            var t_width = d.end - d.start;
            var t_top = y_origin + h;
            svg.append("rect")
                .attr("x", t_left)
                .attr("y", t_top)
                .attr("width", t_width)
                .attr("height", 5)
                .attr("fill", "blue");

        })
        .on("mouseout", function () {
            d3.select("#tooltip").classed("hidden", true);
            svg.selectAll("rect").remove();
        });


});

d3.select(self.frameElement).style("height", height + "px");