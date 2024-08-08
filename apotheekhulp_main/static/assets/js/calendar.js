document.addEventListener('DOMContentLoaded', function() {
    var calendarEl = document.getElementById('calendar');
    if (!calendarEl) {
        console.error('Element with ID "calendar" not found');
        return; // Exit if the element is not found
    }

    var userRole = calendarEl.getAttribute('data-user-role');
    var calendar = new FullCalendar.Calendar(calendarEl, {
        initialDate: new Date(),
        editable: true,
        selectable: true,
        businessHours: true,
        firstDay: 1,
        dayMaxEvents: true,
        locale: 'nl',
        events: function(fetchInfo, successCallback, failureCallback) {
            fetch('/calendar/events/')
                .then(response => response.json())
                .then(data => {
                    successCallback(data);
                })
                .catch(error => {
                    failureCallback(error);
                });
        },
        eventContent: function(arg) {
            let badgeClass = 'text-bg-warning'; // Default color
            switch (arg.event.extendedProps.status) {
                case 'Accepted':
                    badgeClass = 'text-bg-success';
                    break;
                case 'Declined':
                    badgeClass = 'text-bg-danger';
                    break;
                default:
                    badgeClass = 'text-bg-warning';
            }

            let customHtml = '';
            if (arg.event.extendedProps.user_role === 1 || arg.event.extendedProps.user_role === 2) {
                // Show category for Assistants
                customHtml = `
                    <div style="text-align: center;">
                        <span class="badge ${badgeClass}">
                            ${arg.event.extendedProps.category || 'No Category'} - ${arg.event.start.toLocaleTimeString('nl-NL', { hour: '2-digit', minute: '2-digit' })}
                        </span>
                    </div>
                `;
            } else if (arg.event.extendedProps.user_role === 3) {
                // Show assistant's name for Admins
                customHtml = `
                    <div style="text-align: center;">
                        <span class="badge ${badgeClass}">
                            ${arg.event.extendedProps.assistent_name || 'Unknown'} - ${arg.event.start.toLocaleTimeString('nl-NL', { hour: '2-digit', minute: '2-digit' })}
                        </span>
                    </div>
                `;
            }

            return { html: customHtml };
        },
        eventClick: function(info) {
            showEventDetails(info.event);
        },
        dateClick: function(info) {
            if (userRole === "3") {  // Note: userRole will be a string
                showAddEventModal(info.dateStr);
            } else {
                console.log('User role is not authorized to add events');
            }
        }
    });

    calendar.render();
    window.myCalendar = calendar;

    // Handle add event form submission
    document.getElementById('addEventForm').addEventListener('submit', function(event) {
        event.preventDefault(); // Prevent default form submission

        // Collect form data
        const data = {
            date: document.getElementById('modal-add-event-date').textContent,
            startTime: document.getElementById('start-time').value,
            endTime: document.getElementById('end-time').value,
            pauzeDuur: document.getElementById('pauzeduur').value,
            assistent: document.getElementById('assistent').value,
            apotheek: document.getElementById('apotheek').value,
        };

        // Validate data before sending
        if (!validateFormData(data)) {
            alert('Please fill in all the required fields.');
            return;
        }

        // Send form data to server
        fetch('/calendar/events/add/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify(data)
        })
        .then(response => response.json())
        .then(data => {
            if (window.myCalendar) {
                window.myCalendar.refetchEvents();
            }
            const modal = bootstrap.Modal.getInstance(document.getElementById('addEventModal'));
            if (modal) {
                modal.hide();
            }
        })
        .catch(error => {
            console.error('Error saving event:', error);
            alert('An error occurred while saving the event. Please try again.');
        });
    });

    // Handle edit event form submission
    document.getElementById('editEventForm').addEventListener('submit', function(event) {
        event.preventDefault(); // Prevent default form submission

        const eventId = document.getElementById('edit-event-id').value;
        const data = getEventData();

        updateEvent(eventId, data);
    });
});

function showAddEventModal(dateStr) {
    const modal = new bootstrap.Modal(document.getElementById('addEventModal'));
    const dateElem = document.getElementById('modal-add-event-date');

    if (!dateElem) {
        console.error('Date element not found');
        return;
    }

    dateElem.textContent = dateStr;
    document.getElementById('start-time').value = '';
    document.getElementById('end-time').value = '';
    document.getElementById('pauzeduur').value = '';
    document.getElementById('assistent').innerHTML = ''; // Clear existing options
    document.getElementById('apotheek').innerHTML = ''; // Clear existing options

    fetchOptions('/calendar/assistents/', 'assistent');
    fetchOptions('/calendar/apotheken/', 'apotheek');

    modal.show();
}

function fetchOptions(url, elementId) {
    return fetch(url)
        .then(response => response.json())
        .then(data => {
            let options = data.map(item => `<option value="${item.id}">${item.name}</option>`).join('');
            document.getElementById(elementId).innerHTML = options;
        })
        .catch(error => {
            console.error(`Error fetching options from ${url}:`, error);
        });
}

function fetchOptionsEdit(url, elementId, selectedValue) {
    return fetch(url)
        .then(response => response.json())
        .then(data => {
            let options = data.map(item => `<option value="${item.id}">${item.name}</option>`).join('');
            const selectElement = document.getElementById(elementId);
            selectElement.innerHTML = options;

            if (selectedValue) {
                selectElement.value = selectedValue; // Set the selected value
            }
        })
        .catch(error => {
            console.error(`Error fetching options from ${url}:`, error);
        });
}

function showEventDetails(event) {
    function formatTime(date) {
        return new Date(date).toLocaleTimeString('nl-NL', { hour: '2-digit', minute: '2-digit' });
    }

    const categoryElem = document.getElementById('modal-event-category');
    const startElem = document.getElementById('modal-event-start');
    const endElem = document.getElementById('modal-event-end');
    const pauzeduurElem = document.getElementById('modal-event-pauzeduur');
    const apotheekElem = document.getElementById('modal-event-apotheek');

    if (!categoryElem || !startElem || !endElem || !apotheekElem || !pauzeduurElem) {
        console.error('Modal elements not found');
        return;
    }

    categoryElem.textContent = event.extendedProps.category || 'N/A';
    startElem.textContent = formatTime(event.start);
    endElem.textContent = formatTime(event.end);
    pauzeduurElem.textContent = event.extendedProps.pauzeduur || 'N/A';
    apotheekElem.textContent = event.extendedProps.apotheek_naam || 'N/A';

    const acceptBtn = document.getElementById('acceptBtn');
    const rejectBtn = document.getElementById('rejectBtn');
    const editBtn = document.getElementById('editBtn');
    const deleteBtn = document.getElementById('deleteBtn');

    if (event.extendedProps.status === 'noaction' && (event.extendedProps.user_role === 1 || event.extendedProps.user_role === 2)) {
        acceptBtn.style.display = 'inline-block';
        rejectBtn.style.display = 'inline-block';
        deleteBtn.style.display = 'none';
        editBtn.style.display = 'none';
        acceptBtn.onclick = () => handleAction(event.id, 'accept');
        rejectBtn.onclick = () => handleAction(event.id, 'reject');
    } else {
        acceptBtn.style.display = 'none';
        rejectBtn.style.display = 'none';
        deleteBtn.style.display = 'inline-block';
        editBtn.style.display = 'inline-block';
        deleteBtn.onclick = () => handleDelete(event.id);
        editBtn.onclick = () => handleEdit(event);
    }

    const modal = new bootstrap.Modal(document.getElementById('eventDetailsModal'));
    modal.show();
}

function handleEdit(event) {
    const modal = new bootstrap.Modal(document.getElementById('editEventModal'));
    document.getElementById('edit-event-id').value = event.id;
    document.getElementById('modal-edit-event-date').value = event.start.toISOString().split('T')[0];
    document.getElementById('start-edit-time').value = event.start.toLocaleTimeString('nl-NL', { hour: '2-digit', minute: '2-digit' });
    document.getElementById('end-edit-time').value = event.end.toLocaleTimeString('nl-NL', { hour: '2-digit', minute: '2-digit' });
    document.getElementById('edit_pauzeduur').value = event.extendedProps.pauzeduur || '';

    // Fetch options and then set the selected value
    fetchOptionsEdit('/calendar/assistents/', 'edit_assistent');
    fetchOptionsEdit('/calendar/apotheken/', 'edit_apotheek');
    document.getElementById('edit_assistent').value = event.extendedProps.assistent_name
    document.getElementById('edit_apotheek').value = event.extendedProps.apotheek_naam
    modal.show();
}

function getEventData() {
    return {
        date: document.getElementById('modal-edit-event-date').value,
        startTime: document.getElementById('start-edit-time').value,
        endTime: document.getElementById('end-edit-time').value,
        pauzeDuur: document.getElementById('edit_pauzeduur').value,
        assistent: document.getElementById('edit_assistent').value,
        apotheek: document.getElementById('edit_apotheek').value
    };
}

function updateEvent(eventId, eventData) {
    const payload = {
        date: eventData.date,
        startTime: eventData.startTime,
        endTime: eventData.endTime,
        pauzeDuur: eventData.pauzeDuur,
        assistent: eventData.assistent,
        apotheek: eventData.apotheek
    };

    fetch(`/calendar/edit_event/${eventId}/edit/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify(payload)
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(data => {
                throw new Error(`Server error: ${data.message}`);
            });
        }
        return response.json();
    })
    .then(data => {
        if (data.status === 'success') {
            if (window.myCalendar) {
                window.location.reload();
            }
            const modal = bootstrap.Modal.getInstance(document.getElementById('editEventModal'));
            if (modal) {
                modal.hide();
            }
        } else {
            alert(`Error: ${data.error}`);
        }
    })
    .catch(error => {
        alert(`An error occurred: ${error.message}`);
    });
}

function handleDelete(eventId) {
    fetch(`/calendar/delete_event/${eventId}/delete/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken')
        }
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(data => {
                throw new Error(`Server error: ${data.message}`);
            });
        }
        return response.json();
    })
    .then(data => {
        if (data.status === 'success') {
            if (window.myCalendar) {
                window.myCalendar.refetchEvents();
            }
            const modal = bootstrap.Modal.getInstance(document.getElementById('eventDetailsModal'));
            if (modal) {
                modal.hide();
            }
        } else {
            alert(`Error: ${data.error}`);
        }
    })
    .catch(error => {
        alert(`An error occurred: ${error.message}`);
    });
}

function handleAction(eventId, action) {

    fetch(`/calendar/events/${eventId}/${action}/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        }
    })
    .then(response => {
        // Read the response body as JSON once
        return response.json().then(data => {
            // Check if the response is OK
            if (!response.ok) {
                throw new Error(`Server error: ${data.message || 'Unknown error'}`);
            }
            return data;  // Return the data to the next .then
        });
    })
    .then(data => {

        if (data.status === 'Accepted' || data.status === 'success' || data.status === 'Declined') {
            if (window.myCalendar) {
                window.myCalendar.refetchEvents();
            }
            const modal = bootstrap.Modal.getInstance(document.getElementById('eventDetailsModal'));
            if (modal) {
                modal.hide();
            }
        } else {
            alert(`Error: ${data.error}`);
        }
    })
    .catch(error => {
        alert(`An error occurred: ${error.message}`);
    });
}

function validateFormData(data) {
    return data.date && data.startTime && data.endTime && data.pauzeDuur && data.assistent && data.apotheek;
}

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
