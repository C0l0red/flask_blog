//<script src="{{ url_for('static', filename='js/jquery.min.js') }}"></script> 
const comment = (className) => {
    $(className).on("submit", function(e){
      e.preventDefault();
      const commentPost = $(this).closest(".post")[0];
      console.log($(commentPost).attr("id"));
      $.post(
          "/comment",
          {
              "id" : $(commentPost).attr("id"),
              "comment": $(commentPost).find("[name='comment']").val(),
              "csrf_token": $(commentPost).find("[name='csrf_token']").val()
          }
      ).done(function(response){
          if ("error" in response){
            $.each(response.error.comment, function(index, value){
              let msg = `
            <div class='d-block invalid-feedback'>
              <small>${value}</small>
            </div>
            `;
            $(commentPost).find("[name='comment']").after(msg)
            })
            return;
          }
          let newComment = `
          <div class="d-flex flex-row comment-row m-t-0 comment mb-2" id="comment-${ response.public_id }">
              <div class="p-2"><img src="{{ url_for('static', filename='images/4.jpg') }}" alt="user" width="50" class="rounded-circle comment-user-image"></div>
              <div class="comment-text w-100">
                  <h6 class="font-medium comment-user">${ response.user.username }</h6> 
                  <span class="m-b-15 d-block comment-body"> ${ response.comment } </span>
                  <div class="comment-footer"> <span class="text-muted float-right comment-time"> ${ response.ago } </span>
                      <button type="button" class="btn btn-primary btn-sm" id='edit-${response.public_id}'>Edit</button>
                      <button type="button" class="btn btn-danger btn-sm delete-button" id='delete-${response.public_id}'>Delete</button> 
                  </div>
              </div>
          </div> 
          `;
          $(commentPost).find("[name='comment']").val("")
          if ($(commentPost).find(".comments").children().length == 3)
            $(commentPost).find(".comments").children().first().remove();
          $(commentPost).find(".comments").append(newComment);
          }).fail(function(){
              console.log("Server Error");
          });
    });

}


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

/*
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
*/
$(function(){
    console.log();
    react("Like");
    react("Dislike");
    comment(".commentform");
})