/*************************************************
*
* LITTLE HELPER METHODS
*
*************************************************/


/*************************************************
*
* MAGIC NUMBER DECLARATIONS AND SETTINGS
*
*************************************************/

// SVG properties
var width = 960;
var height = 600;

var nodes = [];
var links = [];

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

 

});

d3.select(self.frameElement).style("height", height + "px");