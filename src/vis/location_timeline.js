/*************************************************
*
* LITTLE HELPER METHODS
*
*************************************************/

// draws a rectangle
function draw_rect(rect_x, rect_y, rect_w, rect_h, rect_f, name) {
    svg.append("rect")
        .attr("x", rect_x)
        .attr("y", rect_y)
        .attr("width", rect_w)
        .attr("height", rect_h)
        .attr("fill", rect_f)
        .on("mouseover", function() {
            var x_pos = rect_x;
            var y_pos = rect_y - 60;


            d3.select("#tooltip")
                .style("left", x_pos+"px")
                .style("top", y_pos+"px")
                .select("#value")
                .html(name);
            d3.select("#tooltip").classed("hidden", false);

        })
        .on("mouseout", function () {
            d3.select("#tooltip").classed("hidden", true);
        });
}

/*************************************************
*
* MAGIC NUMBER DECLARATIONS AND SETTINGS
*
*************************************************/

// SVG properties
var width = 2000;
var height = 300;
var padding = 40;

// graph properties
var w = width - padding*2;
var h = height - padding*2;
var x_origin = padding;
var y_origin = padding;

var locations;      // location data
var color_diff = 5;
var bar_height = 50;

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

console.log("Look for data...");

d3.json("../json_/segment.json", function(error, data) {
    if (error) throw error;

    locations = data;

    console.log("number of locations: "+locations.length);


    // set up colours to assign to locations
    var color = d3.scale.linear().domain([1,locations.length*color_diff])
      .interpolate(d3.interpolateHcl)
      .range([d3.rgb("#007AFF"), d3.rgb('#FFF500')]);

    console.log("color scale set up");

    // Set up timeline scale
    var timeline_start = new Date(locations[0].segments[0].start)
    var timeline_end = new Date(locations[locations.length-1].segments[locations[locations.length-1].segments.length-1].end)
    var time_scale = d3.time.scale()
        .domain([timeline_start, timeline_end])
        .range([0,w]);

    console.log("timeline start: "+timeline_start);
    console.log("timeline end: "+timeline_end);

    var xAxis = d3.svg.axis()
        .scale(time_scale)
        .orient("bottom");

    svg.append("g")
        .attr("class", "axis")
        .attr("transform", "translate(" + x_origin + "," + (y_origin+h) + ")")
        .call(xAxis);

    console.log("added timeline axis to svg");


    var index = 0;
    locations.forEach( function(l) {
        var name = l.location;
        var c = color(index*color_diff);

        console.log("=========================");
        console.log("adding to graph: "+name);
        console.log("number of segments: "+l.segments.length);
        console.log("color: "+c);

        l.segments.forEach( function(s) {
            var r_x = x_origin+time_scale(new Date(s.start));
            var r_y = y_origin+h-bar_height-2;
            var r_width = time_scale(new Date(s.end)) - time_scale(new Date(s.start));

            draw_rect(r_x, r_y, r_width, bar_height, c, name);
        });



        index = index +1;
    }); //end for locations

    console.log("number of locations displayed: "+index);

});

d3.select(self.frameElement).style("height", height + "px");