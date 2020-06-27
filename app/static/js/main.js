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
          <div class="d-flex flex-row comment-row m-t-0 comment mb-2" id="${ response.public_id }">
              <div class="p-2"><img src="/static/images/4.jpg" alt="user" width="50" class="rounded-circle comment-user-image"></div>
              <div class="comment-text w-100">
                  <h6 class="font-medium comment-user font-weight-bold">${ response.user.username }</h6> 
                  <span class="m-b-15 d-block comment-body"> ${ response.comment } </span>
                  <div class="comment-footer"> <span class="text-muted float-right comment-time"> ${ response.ago } </span>
                      <button type="button" class="btn btn-info btn-sm edit-comment" onclick='editComment()'>Edit</button>
                      <button type="button" class="btn btn-danger btn-sm delete-comment" onclick='del()'>Delete</button> 
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
              $(Post).find(".Like").removeClass("btn-secondary").addClass("btn-info");
            else
              $(Post).find(".Like").removeClass("btn-info").addClass("btn-secondary");
            if (response.disliked)
              $(Post).find(".Dislike").removeClass("btn-secondary").addClass("btn-danger");
            else
              $(Post).find(".Dislike").removeClass("btn-danger").addClass("btn-secondary");
        }).fail(function(){
            console.log("Server Error");
        });
    });
} 

const del = () => {
    let trigger = $(window.event.target);

    if ($(trigger).hasClass('delete-comment')){
      var target = $(trigger).closest(".comment");
      var type = "comment";
    }else if ($(trigger).hasClass('delete-post')){
      var target = $(trigger).closest('.post');
      var type = 'post';
    }
    
    $("#exampleModal").modal('show');
    $("#confirmDelete").on("click", function(e){
      $("#exampleModal").modal("hide");
      
      $.post(`/delete/${type}/${$(target).attr("id")}`
      ).done(function(response){
        if (response.status == "success")
          $(target).remove();
        
      }).fail(function(){console.log("Server error"); });
    });
  };

const editComment = () => {
  let trigger = $(window.event.target);
  let commentDiv = $(trigger).closest('.comment')
  let commentForm = $(commentDiv).closest('.post').find('.commentform')[0];
  $(commentForm).find("[name='comment']").val($(commentDiv).find('.comment-body').text());
  $(commentForm).find('.comment-submit').html(`
  <button type='button' class='btn btn-info' id='save-edit'>Save</button>
  <button class='btn btn-danger' type='button' id='cancel-edit'>Cancel</button>
  `);
  $(commentForm).find('#cancel-edit').on('click', (e) => {
      console.log($(commentForm).find('.comment-submit').html());
      //return;
      $(commentForm).find('.comment-submit').html(`<input type='submit' class='btn btn-info' value='Comment'>`);
      $(commentForm).find(`[name='comment']`).val('');
  });
  $(commentForm).find("#save-edit").on('click', (e) => {
      console.log($(this));
      //return;
      $.post(`/comment?edit=True`,
      {
        'id': $(commentDiv).attr('id'),
        'comment': $(commentForm).find(`[name='comment']`).val(),
        'csrf_token': $(commentForm).find(`[name='csrf_token']`).val()
      }
      ).done(function(response){
        console.log(response);
        //return;
        if (response.status == 'success'){
          $(commentDiv).find('.comment-body').text($(commentForm).find(`[name='comment']`).val());
          $(commentForm).find(`[name='comment']`).val('');
          $(commentForm).find('.comment-submit').html(`<input type='submit' class='btn btn-info' value='Comment'>`);
        }
      }).fail(function(response){console.log("Server Error")});
  });
};


$(function(){
    console.log("POLLY");
    react("Like");
    react("Dislike");
    comment(".commentform");
})