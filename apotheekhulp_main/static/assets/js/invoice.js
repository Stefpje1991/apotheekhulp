document.addEventListener('DOMContentLoaded', function () {
    // Function to fetch event data and populate the modal
    window.openEditModal = function (eventId) {
        fetch(`/invoice/admin/get_event_data/${eventId}/`)
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    const event = data.event;

                    // Populate form fields with event data
                    document.getElementById('edit-event-id').value = event.id;
                    document.getElementById('modal-edit-event-date').value = event.date;
                    document.getElementById('start-edit-time').value = event.startTime;
                    document.getElementById('end-edit-time').value = event.endTime;
                    document.getElementById('edit_pauzeduur').value = event.pauzeDuur;

                    // Populate select options
                    populateSelect('edit_assistent', data.assistants, event.assistent);
                    populateSelect('edit_apotheek', data.pharmacies, event.apotheek);

                    // Show the modal
                    const modalElement = document.getElementById('editEventModal');
                    const modal = new bootstrap.Modal(modalElement);
                    modal.show();
                } else {
                    alert(`Error: ${data.error}`);
                }
            })
            .catch(error => {
                alert(`An error occurred: ${error.message}`);
            });
    };

    // Handle click events for "Bewerken" buttons
    document.addEventListener('click', function (event) {
        if (event.target.matches('.edit-btn-goed-te-keuren-door-assistent')) {
            const eventId = event.target.getAttribute('data-event-id');
            openEditModal(eventId);
        }
    });

    document.addEventListener('click', function (event) {
        if (event.target.matches('.accept_apotheek_event')) {
            const eventId = event.target.closest('tr').getAttribute('data-event-id');
            fetch(`/invoice/admin/accept_apotheek_event/${eventId}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({ event_id: eventId })
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    window.location.reload();  // Reload the page to reflect changes
                } else {
                    alert(`Error: ${data.error}`);
                }
            })
            .catch(error => {
                alert(`An error occurred: ${error.message}`);
            });
        }
    });

    const editEventForm = document.getElementById('editEventForm');

    // Handle form submission to update the event
    if (editEventForm) {
        editEventForm.addEventListener('submit', function (event) {
            event.preventDefault();  // Prevent default form submission

            const formData = new FormData(editEventForm);
            const payload = {
                'date': formData.get('date'),
                'startTime': formData.get('startTime'),
                'endTime': formData.get('endTime'),
                'pauzeDuur': formData.get('pauzeDuur'),
                'assistent': formData.get('assistent'),
                'apotheek': formData.get('apotheek')
            };

            const eventId = document.getElementById('edit-event-id').value;

            fetch(`/invoice/admin/edit_event_overview_pagina_goed_te_keuren_door_assistent_admin/${eventId}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify(payload)
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    window.location.reload();  // Reload the page to reflect changes
                    const modal = bootstrap.Modal.getInstance(document.getElementById('editEventModal'));
                    if (modal) {
                        modal.hide();  // Hide the modal on success
                    }
                } else {
                    alert(`Error: ${data.error}`);
                }
            })
            .catch(error => {
                alert(`An error occurred: ${error.message}`);
            });
        });
    }

    // Function to get CSRF token from cookies
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // Function to populate select elements with options
    function populateSelect(selectId, options, selectedValue) {
        const selectElement = document.getElementById(selectId);
        selectElement.innerHTML = ''; // Clear existing options
        options.forEach(option => {
            const optionElement = document.createElement('option');
            optionElement.value = option.id;
            optionElement.textContent = option.name; // Or however you need to display the option
            if (option.id == selectedValue) {
                optionElement.selected = true;
            }
            selectElement.appendChild(optionElement);
        });
    }
});
