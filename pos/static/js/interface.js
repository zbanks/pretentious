$(document).ready(function(){
    var PRODUCTS = ["credit"]; // To be populated
    var PANES = [$("div.customers_pane"), $("div.products_pane"), $("div.amount_pane"), $("div.confirmation_pane")];
    var VPANES = {"customers": 0, "products": 1, "amount": 2, "confirmation": 3};
    var currentPane = 0;

    var lastParse = {"type": ""};
    var lastParseLen = 0;

    for(var i = 1; i <= 9; i++){
        $("div.box"+i).data("index", i).click(function(){
            $this = $(this);
            PRODUCTS[$this.data("index")] = $this.attr("productslug");
            setOrderbar($this.data("index"));
        });
    }
    $("div.box0").data("index", 0).click(function(){
        $this = $(this);
        setOrderbar("credit", null);
    }); 

    $("li.customer").each(function(i){
        $this = $(this);
        var username = $this.html();
        $this.click(function(){
            setOrderbar(null, username);
        });
    });
    
    alertParseError = function(){
        console.log("Parse Error");
    }

    $("input.orderbar").keyup(function(ev){
        var $this = $(this);
        var stat = parseOrderbar();

        if(ev.which == 13){ // Enter
            ev.preventDefault();
        }
        
        if(!stat || stat.error){
            alertParseError();
            return;
        }
//US UC UT U
//UT< UT<U UT<UA
        if(stat.type == "" || (stat.type == "U" && !stat.onNext)){
            // Choose a user
            console.log("Pane: user");
            switchToPane(VPANES.customers);
        }else if((stat.type == "US" && !stat.onNext) || (stat.type == "U" && stat.onNext)){
            // Make selection
            console.log("Pane: product");
            switchToPane(VPANES.products);
        }else if(stat.type == "UC" && (stat.credit == 0 || !stat.onNext)){
            // Enter credit amount
            console.log("Pane: amount");
            switchToPane(VPANES.amount);
        }else if(stat.type == "UT" && (stat.transfer.type == ">" || (stat.transfer.type == ">U" && !stat.onNext))){
            // Enter user to transfer to
            console.log("Pane: user (xfer)");
            switchToPane(VPANES.customers);
        }else if(stat.type == "UT" && ((stat.transfer.type == ">U" && stat.onNext) || (stat.transfer.type == ">UA" && !stat.onNext))){
            // Enter amount to transfer
            console.log("Pane: amount (xfer)");
            switchToPane(VPANES.amount);
        }else{
            // Confirm
            console.log("Pane: confirm");
            switchToPane(VPANES.confirmation);
        }
        /*
        if(stat[0] == -1){
            // Go to pane 1
            switchPanes(currentPane, 0);
            currentPane = 0;
        }else if(!stat[1]){
            // Go to pane 2
            switchPanes(currentPane, 1);
            currentPane = 1;
        }else if(ev.which == 13){ // Enter
            switchPanes(currentPane, 2);
            currentPane = 2;
        }
        */
    }).change(function(){
        $(this).keydown(); 
    });
    
    /*
    parseOrderbar = function(){
        var parseIntOrCredit = function(x){
            if(x == "credit"){
                return x;
            }else{
                return parseInt(x);
            }
        }
        var parseExpr = /\s*([0-9]+|credit)\s+([a-zA-Z0-9_-]+)?\s* ?/i
        var ps = $("input.orderbar").val().match(parseExpr);
        if(!ps){
            return [-1, ""];
        }else if(ps.length > 2){
            return [parseIntOrCredit(ps[1]), ps[2] || ""];
        }else{
            return [parseIntOrCredit(ps[1]), ""];
        }
    } 
    */

    parseOrderbar = function(){
        var data;
        try{
            var rawtext = $("input.orderbar").val();
            var ps = parser.parse(rawtext);
            
            data = ps;
            data.error = false;

            lastParse = ps;
            lastParseLen = rawtext.length;
        }catch(ex){
            data = lastParse;
            data.error = true;
        }

        return data;
    }

    setOrderbar = function(number, username){
        var state = parseOrderbar();
        console.log(state);
        number = number || state[0];
        username = username || state[1] || "";

        $("input.orderbar").val(number + " " + username);
        $("input.orderbar").change().focus();
    }
    
    submitOrder = function(){
        var state = parseOrderbar();
        product = PRODUCTS[state[0]];
        username = state[1];
        
        $.get("/buy", {"username": username, "product": product}, function(data, textstatus ){
            updateMessages();
        });
    }

    updateMessages = function(){
        $.getJSON("/messages", function(data){
            console.log(data);
        });
    }

    switchToPane = function(showpane, hidepane){
        var hidepane = hidepane || currentPane;
        if(hidepane == showpane){
            return;
        }
        console.log(hidepane, showpane);
        console.log(PANES);
        var ANIM_LEN = 600; // length of animation in ms 
        if(hidepane < showpane){
            PANES[hidepane].animate({
                opacity: 0,
                left: "-100%",
            }, ANIM_LEN, "swing", function(){
                $(this).hide().css("left", "-100%")
            });

            PANES[showpane].css({ opacity: 0, display: "block", left: "100%"}).animate({
                opacity: 1,
                left: 0,
            }, ANIM_LEN, "swing", function(){
                ;
            });
        }else{
            PANES[hidepane].animate({
                opacity: 0,
                left: "100%",
            }, ANIM_LEN, "swing", function(){
                $(this).hide().css("left", "100%")
            });

            PANES[showpane].css({ opacity: 0, display: "block", left: "-100%"}).animate({
                opacity: 1,
                left: 0,
            }, ANIM_LEN, "swing", function(){
                ;
            });

        }
        currentPane = showpane;
    }
});
