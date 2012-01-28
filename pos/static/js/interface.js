$(document).ready(function(){
    var PRODUCTS = ["credit"]; // To be populated
    var PANES = [$("div.customers_pane"), $("div.products_pane"), $("div.amount_pane"), $("div.confirmation_pane")];
    var VPANES = {"customers": 0, "products": 1, "amount": 2, "confirmation": 3};
    var currentPane = 0;

    var lastParse = {"type": ""};
    var lastParseLen = 0;

    var tabCompletes = [];

    for(var i = 1; i <= 9; i++){
        $("div.products_pane div.box"+i).data("index", i).click(function(){
            $this = $(this);
            var index = i;
            //setOrderbar($this.data("index"));
            setOrderbar("selection", $this.data("index"));
        }).each(function(){
            $this = $(this);
            PRODUCTS[$this.data("index")] = $this.attr("productslug");
        });
    }
    $("div.products_pane div.box0").data("index", 0).click(function(){
        $this = $(this);
        //setOrderbar("credit", null);
        setOrderbar("credit", "credit");
    }); 

    $("li.customer").each(function(i){
        $this = $(this);
        var username = $this.html();
        $this.click(function(){
            //setOrderbar(null, username);
            setOrderbar("customer", username);
            console.log(username);
        });
    });
    
    var alertParseError = function(){
        console.log("Parse Error");
    }

    var setOrderbar = function(pane, value){
        var stat = parseOrderbar();
        if(pane == "customer"){
            if(stat.type == "UT"){
                stat.transfer.username = value;
                stat.transfer.type = ">UA";
            }else{
                stat.username = value;
                stat.type = "U";
                stat.onNext = true;
            }
        }else if(pane == "amount"){
            if(stat.type == "UT"){
                stat.transfer.amount = value;
                stat.transfer.type = ">UA";
                stat.onNext = true;
            }else{
                stat.credit = value;
            }
        }else if(pane == "selection"){
            stat.selection = value;
            stat.type = "US";
        }else if(pane == "credit"){
            stat.type = "UC"
        }else{
            console.log("Error setorderbar", pane, value);
        }
        unparseOrderbar(stat);
    }
    
    var unparseOrderbar = function(stat, preString){
        preString = preString || $("input.orderbar").val();

        outstr = "";
        if(stat.type == ""){
            outstr = "";
        }else if(stat.type == "U"){
            outstr = stat.username + " ";
        }else if(stat.type == "US"){
            outstr = stat.username + " " + stat.selection;
        }else if(stat.type == "UC"){
            var creditStr = " credit ";
            if(preString.trim().substr(stat.username.length).trim().indexOf("c") == -1){
                creditStr = " 0 ";
            }

            if(stat.credit){
                outstr = stat.username + creditStr + stat.credit + " ";
            }else{
                outstr = stat.username + creditStr; 
            }
        }else if(stat.type == "UT"){
            if(stat.transfer.type == ">"){
                outstr = stat.username + " > ";
            }else if(stat.transfer.type == ">U"){
                outstr = stat.username + " > " + stat.transfer.username + " ";
            }else if(stat.transfer.type == ">UA"){
                outstr = stat.username + " > " + stat.transfer.username + " " + stat.transfer.amount + " ";
            }else{
                console.log("Error", stat);
            }
        }else{
            console.log("Error", stat);
        }
        $("input.orderbar").val(outstr).keyup();
    }
    
    $("input.orderbar").keydown(function(ev){
        if(ev.which == 13 || ev.which == 9){
            ev.preventDefault();
            return false;
        }
    }).keyup(function(ev){
        var $this = $(this);
        var stat = parseOrderbar();
        
        var tab = function(f){};
        var enter = function(f){};
        if(ev.which == 13){ // Enter
            ev.preventDefault();
            enter = function(f){return f();};
        }
        if(ev.which == 9){ // Tab
            ev.preventDefault();
            tab = function(f){return f();};
        }

        if(!stat || stat.error){
            alertParseError();
            return;
        }
        if(stat.type == "" || (stat.type == "U" && !stat.onNext)){
            // Choose a user
            console.log("Pane: user");
            switchToPane(VPANES.customers);

            limitCustomers(stat.username);
            
            enter(function(){

            });

            tab(function(){
                console.log(tabCompletes);
                if(tabCompletes.length == 1){
                    stat.username = tabCompletes[0];
                    unparseOrderbar(stat);
                }
            });
            
        }else if((stat.type == "US" && !stat.onNext) || (stat.type == "U" && stat.onNext)){
            // Make selection
            console.log("Pane: product");
            switchToPane(VPANES.products);
                        
            enter(function(){
                // Submit
            });

            tab(function(){

            });
        }else if(stat.type == "UC" && (stat.credit == 0 || !stat.onNext)){
            // Enter credit amount
            console.log("Pane: amount");
            switchToPane(VPANES.amount);             

            enter(function(){
                // Submit
            });

            tab(function(){

            });
        }else if(stat.type == "UT" && (stat.transfer.type == ">" || (stat.transfer.type == ">U" && !stat.onNext))){
            // Enter user to transfer to
            console.log("Pane: user (xfer)");
            switchToPane(VPANES.customers);

            limitCustomers(stat.transfer.username);
            
            enter(function(){

            });

            tab(function(){
                if(tabCompletes.length == 1){
                    stat.transfer.username = tabCompletes[0];
                    unparseOrderbar(stat);
                }
            });
        }else if(stat.type == "UT" && ((stat.transfer.type == ">U" && stat.onNext) || (stat.transfer.type == ">UA" && !stat.onNext))){
            // Enter amount to transfer
            console.log("Pane: amount (xfer)");
            switchToPane(VPANES.amount);
            
            enter(function(){
                // Submit
            });

            tab(function(){

            });
        }else{
            // Confirm
            console.log("Pane: confirm");
            switchToPane(VPANES.confirmation);

            enter(function(){
                // Refresh
            });

            tab(function(){

            });
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

    var limitCustomers = function(substr){
        substr = substr || "";
        tabCompletes = [];
        $("li.customer").each(function(){
            var $this = $(this);
            if($this.html().toLowerCase().match("^" + substr.toLowerCase())){
                $this.removeClass("nonmatch");
                tabCompletes.push($this.html());
            }else{
                $this.addClass("nonmatch");
            }
        });
    };
    
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
    
    /*
    setOrderbar = function(number, username){
        var state = parseOrderbar();
        console.log(state);
        number = number || state[0];
        username = username || state[1] || "";

        $("input.orderbar").val(number + " " + username);
        $("input.orderbar").change().focus();
    }
    */
    
    submitOrder = function(){
        var stat = parseOrderbar();
        console.log("ERROR");
        //product = PRODUCTS[state[0]];
        //username = state[1];
        
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
