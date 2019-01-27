var App = (function () {

    return {
        OpenLinkInDiv: function (link, divSelector) {
            $(divSelector).empty();
            App.ShowLoading(divSelector);
            $(divSelector).load(link, function () { App.HideLoading(divSelector) });
        },

        ShowLoading: function (divSelector) {
            $(divSelector).append($( '<i class="loading-circle fa fa-circle-o-notch fa-spin" ></i>'));
        },

        HideLoading: function (divSelector) {
            $(divSelector).remove("i");
        }
    }
})()

var Animation = (function(){

  var colors = {
    "red" : "#678942"
    ,"purple" : "#685C79"
    ,"pinkred" : "#AC6C82"
    ,"peach" : "#DA727E"
    ,"yellow" : "#FFBC67"
  }
  var colorArr  = Object.keys(colors);

  var textColor = "#ffffff";

  var baseTime = 4
  var baseX = 40;
  var baseY = 45;


  var textSquence = [
    ["Hey...." , baseTime , 40,45] ,
    ["So...." , baseTime] ,
    ["I...." , baseTime/2] ,
    ["Didn't know what to\ndo...." , baseTime] ,
    ["Not as skilled as you are\n to draw...." ,baseTime] ,
    ["Not as skilled as you are\n to sing...." , baseTime] ,
    ["Not as skilled as you are\n to make pipelines...." , baseTime] ,
    //All the hahas
    ["Okay...sorry about that..\nshould stop" , baseTime , 0,40] ,
    ["Truth is\nThis is what i could\ncome up with" , baseTime] ,
  ]

  var hahas = [];

  for(var i = 0; i < 5 ; i++){
    hahas.push([ Math.random() > 0.5 ? "Haha" : "Hahaha" , baseTime*0.5*Math.random() , Math.random()*90 , Math.random()*90])
  }
  hahas.push([ "Ha ha" , baseTime*0.5 , 40,40])
  hahas.push([ "Ha....." , baseTime*0.5 , 40,40])

  var insertAt = 7
  textSquence = textSquence.slice(0,insertAt).concat(hahas).concat(textSquence.slice(insertAt))


  var images = {
    "wolf" : "/static/Images/wolf.jpg"
  }

  var balls = function(svg){
    //var data = Array(10000)
      var self = this;
      return {

        Init : function(data,delay,duration){
          /*
          d3.select("svg").selectAll("circle")
                          .transition()
                          .delay(delay-100)
                          .remove();
          */window.setTimeout(function(){
                  d3.select("svg")
                             .attr("width", window.innerWidth)
                            .attr("height", window.innerHeight)
                            .attr("viewBox" , "0 0 100 100")
                            .selectAll("circle")
                            .data(data)
                            .enter()
                            .append("circle")
                            .transition()
                            .duration(duration)
                            .attr("cx", function (d) { return Math.random()*100; })
                            .attr("cy", function (d) { return Math.random()*100; })
                             .attr("r", function (d) { return Math.random()*2; })
                             .style("fill", function(d) { return  colorArr[Math.floor(Math.random()*colorArr.length)] ; })
                             .style("fill-opacity" , 0.1);
          } , delay-100)

          return this;
        },
        Update : function(data,  delay , duration){

          return this;
        },
        Move : function(data ,delay,duration, factor){
            window.setTimeout(function(){

              d3.select("svg")
                .selectAll("circle")
                .data(data)
                .transition()
                .duration(duration)
                .attr("cx", function (d,i) { return d["x"] })
                .attr("cy", function (d,i) { return d["y"] })
                .attr("r", function (d) { return d["r"] * factor })

              d3.select("svg")
                .selectAll("circle")
                .data(data)
                .exit()
                .transition()
                .duration(duration/10)
                .style("opacitiy" , 0)
                .remove()
            } , delay)

            return this;
        }
      }

  }

  var animateTextSequence = function(elapsedTime , textSquence , html){

    var textElem = html["text"];

    textSquence.forEach(function(elem , i){
      text = elem[0];
      time = elem[1]*1000;
      x = elem[2] || 0;
      y = elem[3] || 0;
      console.log(elem,x,y)
      console.log(elapsedTime)

      textElem
        .transition()
        .duration(0)
        .delay(elapsedTime)
        .style("opacity" , 1)
        .style("position" , "absolute")
        .style("left" , x+"%")
        .style("top" , y+"%")

      textElem
        .transition()
        .duration(0.7*time)
        .delay(elapsedTime)
        .style("color" , colorArr[i%colorArr.length])
        .style( "font-size" , "5em")
        .text(text)

      textElem
        .transition()
        .delay(elapsedTime + 0.7*time)
        .duration(0.3*time)
        .style("opacity" , 0)

        elapsedTime += time;
    });

    return elapsedTime;
  }

  var startBalls = function(dataArr , estElapsedTime , timeToSta , timeToDisplay){

    dataArr.forEach(function(d,i){
        data = d[0]
        factor = d[2]
        balls().Init(data ,estElapsedTime + 0,timeToSta).Move(data , estElapsedTime + timeToSta, timeToDisplay ,factor);
        estElapsedTime += (timeToSta + timeToDisplay);
    });
    return estElapsedTime;
  }

  var animateBalls = function(estElapsedTime,timeToSta,timeToDisplay){
    imgData = []
    var factors = [0.05 , 0.08 , 0.05 , 0.1 , 0.1,0.5 , 0.1 , 0.2 , 0.2 , 0.1 , 0.1 , 0.1];
    factors.forEach(function(d,i){
      $.get({url :"/imagedata/"+(i+1), success: function(data){
        imgData.push([data , i , d]);
        if(i == factors.length-1){
          elapsedTime = startBalls(imgData.sort(function(a,b){return a[1] - b[1];}) , estElapsedTime , timeToSta ,timeToDisplay)
        }
      }})
    })
  }
  return {

    Start : function(){

      var viewBoxElem = d3.select("#viewBox");
      var viewBoxSVG = viewBoxElem.select("svg");
      var textElem = d3.select("#mytext");

      var timeToSta = 1000;
      var timeToDisplay = 5000;
      var elapsedTime = 0;
      var imgData = []
      elapsedTime = animateTextSequence(elapsedTime , textSquence , {"text" : textElem , "svg" : viewBoxSVG});


      animateBalls(elapsedTime,timeToSta,timeToDisplay)
      //elapsedTime = factors.length*(timeToSta + timeToDisplay)

      //elapsedTime = animateTextSequence(elapsedTime , textSquence , {"text" : textElem , "svg" : viewBoxSVG});

      /*
      viewBoxSVG.append("svg:image")
              .attr('x', 100)
              .attr('y', 100)
              .attr('width', window.innerWidth)
              .attr('height', window.innerHeight)
              .attr("xlink:href", images["wolf"])
      */
    }
  }
})()
