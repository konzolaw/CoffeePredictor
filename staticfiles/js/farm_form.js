document.getElementById('farm-form').addEventListener('submit', function(event) {
            event.preventDefault(); // Prevent the default form submission

            const formData = new FormData(this);

            console.log('Form submission started.');
            console.log('Form data:', Object.fromEntries(formData.entries()));

            fetch(this.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': formData.get('csrfmiddlewaretoken')
                }
            })
            .then(response => {
                console.log('Server response status:', response.status);
                if (response.ok) {
                    // Attempt to parse JSON response
                    return response.json().catch(() => {
                        console.warn('Received non-JSON response from server. Assuming success.');
                        return { success: true, message: 'Database updated successfully.' }; // Assume success if response is not JSON
                    });
                } else {
                    console.error('Server responded with an error status. Redirecting to results page.');
                    window.location.href = '/results'; // Redirect to results page even on error
                    return { success: false, message: 'Redirecting to results page.' };
                }
            })
            .then(data => {
                console.log('Server response data:', data);
                if (data.success) {
                    alert(data.message || 'Data successfully updated!');

                    // Clear the form inputs
                    this.reset();
                }

                // Redirect to the results page to display predictions
                window.location.href = '/results';
            })
            .catch(error => {
                console.error('Error during form submission:', error);
                alert('An error occurred. Please try again later.');
            });
        });