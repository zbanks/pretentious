$(document).ready(function(){
    console.log("signup");
    
    fetching = false;
    $("input#id_username").blur(function(){
        var $this = $(this);
        if(fetching){
            //return;
        }
        var kerberos = $this.val();
        $.get("/finger/" + kerberos, function(data){
            console.log(data);
            if(data){
                $("input#id_name").val(data);
                $("input#id_email").val(kerberos + "@mit.edu");
                $("input#id_balance").focus();
            }
        });
        /*
        if(email.indexOf("@m") != -1){ // Likely they're using an @mit.edu, want to catch early
            var kerberos = email.substr(0, email.indexOf("@m"));
            console.log(kerberos);
            fetching = true;
            $("input#id_username").val(kerberos);
            $.get("/finger/" + kerberos, function(data){
                console.log(data);
                $("input#id_name").val(data);
            });
        }
        */
    });
    
    $("input#id_balance").keyup(function(ev){
        var $this = $(this);
        var text = $this.val().replace(/[^0-9.-]/g, "")
        $this.val(text);
    }).keydown(function(ev){
        return "0123456789".indexOf(String.fromCharCode(ev.which)) != -1 || ev.which == 190 || ev.which == 189 || ev.which == 13 || ev.which == 9 || ev.which == 8; 
    });
});
