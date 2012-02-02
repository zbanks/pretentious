$(document).ready(function(){
    console.log("signup");
    
    fetching = false;
    $("input#id_username").keyup(function(){
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
});
