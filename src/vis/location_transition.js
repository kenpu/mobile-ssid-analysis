/*************************************************
*
* LITTLE HELPER METHODS
*
*************************************************/

function get_nodes_min_total_time(n) {
    min_count = n[0].total_time;
    for (i=0;  i < Object.keys(n).length; i++) {
        min_count = Math.min(min_count, n[i].total_time);
    }
    return min_count;
}

function get_nodes_max_total_time(n) {
    max_count = n[0].total_time;
    for (i=0;  i < Object.keys(n).length; i++) {
        max_count = Math.max(max_count, n[i].total_time);
    }
    return max_count;
}

function humanize(sec) {
    if (sec < 60)
        return sec.toFixed(2) + " s";
    min = sec / 60.0;
    if (min < 60)
        return min.toFixed(2)+" m";
    hr = min / 60.0;
    return hr.toFixed(2)+" h";
}

// Great function to get url get variables
function getParameterByName(name, url) {
    if (!url) url = window.location.href;
    name = name.replace(/[\[\]]/g, "\\$&");// This is just to avoid case sensitiveness for query parameter name
    var regex = new RegExp("[?&]" + name + "(=([^&#]*)|&|#|$)"),
        results = regex.exec(url);
    if (!results) return null;
    if (!results[2]) return '';
    return decodeURIComponent(results[2].replace(/\+/g, " "));
}

function marked(s) {
    var m = ["CAMPUS", "BISHOPTUTU", "DDSB", "Starbucks"];

    var return_value = false;
    m.forEach(function(l) {
        console.log(s.indexOf(l) + " " + s + " " + l);
        if (s.indexOf(l) > -1) {
            console.log("it is true!!");
            return_value = true;
        }
    });

    return return_value;

}

/*************************************************
*
* MAGIC NUMBER DECLARATIONS AND SETTINGS
*
*************************************************/

// SVG properties
var width = 2000;
var height = 2000;

var min_radius = 10;
var max_radius = 30;
var min_loc_count;
var max_loc_count;

var min_stroke_width = 1;
var max_stroke_width = 10;
var min_tran_count;
var max_tran_count;

var nodes = {};
var links = {};

// create the svg to work with
var svg = d3.select("body").append("svg")
        .attr("width", width)
        .attr("height", height)
        .append("g");


/*************************************************
*
* THIS IS THE MAIN ATTRACTION
*
*************************************************/
console.log("got here");
var data_location = "../json_/location_transition.json";
if (getParameterByName('data_location'))
    data_location = getParameterByName('data_location');


d3.json(data_location, function(error, data) {
    if (error) throw error;



    links = data.transitions;
    var legend = "";

    data.locations.sort( function(a,b) {
            return a.id > b.id;
        })
        .forEach( function(loc) {
            nodes[loc.id] = {name: loc.name, count: loc.count, total_time: loc.total_time}
            legend = legend + loc.id + " - " + loc.name + "<br />";


        });

    d3.select("#legend")
        .select("#key")
        .html(legend);


    // Set up radius scale to size nodes according to count
    var r_scale = d3.scale.linear()
        .domain([get_nodes_min_total_time(nodes), get_nodes_max_total_time(nodes)])
        .range([min_radius, max_radius])
        .nice();


    var force = d3.layout.force()
        .nodes(d3.values(nodes))
        .links(links)
        .size([width, height])
        .linkDistance(100)
        .charge(-500)
        .on("tick", tick)
        .start();

    // build the arrow.
    svg.append("svg:defs").selectAll("marker")
        .data(["end"])      // Different link/path types can be defined here
        .enter().append("svg:marker")    // This section adds in the arrows
        .attr("id", String)
        .attr("viewBox", "0 -5 10 10")
        .attr("refX", 15)
        .attr("refY", -1.5)
        .attr("markerWidth", 6)
        .attr("color", "#666")
        .attr("markerHeight", 6)
        .attr("orient", "auto")
        .append("svg:path")
        .attr("d", "M0,-5L10,0L0,5");


    // add the links and the arrows
    var path = svg.append("svg:g").selectAll("path")
        .data(force.links())
        .enter().append("svg:path")
    //    .attr("class", function(d) { return "link " + d.type; })
        .attr("class", "link")
        .attr("marker-end", "url(#end)")
        .attr("stroke-width", 1)
        .attr("stroke", "#000");

    // define the nodes
    var node = svg.selectAll(".node")
        .data(force.nodes())
        .enter().append("g")
        .attr("class", "node")
        .attr("fill", "#ccc")
        .attr("stroke", "#000")
        .attr("stroke-width", function(d) {
            console.log(marked(d.name));
            if (marked(d.name)) return "1px";
            else return "0";
        })
        .call(force.drag);

    // add the nodes
    node.append("circle")
        .on("mouseover", function(d) {
            var x_pos = d.x + 20;
            var y_pos = d.y - 20;

            var msg = d.name+"<br/>"
                + " time spent: " + humanize(d.total_time);

            d3.select("#tooltip")
                .style("left", x_pos+"px")
                .style("top", y_pos+"px")
                .select("#value")
                .html(msg);
            d3.select("#tooltip").classed("hidden", false);
        })
        .on("mouseout", function () {
            d3.select("#tooltip").classed("hidden", true);
        })
        .attr("r", function(d) { return r_scale(d.total_time); } );



    node.append("text")
      .attr("dx", -6)
      .attr("dy", ".35em")
      .attr("font-family", "san-serif")
      .attr("font-size", "12px")
      .attr("fill", "#000")
      .text(function(d) { return d.index });


    // add the curvy lines
    function tick() {

        node
            .attr("transform", function(d) {
            return "translate(" + d.x + "," + d.y + ")"; });

        path.attr("d", function(d) {

            // Total difference in x and y from source to target
            diffX = d.target.x - d.source.x;
            diffY = d.target.y - d.source.y;

            // Length of path from center of source node to center of target node
            pathLength = Math.sqrt((diffX * diffX) + (diffY * diffY));

            // x and y distances from center to outside edge of target node
            offsetX = (diffX * (r_scale(d.target.total_time)-3)) / pathLength;
            offsetY = (diffY * (r_scale(d.target.total_time)-3)) / pathLength;

            return "M" + d.source.x + "," + d.source.y + "L" + (d.target.x - offsetX) + "," + (d.target.y - offsetY);
        });


    }


});

d3.select(self.frameElement).style("height", height + "px");