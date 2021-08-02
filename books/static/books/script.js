like = document.querySelectorAll(".liked");
like.forEach((element) => {
  isread_handeler(element);
});

function isread_handeler(element) {
  element.addEventListener("click", () => {
    id = element.getAttribute("data-id");
    is_read = element.getAttribute("data-is_read");
    icon = document.querySelector(`#post-like-${id}`);
    count = document.querySelector(`#post-count-${id}`);

    form = new FormData();
    form.append("id", id);
    form.append("is_read", is_read);
    fetch("/read/", {
      method: "POST",
      body: form,
    })
      .then((res) => res.json())
      .then((res) => {
        if (res.status == 201) {
          if (res.is_read === "yes") {
            icon.src = "https://img.icons8.com/plasticine/100/000000/reading.png";
            element.setAttribute("data-is_read", "yes");
          } else {
            icon.src =
              "https://img.icons8.com/plasticine/100/000000/bookmark.png";
            element.setAttribute("data-is_read", "no");
          }
          count.textContent = res.like_count;
        }
      })
      .catch(function (res) {
        alert("Network Error. Please Check your connection.");
      });
  });
}

document.addEventListener('DOMContentLoaded', function() {

  document.querySelector('#inbox').addEventListener('click', () => load_mailbox('inbox'));
  document.querySelector('#sent').addEventListener('click', () => load_mailbox('sent'));
  document.querySelector('#compose').addEventListener('click', compose_email);
  load_mailbox('inbox');

});

function compose_email() {

  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'block';

  document.querySelector('#compose-recipients').value = '';
  document.querySelector('#compose-body').value = '';
  
}

function load_mailbox(mailbox) {
  
  document.querySelector('#emails-view').style.display = 'block';
  document.querySelector('#compose-view').style.display = 'none';
  document.querySelector('#emails-view').innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;

  fetch(`/emails/${mailbox}`)
  .then(response => response.json())
  .then(emails => {
    emails.forEach((element) => {
      if (mailbox == 'sent'){
        account = element.recipients;
      } else {
        account = element.sender;
      }
      var item = document.createElement('div');
      item.className = `card my-1 items`;
      item.innerHTML = `<div class="card-body" id="item-${element.id}">
        ${element.body} | ${account}
        </div>`;
      document.querySelector("#emails-view").appendChild(item); 

      item.addEventListener("click", () => {
        fetch(`/emails/${element.id}`)
        .then(response => response.json())
        .then(email => {
            document.querySelector("#emails-view").innerHTML = ""
            var mail = document.createElement("div");
            mail.className = `card`;
            mail.innerHTML = `<div class="card-body" style="white-space: pre-wrap;">
              Sender: ${element.sender}
              Recipients: ${element.recipients}
              Subject: ${element.subject}
              Time: ${element.timestamp}
              <br>${element.body}
              </div>`;
            document.querySelector("#emails-view").appendChild(mail);

            fetch(`/emails/${element.id}`, {
              method: 'PUT',
              body: JSON.stringify({
              read: true
              })
            })

            let reply = document.createElement("button");
            reply.className = `btn btn-outline-info my-2`;
            reply.textContent = "Reply";
            document.querySelector("#emails-view").appendChild(reply);
            reply.addEventListener("click", () => {

              document.querySelector('#emails-view').style.display = 'none';
              document.querySelector('#compose-view').style.display = 'block';
              
              document.querySelector('#compose-recipients').value = `${element.sender}`;
              document.querySelector('#compose-body').value = `\n${element.body}\n`;

            });
        })  
      })     
    });
  });
}
  
document.addEventListener('DOMContentLoaded', function() {

    document.querySelector('#compose-form').addEventListener('submit', function (event) {

      fetch('/emails', {
        method: 'POST',
        body: JSON.stringify({
          recipients: document.querySelector('#compose-recipients').value,
          body: document.querySelector('#compose-body').value
        })
      })
      .then( () => {
                  load_mailbox('sent');
                  })
      .then(result => {      
      console.log(result);
      });
      
      event.preventDefault();
      return false;
    });
});


  