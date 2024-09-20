var express = require("express");
var fs = require("fs");
var bodyParser = require("body-parser");
var formidable = require('formidable');
const credentials = require('./credentials.js');

var fortunes = [
    "Conquer your fears or htey will conquer you",
    "Rivers need springs",
    "Do not fear what you don't know",
    "You will have a pleasant surprise",
    "Whenever possible, keep it simple",
]

function serveStaticFiles (res,path,responseCode) {
    if (!responseCode) responseCode = 200;
    fs.readFile(__dirname + path,function(err,data) {
       if (err) {
           res.type("text/plain");
           res.send("500 - Internal Error");
           print(err);
       }
       else {
        res.type("text/html");
        res.send(data);
       }
    })

}
var app = express();
var handlebars = require("express3-handlebars").create({defaultLayout: 'main'});

app.engine('handlebars', handlebars.engine);
app.set('view engine', 'handlebars');
app.set('port', 3000);
app.disable("x-powered-by");
app.use(express.static(__dirname + "/public"));
app.use(require("cookie-parser")(credentials.cookieSecretes));

var port = app.get("port");

app.get("/", function (req,res) {
    if (req.cookies.name == undefined || req.cookies.userid == undefined) {
         res.cookie('name', 'nathnael');
         res.cookie('userid', 's_001');
    }
    console.log(req.cookies.name  + " " + req.cookies.userid);
    res.render('home');
 })
 
 app.get("/fortunes", function (req,res) {
          var randomFortune = fortunes[Math.floor(Math.random() * fortunes.length)];
          res.render("fortunes", {fortune: randomFortune});
 });
 app.post('/process', function (req,res) {
        try {
            var form = new formidable.IncomingForm();
            form.parse(req,function (err,fields,files) {
               if (err) return res.redirect(303,"/");
               console.log("recived fields: " + fields);
               console.log("recived files: ");
               console.log(files);
               res.redirect(303,'/about');
            })
        } catch (error) {
             console.log(error);
        }
 });
 app.get("/about", function (req,res) {
   serveStaticFiles(res,"/about.html");
 
 });
app.use(function(req,res) {
    res.type("text/plain");
    res.status(404);
    res.send("404 - Page not found");
})

app.use(function(err,req,res,next) {
    res.type("text/plain");
    res.status(500);
    res.send("500 - Internal Error");
})



app.listen(port , function () {
    console.log("Website running at " + port);
}) ;