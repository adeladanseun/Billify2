const DOMAIN = "http://localhost:8000";
const REDIRECT_TO_LOGIN = () => {
    window.location.href = "/auth/html/login.html";
}
const DISPLAY_MESSAGE = (message, priority="low", status="positive", time=5000) => {
    //message is the message to display, 
    // priority (low, urgent) to communicate urgency in color of popup, 
    // status (positive, neutral, negative) to show whether something succeded, failed or just a neutral message
    let body = document.getElementsByTagName('body')[0];
    console.log(body);
    let alert_message = document.createElement('div');
    alert_message.classList.add('popup_message', `priority_${priority}`, `status_${status}`)
    alert_message.textContent = message;
    body.appendChild(alert_message)
    setTimeout(() => {
        body.removeChild(alert_message)
    }, time ? time : 5000) 
}