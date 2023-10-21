document.addEventListener('DOMContentLoaded', function(){
    document.querySelector('form').addEventListener('submit', function(event){
      event.preventDefault(); // Prevent the default form submit
      
      var formData = new FormData(this); // 'this' is the form element
      
      // Using fetch to post the form data
      fetch(this.action, { // 'this.action' is the form action attribute
        method: 'POST',
        body: formData,
        headers: {
          'X-Requested-With': 'XMLHttpRequest' // NEEDED for Django to recognize it as an AJAX request
        },
        credentials: 'same-origin' // This is needed to include the CSRF token
      })
      .then(response => response.json())
      .then(data => {
        // Here you would handle the response. For example, updating the DOM with the new computer components
        console.log('Success:', data);
        updateComputerTable(data.computer);
      })
      .catch((error) => {
        console.error('Error:', error);
      });
    });
});