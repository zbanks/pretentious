$(document).ready(function(){
    PRODUCTS = ["credit"];

    for(var i = 1; i <= 9; i++){
        $("div.box"+i).data("index", i).click(function(){
            $this = $(this);
            console.log($this.data("index"));
            PRODUCTS[$this.data("index")] = $this.attr("productslug");
            setOrderbar($this.data("index"));
        });
    }
    $("div.box0").data("index", 0).click(function(){
        $this = $(this);
        console.log($this.data("index"));
        setOrderbar("credit");
    }); 

    $("li.customer").each(function(i){
        $this = $(this);
        $this.username = $this.html();
        $this.click(function(){
            console.log($this.username);
            setOrderbar(null, $this.username);

            //submitOrder();
        });
    });

    parseOrderbar = function(){
        parseExpr = /\s*([0-9]{1,2})\s+([a-zA-Z0-9_-]+)\s*/i
        var ps = $("input.orderbar").val().match(parseExpr);
        console.log(ps);
        if(!ps){
            return [0, ""];
        }else if(ps.length > 2){
            return [parseInt(ps[1]), ps[2]];
        }else{
            return [parseInt(ps[1]), ""];
        }
    } 

    setOrderbar = function(number, username){
        var state = parseOrderbar();
        number = number || state[0];
        username = username || state[1];

        $("input.orderbar").val(number + " " + username);
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
});
