document.addEventListener('DOMContentLoaded', function() {

  // Use buttons to toggle between views
  document.querySelector('#inbox').addEventListener('click', () => load_mailbox('inbox'));
  document.querySelector('#sent').addEventListener('click', () => load_mailbox('sent'));
  document.querySelector('#archived').addEventListener('click', () => load_mailbox('archive'));
  document.querySelector('#compose').addEventListener('click', compose_email);
  
  // By default, load the inbox
  load_mailbox('inbox');
  
  // Send Mail
  document.querySelector('#compose-form').addEventListener('submit', (event) => {
    event.preventDefault();
    send_mail(event.target)
  })
});

function compose_email() {

  // If user has opened an email.
  if (document.querySelector('.email-detail')) {
    document.querySelector('.email-detail').remove();
  }
  // Show compose view and hide other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'block';

  // Clear out composition fields
  document.querySelector('#compose-recipients').value = '';
  document.querySelector('#compose-subject').value = '';
  document.querySelector('#compose-body').value = '';
}

function load_mailbox(mailbox) {
  
  // If user has opened an email.
  if (document.querySelector('.email-detail')) {
    document.querySelector('.email-detail').remove();
  }
  // Show the mailbox and hide other views
  document.querySelector('#emails-view').style.display = 'block';
  document.querySelector('#compose-view').style.display = 'none';

  // Show the mailbox name
  document.querySelector('#emails-view').innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;

  fetch(`/emails/${mailbox}`)
  .then(response => response.json())
  .then(emails => {
    emails.forEach(email => {
      
      const emailView = document.querySelector('#emails-view');
      
      // Create email element
      let emailElement = document.createElement('div');
      emailElement.id = email.id;

      // Create spans
      let senderDiv = document.createElement('div');
      let subjectDiv = document.createElement('div');
      let timestampDiv = document.createElement('div');

      // Add class
      emailElement.className = 'email-div';
      senderDiv.className = 'sender';
      subjectDiv.className = 'subject';
      timestampDiv.className = 'timestamp';

      // Background
      if (email.read) {
        emailElement.style.background = 'lightgray';
      }
      else {
        emailElement.style.background = 'white';
      }
      // Text
      senderDiv.textContent = email.sender;
      subjectDiv.textContent = email.subject;
      timestampDiv.textContent = email.timestamp;

      // Add event listener
      emailElement.addEventListener('click', open_email)

      // Append Div
      emailElement.append(senderDiv, subjectDiv, timestampDiv);
      // If we're in inbox page
      if (mailbox === 'inbox') {
        // Create a button
        let btn = document.createElement('button');
        btn.textContent = 'Archive';
        btn.style.border = '1px solid black'
        btn.style.borderRadius = '5px'
        btn.addEventListener('click', () => archive_mail(email.id, true))
        emailElement.append(btn);
      }
      else if (mailbox === 'archive') {
        // Create a button
        let btn = document.createElement('button');
        btn.textContent = 'Unarchive';
        btn.style.border = '1px solid black'
        btn.style.borderRadius = '5px'
        btn.addEventListener('click', () => archive_mail(email.id, false))
        emailElement.append(btn);
      }
      emailView.append(emailElement);
    })
  })
}


function send_mail(event) {
  // Get the values of the form
  const recipients = event.querySelector('#compose-recipients').value
  const subject = event.querySelector('#compose-subject').value
  const body = event.querySelector('#compose-body').value
  
  // Check the values

  // Split and trim recipients
  const recipientList = recipients.split(',').map(email => email.trim());

  // Validate each email
  const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  for (const recipient of recipientList) {
    if (!emailPattern.test(recipient)) {
      alert("Please enter a valid email address.");
      return;
    }
  }

  // Check if subject and body is not empty
  if (subject.trim() === '' || body.trim() === '') {
    alert("Subject and Body cannot be empty");
    return;
  }

  // Make a POST request to /emails route
  fetch('/emails', {
    method: 'POST',
    body: JSON.stringify({
      recipients: recipients,
      subject: subject,
      body: body
    })
  })
  .then(response => response.json())
  .then(result => {
    if(result.error) {
      alert(result.error)
    }
    
    // Load the sent mailbox
    load_mailbox('sent')
  })
  .catch(error => {
    alert("Something went wrong.")
    load_mailbox('sent')
  })
}


function open_email() {
  fetch(`/emails/${this.id}`)
  .then(response => response.json())
  .then(result => {
    // Hide everything else
    document.querySelector('#emails-view').style.display = 'none';
    document.querySelector('#compose-view').style.display = 'none';  
    
    // Create a new div
    const emailDiv = document.createElement('div');
    emailDiv.className = 'email-detail'
    document.querySelector('body').append(emailDiv)

    emailDiv.innerHTML = `
    <div id="email-details">
    <h3>Sender: ${result.sender}</h3>
    <h4>Recipients: ${result.recipients}</h4>
    <h5>Subject: ${result.subject}</h5>
    <p>${result.body}</p>
    <p>Timestamp: ${result.timestamp}</p>
    <button id="reply-${result.id}">Reply</button>
    </div>
    `;
    
    document.querySelector(`#reply-${result.id}`).addEventListener('click', () => reply(result))

    // Mark as read
    fetch(`/emails/${result.id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        read: true
      })
    })
  })
  
}


function archive_mail(id, boolean) {
  event.stopPropagation()
  
  fetch(`/emails/${id}`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      archived: boolean
    })
  })
  .then(response => {
    if (response.ok && boolean) {
      load_mailbox('inbox');
    }
    else if (response.ok && !boolean) {
      load_mailbox('archive')
    }
  })
  
}

function reply(email) {
  compose_email()
  
  document.querySelector('#compose-recipients').value = `${email.sender}`;
  if (!email.subject.startsWith('Re: ')) {
    document.querySelector('#compose-subject').value = `Re: ${email.subject}`;
  }
  else {
    document.querySelector('#compose-subject').value = `${email.subject}`;
  }
  document.querySelector('#compose-body').value = `On ${email.timestamp} ${email.sender} Wrote: ${email.body}\n`;
}