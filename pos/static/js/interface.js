$(document).ready(function(){
    var PRODUCTS = ["credit"]; // To be populated
    var PANES = [$("div.products_pane"), $("div.customers_pane"), $("div.confirmation_pane")]
    var currentPane = 0;

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

    $("input.orderbar").keydown(function(ev){
        var $this = $(this);
        var stat = parseOrderbar();

        if(ev.which == 13){ // Enter
            ev.preventDefault();
        }

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
    }).change(function(){
        $(this).keydown(); 
    });

    parseOrderbar = function(){
        var parseIntOrCredit = function(x){
            if(x == "credit"){
                return x;
            }else{
                return parseInt(x);
            }
        }
        var parseExpr = /\s*([0-9]+|credit)\s+([a-zA-Z0-9_-]+)?\s*/i
        var ps = $("input.orderbar").val().match(parseExpr);
        if(!ps){
            return [-1, ""];
        }else if(ps.length > 2){
            return [parseIntOrCredit(ps[1]), ps[2] || ""];
        }else{
            return [parseIntOrCredit(ps[1]), ""];
        }
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

    switchPanes = function(hidepane, showpane){
        if(hidepane == showpane){
            return;
        }
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
    }
});
