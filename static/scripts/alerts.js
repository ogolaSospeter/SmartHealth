//The function to dismiss the alerts after a 4 second delay
function dismissAlerts() {
    // Line 4 selects all alert elements
    const alerts = document.querySelectorAll('.alert');

    // Line 7 to 11 below loops through each alert and set a timeout to remove it
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.remove();
        }, 4000); // 4000 milliseconds = 4 seconds
    });
}
//Invoking the function execution
dismissAlerts();