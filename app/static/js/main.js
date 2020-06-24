//<script src="{{ url_for('static', filename='js/jquery.min.js') }}"></script> 
function react(reaction){
    $(`.${reaction}`).on('click', function(e){
        const Post = $(this).closest(".post")[0];
        e.preventDefault();
        $.post(
            "/react",
            {"id": $(Post).attr("id"),
            "reaction": reaction
        }).done(function(response){
            if (response.redirect){
                location.replace('/login');
            }
            $(Post).find(".Like").text(response.likes);
            $(Post).find(".Dislike").text(response.dislikes);
            if (response.liked)
              $(Post).find(".Like").removeClass("btn-secondary").addClass("btn-success");
            else
              $(Post).find(".Like").removeClass("btn-success").addClass("btn-secondary");
            if (response.disliked)
              $(Post).find(".Dislike").removeClass("btn-secondary").addClass("btn-danger");
            else
              $(Post).find(".Dislike").removeClass("btn-danger").addClass("btn-secondary");
        }).fail(function(){
            console.log("Server Error");
        });
    });
} 


const del = (e)=> {
    e.preventDefault();
    //console.log($(e.currentTarget).parent());
    $.post($(e.currentTarget).attr("href"),{}
    ).done(function(response){
        if (response.message == "deleted"){
            $($(e.currentTarget).parent()).remove();
        }
    });
}

$(function(){
    console.log();
    react("Like");
    react("Dislike");
    
})