document.addEventListener('DOMContentLoaded', function() {
    var calendarEl = document.getElementById('calendar');
    // Get today's date in the format 'YYYY-MM-DD'
    var today = new Date();
    var year = today.getFullYear();
    var month = String(today.getMonth() + 1).padStart(2, '0'); // Months are zero-based
    var day = String(today.getDate()).padStart(2, '0');
    var todayDate = `${year}-${month}-${day}`;

    var calendar = new FullCalendar.Calendar(calendarEl, {
      initialDate: todayDate, // Set the initial date to today's date
      editable: true,
      selectable: true,
      businessHours: true,
      firstDay: 1,
      dayMaxEvents: true, // allow "more" link when too many events
      locale: 'nl',
      events: [

      ]
    });

    calendar.render();
  });
