document.addEventListener('DOMContentLoaded', function() {
    var calendarEl = document.getElementById('calendar');

    // Get today's date in the format 'YYYY-MM-DD'
    var today = new Date();
    var year = today.getFullYear();
    var month = String(today.getMonth() + 1).padStart(2, '0'); // Months are zero-based
    var day = String(today.getDate()).padStart(2, '0');
    var todayDate = `${year}-${month}-${day}`;

    var calendar = new FullCalendar.Calendar(calendarEl, {
        initialDate: todayDate,
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

            // Determine badge color based on event status
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

            let customHtml = `
                <div style="text-align: center;">
                    <span align="center" class="badge ${badgeClass}">
                        ${arg.event.extendedProps.category} - ${arg.event.start.toLocaleTimeString('nl-NL', { hour: '2-digit', minute: '2-digit' })}
                    </span>
                </div>
            `;
            return { html: customHtml };
        },
        eventClick: function(info) {
            showEventDetails(info.event);
        }
    });

    calendar.render();
    window.myCalendar = calendar;
});

function showEventDetails(event) {
    const today = new Date().toISOString();

    function formatTime(date) {
        return new Date(date).toLocaleTimeString('nl-NL', { hour: '2-digit', minute: '2-digit' });
    }

    document.getElementById('modal-event-category').textContent = event.extendedProps.category || 'N/A';
    document.getElementById('modal-event-start').textContent = formatTime(event.start);
    document.getElementById('modal-event-end').textContent = formatTime(event.end);
    document.getElementById('modal-event-apotheek').textContent = event.extendedProps.apotheek_naam || 'N/A';

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
