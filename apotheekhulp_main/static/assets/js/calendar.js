document.addEventListener('DOMContentLoaded', function() {
    var calendarEl = document.getElementById('calendar');
    var userRole = document.getElementById('userRole') ? document.getElementById('userRole').dataset.role : 'ASSISTENT';

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
            showAddEventModal(info.dateStr);
        }
    });

    calendar.render();
    window.myCalendar = calendar;

    // Handle form submission
    document.getElementById('addEventForm').addEventListener('submit', function(event) {
        event.preventDefault(); // Prevent default form submission

        // Collect form data
        const data = {
            date: document.getElementById('modal-add-event-date').textContent,
            startTime: document.getElementById('start-time').value,
            endTime: document.getElementById('end-time').value,
            assistent: document.getElementById('assistent').value,
            apotheek: document.getElementById('apotheek').value
        };

        // Send form data to server
        fetch('/calendar/events/add/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify(data) // Ensure this contains the data in JSON format
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
        });
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
    document.getElementById('assistent').innerHTML = ''; // Clear existing options
    document.getElementById('apotheek').innerHTML = ''; // Clear existing options

    fetchOptions('/calendar/assistents/', 'assistent');
    fetchOptions('/calendar/apotheken/', 'apotheek');

    modal.show();
}

function fetchOptions(url, elementId) {
    fetch(url)
        .then(response => response.json())
        .then(data => {
            let options = data.map(item => `<option value="${item.id}">${item.name}</option>`).join('');
            document.getElementById(elementId).innerHTML = options;
        })
        .catch(error => {
            console.error(`Error fetching options from ${url}:`, error);
        });
}

function showEventDetails(event) {
    const today = new Date().toISOString();

    function formatTime(date) {
        return new Date(date).toLocaleTimeString('nl-NL', { hour: '2-digit', minute: '2-digit' });
    }

    const categoryElem = document.getElementById('modal-event-category');
    const startElem = document.getElementById('modal-event-start');
    const endElem = document.getElementById('modal-event-end');
    const apotheekElem = document.getElementById('modal-event-apotheek');

    if (!categoryElem || !startElem || !endElem || !apotheekElem) {
        console.error('Modal elements not found');
        return;
    }

    categoryElem.textContent = event.extendedProps.category || 'N/A';
    startElem.textContent = formatTime(event.start);
    endElem.textContent = formatTime(event.end);
    apotheekElem.textContent = event.extendedProps.apotheek_naam || 'N/A';

    const acceptBtn = document.getElementById('acceptBtn');
    const rejectBtn = document.getElementById('rejectBtn');
    if (event.extendedProps.status === 'noaction' && new Date(event.start) > new Date(today)) {
        acceptBtn.style.display = 'inline-block';
        rejectBtn.style.display = 'inline-block';
        acceptBtn.onclick = () => handleAction(event.id, 'accept');
        rejectBtn.onclick = () => handleAction(event.id, 'reject');
    } else {
        acceptBtn.style.display = 'none';
        rejectBtn.style.display = 'none';
    }

    const modal = new bootstrap.Modal(document.getElementById('eventDetailsModal'));
    modal.show();
}

function handleAction(eventId, action) {
    fetch(`/calendar/events/${eventId}/${action}/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({ action: action })
    })
    .then(response => response.json())
    .then(data => {
        if (window.myCalendar) {
            window.myCalendar.refetchEvents();
        }
        const modal = bootstrap.Modal.getInstance(document.getElementById('eventDetailsModal'));
        if (modal) {
            modal.hide();
        }
    })
    .catch(error => {
        console.error('Error handling action:', error);
    });
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
