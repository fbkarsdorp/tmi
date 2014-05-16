$(document).ready(function(){

        $("#search input").on("keydown",function(e){
                if(e.keyCode == "13"){
                        $("#results").html("");
                        $("#results").addClass("loading");
                        query = $(this).val();
                        console.log(query);
                        $.ajax({
                                url:"api",
                                data:{"q":query},
                                method:"POST",
                                dataType: "json",
                                success:function(data){
                                        $("#results").removeClass("loading");
                                        $("#counts").html(data.categories);
                                        $("#suggestion").html(data.suggest);
                                        $("#opdracht").html(data.opdracht);
                                        $("#hits").html(data.hits);
                                        $("#time").html(data.time);
                                        $("#results").html(data.html);
                                },
                                error:function(){
                                        $("#results").removeClass("loading");
                                        $("#results").html("oops, something went wrong...");
                                }
                        })
                }
        })

})
