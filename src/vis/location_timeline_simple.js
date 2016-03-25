/*************************************************
*
* LITTLE HELPER METHODS
*
*************************************************/

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


//find filtered set of locations
function get_filtered_data(data) {
    return_data = [];
    //console.log(data);
    var last_location = "";
    data.forEach(function(d) {
        var d_location = marked(d.name);
        if (d_location.length > 0 && last_location != d_location) {
            d.name = d_location;
            return_data.push(d);
            last_location = d_location;
        }
    });
    console.log(return_data);
    return return_data;
}

function marked(s) {

    var return_value = "";
    marked_locations.forEach(function(l) {
        //console.log(s.indexOf(l["search"]) + " " + s + " " + l);
        if (s.indexOf(l["search"]) > -1) {
            //console.log("it is true!!");
            return_value = l["label"];
        }
    });

    return return_value;
}

function get_marked_index(s) {
    return_value = -1;
    marked_locations.forEach(function(l) {
        if (s.indexOf(l["label"]) > -1) {
            return_value = l["index"];
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
var width = 1100;
var height = 500;
var padding = 40;

// graph properties
var w = width - padding*2;
var h = height - padding*2;
var x_origin = padding;
var y_origin = padding;

var marked_locations = [{"search":"CAMPUS", "label":"Work", "index":0},
        {"search":"BISHOPTUTU", "label":"Home", "index":1},
        {"search":"DDSB", "label":"School", "index":2},
        {"search":"STARBUCKS", "label":"Coffee Shop", "index":3}];

// set up colours to assign to locations
//var locations_length = locations.length;
var color_diff = 5;
var locations_length = marked_locations.length;
var color = d3.scale.linear().domain([0,locations_length-1])
  .interpolate(d3.interpolateHcl)
  .range([d3.rgb("#007AFF"), d3.rgb('#FFF500')]);

console.log("color scale set up");


var bar_height = 50;
var min_seg_size = 2;
var days = 4;

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

    timeline = get_filtered_data(data);
    //locations = data;
    console.log("number of location changes: "+timeline.length);

    // create the svg to work with
    var svg = d3.select("svg")
        .attr("width", width)
        .attr("height", height)
        .append("g")
        .attr("transform", "translate(x_origin, y_origin)");

    console.log("created svg: "+width+" "+height);

    var cx = x_origin;
    var cy = y_origin + 20;
    var x_space = 150;
    var max_points_per_line = 7;
    var text_height = 100;
    var timeline_space = 50;

    var point_index = 1;
    timeline.forEach( function(t) {
        //var c = color(get_marked_index(t.name));
        var t_date = new Date(t.time);

        svg.append("circle")
            .attr("cx", cx)
            .attr("cy", cy)
            .attr("r", 10)
            .style("fill", "#666");

        svg.append("text")
            .attr("x", cx)
            .attr("y", cy+35)
            .attr("font-size", "11pt")
            .text(t.name);

        svg.append("text")
            .attr("x", cx)
            .attr("y", cy+35+20)
            .attr("font-size", "11pt")
            .text(t_date.toLocaleDateString());

        svg.append("text")
            .attr("x", cx)
            .attr("y", cy+35+20+20)
            .attr("font-size", "11pt")
            .text(t_date.toLocaleTimeString());

        svg.append("line")
            .attr("x1", cx)
            .attr("y1", cy)
            .attr("x2", cx+x_space)
            .attr("y2", cy)
            .attr("stroke-width", 2)
            .attr("stroke", "#666");

        if (point_index == max_points_per_line) {

            svg.append("line")
                .attr("x1", cx+x_space)
                .attr("y1", cy)
                .attr("x2", cx+x_space)
                .attr("y2", cy+text_height)
                .attr("stroke-width", 2)
                .attr("stroke", "#666");

            svg.append("line")
                .attr("x1", x_origin)
                .attr("y1", cy+text_height)
                .attr("x2", cx+x_space)
                .attr("y2", cy+text_height)
                .attr("stroke-width", 2)
                .attr("stroke", "#666");

            svg.append("line")
                .attr("x1", x_origin)
                .attr("y1", cy+text_height)
                .attr("x2", x_origin)
                .attr("y2", cy+text_height+timeline_space)
                .attr("stroke-width", 2)
                .attr("stroke", "#666");

            cx = x_origin;
            point_index = 1;
            cy = cy + text_height + timeline_space;
        } else {
            cx = cx + x_space;
            point_index = point_index+1;
        }




    }); //end for timeline





});

d3.select(self.frameElement).style("height", height + "px");