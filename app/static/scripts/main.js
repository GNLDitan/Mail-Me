function logout() {
    fetch('/logout', {
        method: 'GET'
    }).then((_res) => {
        window.location.href = "/login";
    })
}

function gotoMessage(id, data) {
    fetch(`/mail/inbox/${id}`, {
        method: 'POST',
        body: JSON.stringify({ noteId: noteId, data: data })
    }).then((_res) => {
        window.location.href = _res.url
    })
}

function goToInbox(id) {
    window.location.href = "/mail/inbox"
}

function goToReply(id) {
    window.location.href = `/mail/inbox/${id}/reply`
}

function addEmailList(event) {
   if (event.which == 13) {
        event.preventDefault();
        var tc = document.getElementById('tagContainer');
        var node = document.createElement("span"); 
        var txt = document.createTextNode(event.currentTarget.value);
        
        node.classList.add('tag')
        node.appendChild(txt);

        tc.appendChild(node)

        addEmailSession(event.currentTarget.value)

        event.currentTarget.value = '';
      }
}

function addEmailSession(email) {
    fetch(`/mail/inbox/email/session/${email}`, {
        method: 'GET'
    })
}


