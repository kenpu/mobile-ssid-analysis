/*************************************************
*
* LITTLE HELPER METHODS
*
*************************************************/

function get_nodes_min_count(n) {
    min_count = n[n.length-1].count;
    for (i=0;  i < n.length; i++) {
        min_count = Math.min(min_count, n[i].count);
    }
    return min_count;
}

function get_nodes_max_count(n) {
    max_count = n[0].count;
    for (i=0;  i < n.length; i++) {
        max_count = Math.max(max_count, n[i].count);
    }
    return max_count;
}

/*************************************************
*
* MAGIC NUMBER DECLARATIONS AND SETTINGS
*
*************************************************/

// SVG properties
var width = 1600;
var height = 960;

var min_radius = 5;
var max_radius = 50;
var min_loc_count;
var max_loc_count;

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

d3.json("../json_/location_transition.json", function(error, data) {
    if (error) throw error;

    links = data.transitions;

    data.locations.forEach( function(loc) {
        nodes[loc.id] = {name: loc.name, count: loc.count}
    });

    // Set up radius scale to size nodes according to count
    min_loc_count = get_nodes_min_count(nodes);
    max_loc_count = get_nodes_max_count(nodes);

    var r_scale = d3.scale.linear()
        .domain([get_nodes_min_count(nodes), get_nodes_max_count(nodes)])
        .range([min_radius, max_radius])
        .nice();

    var force = d3.layout.force()
        .nodes(d3.values(nodes))
        .links(links)
        .size([width, height])
        .linkDistance(60)
        .charge(-300)
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
        .attr("marker-end", "url(#end)");

    // define the nodes
    var node = svg.selectAll(".node")
        .data(force.nodes())
        .enter().append("g")
        .attr("class", "node")
        .call(force.drag);

    // add the nodes
    node.append("circle")
        .on("mouseover", function(d) {
            var x_pos = d.x + 20;
            var y_pos = d.y - 20;

            d3.select("#tooltip")
                .style("left", x_pos+"px")
                .style("top", y_pos+"px")
                .select("#value")
                .html(d.name);
            d3.select("#tooltip").classed("hidden", false);
        })
        .on("mouseout", function () {
            d3.select("#tooltip").classed("hidden", true);
        })
        .attr("r", 5);
        //.attr("r", function(d) { return r_scale(d.count); } );


    // add the curvy lines
    function tick() {
        path.attr("d", function(d) {
            var dx = d.target.x - d.source.x,
                dy = d.target.y - d.source.y,
                dr = Math.sqrt(dx * dx + dy * dy);
            return "M" +
                d.source.x + "," +
                d.source.y + "A" +
                dr + "," + dr + " 0 0,1 " +
                d.target.x + "," +
                d.target.y;
        });

        node
            .attr("transform", function(d) {
            return "translate(" + d.x + "," + d.y + ")"; });
    }


});

d3.select(self.frameElement).style("height", height + "px");