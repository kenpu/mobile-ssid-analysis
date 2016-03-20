/*************************************************
*
* LITTLE HELPER METHODS
*
*************************************************/

// draws a rectangle
function draw_rect(rect_x, rect_y, rect_w, rect_h, rect_f, name, id) {
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

    if (rect_w > 20) {
        svg.append("text")
            .attr("x", (rect_x+2))
            .attr("y", (rect_y+20))
            .attr("font-size", "11pt")
            .text(id);
    }
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

//find smallest segment to set scale
function get_timeline_properties(d) {
    var start = new Date(d[0].segments[0].start),
        end = new Date(d[0].segments[0].start),
        smallest = end-start;

    d.forEach(function (l) {
        l.segments.forEach(function(s) {
            test_s = new Date(s.start);
            test_e = new Date(s.end);
            test_duration = test_e - test_s;

            if (test_s < start) start = test_s;
            if (test_e > end) end = test_e;
            if (test_duration < smallest) smallest = test_duration;
        });
    });

    if (smallest == 0) smallest = 1;
    return [start, end, smallest];
}

/*************************************************
*
* MAGIC NUMBER DECLARATIONS AND SETTINGS
*
*************************************************/

// SVG properties
var width = 4000; //this will get overwritten
var height = 300;
var padding = 40;

// graph properties
var w = width - padding*2; //this will get overwritten
var h = height - padding*2;
var x_origin = padding;
var y_origin = padding;

var locations;      // location data
var color_diff = 5;
var bar_height = 50;
var min_seg_size = 2;

var svg;


/*************************************************
*
* THIS IS THE MAIN ATTRACTION
*
*************************************************/

console.log("Look for data...");

var data_location = "../json_/segment.json";
if (getParameterByName('data_location'))
    data_location = getParameterByName('data_location');

d3.json(data_location, function(error, data) {
    if (error) throw error;

    locations = data;

    console.log("number of locations: "+locations.length);


    // set up colours to assign to locations
    var color = d3.scale.linear().domain([1,locations.length*color_diff])
      .interpolate(d3.interpolateHcl)
      .range([d3.rgb("#007AFF"), d3.rgb('#FFF500')]);

    console.log("color scale set up");

    // Set up timeline scale
    var timeline_attibutes = get_timeline_properties(locations);
    var timeline_start = timeline_attibutes[0];
    var timeline_end = new Date(timeline_start.getTime() + 3 * 86400000 );
    var smallest_duration = timeline_attibutes[2];
    //w = (timeline_end-timeline_start) * (min_seg_size/smallest_duration);

    width = w + padding*2;
    var time_scale = d3.time.scale()
        .domain([timeline_start, timeline_end])
        .range([0,w]);

    console.log("timeline start: "+timeline_start);
    console.log("timeline end: "+timeline_end);

    // create the svg to work with
    svg = d3.select("svg")
        .attr("width", width)
        .attr("height", height)
        .append("g")
        .attr("transform", "translate(x_origin, y_origin)");


    var xAxis = d3.svg.axis()
        .scale(time_scale)
        .orient("bottom");

    svg.append("g")
        .attr("class", "axis")
        .attr("transform", "translate(" + x_origin + "," + (y_origin+h) + ")")
        .call(xAxis);

    console.log("added timeline axis to svg");


    var index = 0;
    var legend = "";
    locations.forEach( function(l) {
        var name = l.location;
        var c = color(index*color_diff);

        console.log("=========================");
        console.log("adding to graph: "+name);
        console.log("number of segments: "+l.segments.length);
        console.log("color: "+c);

        legend = legend + index + " - " + name + "<br />";

        l.segments.forEach( function(s) {
            if (new Date(s.end) < timeline_end) {
                var r_x = x_origin+time_scale(new Date(s.start));
                var r_y = y_origin+h-bar_height-2;
                var r_width = time_scale(new Date(s.end)) - time_scale(new Date(s.start));

                draw_rect(r_x, r_y, r_width, bar_height, c, name, index);
            }
        });

        index = index +1;
    }); //end for locations

    d3.select("#legend")
        .select("#key")
        .html(legend);

    console.log("number of locations displayed: "+index);

});

d3.select(self.frameElement).style("height", height + "px");