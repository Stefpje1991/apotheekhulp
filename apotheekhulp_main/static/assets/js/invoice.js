document.addEventListener('DOMContentLoaded', function() {
    const buttonCreateInvoiceApotheek = document.getElementById('createInvoiceButton_apotheek');
    const saveInvoiceApotheekButton = document.getElementById('saveInvoiceApotheekButton');
    const createInvoiceApotheekModalElement = document.getElementById('createInvoiceApotheekModal');
    const invoiceApotheekCreationStatus = sessionStorage.getItem('invoiceApotheekCreationStatus');
    const downloadUrlApotheek = sessionStorage.getItem('downloadUrlApotheek');
    const buttonCreateInvoiceAssistent = document.getElementById('createInvoiceButton_assistent');
    const saveInvoiceButton = document.getElementById('saveInvoiceButton');
    const createInvoiceModalElement = document.getElementById('createInvoiceModal');
    const invoiceCreationStatus = sessionStorage.getItem('invoiceCreationStatus');
    const downloadUrl = sessionStorage.getItem('downloadUrl');
    const table = document.getElementById('tbl_nog_te_factureren_door_assistent_obj');
    const editEventForm = document.getElementById('editEventForm');
    const badges = document.querySelectorAll('.toggle-status-factuur-assistent');
    const currentUrl = window.location.pathname;
    const badgesApotheek = document.querySelectorAll('.toggle-status-factuur-apotheek');
    const addNewLinkButton = document.querySelector('.add-new-link-between-assistent-and-apotheek');
    const editLinkModalCheck = document.getElementById('editLinkModal');
    const dropdownItemsInvoiceStatus = document.querySelectorAll('.dropdown-item-invoice-status');
    const dropdownItemsInvoiceApotheekStatus = document.querySelectorAll('.dropdown-item-invoice-status-apotheek');
    const invoiceTableBody = document.querySelector('#invoiceTable tbody');
    const select = document.querySelector('#recordsPerPage');
    let searchFieldInvoiceTable = document.getElementById("searchInvoice");
    let invoiceTable = document.getElementById("invoiceTable");

    let createInvoiceApotheekModal;
    let createInvoiceModal;
    let editLinkModal;
    let modal;

    // Check if the success flag is set in localStorage
    if (localStorage.getItem('eventEditSuccess') === 'true') {
        // Show the SweetAlert
        Swal.fire({
            icon: 'success',
            title: 'Succes',
            text: 'Event werd aangepast.',
        });

        // Clear the flag
        localStorage.removeItem('eventEditSuccess');
    }
    // Function to fetch event data and populate the modal
    window.openEditModal = function(eventId) {
        const eventContainer = document.getElementById('row-id');
        if (eventContainer) {
            eventId = eventContainer.getAttribute('data-event-id')
        }
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
                    modal = new bootstrap.Modal(modalElement);
                    modal.show();
                } else {
                    alert(`Error: ${data.error}`);
                }
            })
            .catch(error => {
                alert(`An error occurred: ${error.message}`);
            });
    };

    if (createInvoiceApotheekModalElement) {
        createInvoiceApotheekModal = new bootstrap.Modal(createInvoiceApotheekModalElement);
    }

    if (buttonCreateInvoiceApotheek) {
        buttonCreateInvoiceApotheek.addEventListener('click', function() {
            const checkboxes = document.querySelectorAll('input[name="select_event"]');
            const selectedEvents = Array.from(checkboxes).filter(checkbox => checkbox.checked);

            // If no checkbox is selected, show the error alert
            if (selectedEvents.length === 0) {
                Swal.fire({
                    icon: 'error',
                    title: 'Geen selectie',
                    text: 'Selecteer minstens één item om een factuur aan te maken.'
                });
                return;
            }

            // Extract Apotheek IDs from selected events
            const apotheekIds = selectedEvents.map(checkbox => checkbox.closest('tr').querySelector('td:nth-child(7)').innerText.trim());

            // Check if all selected events have the same Apotheek
            const uniqueApotheekIds = [...new Set(apotheekIds)];
            if (uniqueApotheekIds.length > 1) {
                Swal.fire({
                    icon: 'error',
                    title: 'Meerdere Apotheken',
                    text: 'Selecteer alleen items van dezelfde Apotheek om een factuur aan te maken.'
                });
                return;
            }

            const eventsList = document.getElementById('selected-events-list');
            eventsList.innerHTML = ''; // Clear previous content

            selectedEvents.forEach(checkbox => {
                const eventId = checkbox.value;
                const eventRow = document.querySelector(`input[name="select_event"][value="${eventId}"]`).closest('tr');
                const cells = eventRow.querySelectorAll('td');
                const eventInfo = `
                <p>
                    Datum: ${cells[1].textContent.trim()}
                </p>
                <p>
                    Naam Assistent: ${cells[5].textContent.trim()}
                </p>
                <p>
                    Bedrag: ${cells[7].textContent.trim()}
                </p>
                <hr>
            `;
                eventsList.innerHTML += eventInfo;
            });

            // Show the create invoice modal using Bootstrap
            if (createInvoiceApotheekModal) {
                createInvoiceApotheekModal.show();
            }
        });
    }

    if (saveInvoiceApotheekButton) {
        saveInvoiceApotheekButton.addEventListener('click', function() {
            submitInvoiceApotheek();
        });
    }

    if (invoiceApotheekCreationStatus === 'success') {
        sessionStorage.removeItem('invoiceApotheekCreationStatus'); // Remove the flag
        sessionStorage.removeItem('downloadUrl'); // Clean up

        Swal.fire({
            icon: 'success',
            title: 'Succes',
            text: 'Factuur werd succesvol aangemaakt.',
            footer: downloadUrlApotheek ? `<a href="${downloadUrlApotheek}" target="_blank">Download de factuur</a>` : ''
        });
    }

    if (createInvoiceModalElement) {
        createInvoiceModal = new bootstrap.Modal(createInvoiceModalElement);
    }

    if (buttonCreateInvoiceAssistent) {
        buttonCreateInvoiceAssistent.addEventListener('click', function() {
            // Get all checkboxes with the name 'select_event'
            const checkboxes = document.querySelectorAll('input[name="select_event"]');
            const selectedEvents = Array.from(checkboxes).filter(checkbox => checkbox.checked);

            // If no checkbox is selected, show the error alert
            if (selectedEvents.length === 0) {
                Swal.fire({
                    icon: 'error',
                    title: 'Geen selectie',
                    text: 'Selecteer minstens één item om een factuur aan te maken.'
                });
            } else {
                // Populate the create invoice modal with selected events
                const eventsList = document.getElementById('selected-events-list');
                eventsList.innerHTML = ''; // Clear previous content

                selectedEvents.forEach(checkbox => {
                    const eventId = checkbox.value;
                    const eventRow = document.querySelector(`input[name="select_event"][value="${eventId}"]`).closest('tr');
                    const cells = eventRow.querySelectorAll('td');
                    const eventInfo = `
                        <p>
                            Datum: ${cells[1].textContent.trim()}
                        </p>
                        <p>
                            Naam Apotheek: ${cells[5].textContent.trim()}
                        </p>
                        <p>
                            Bedrag: ${cells[6].textContent.trim()}
                        </p>
                        <hr>
                    `;
                    eventsList.innerHTML += eventInfo;
                });

                // Show the create invoice modal using Bootstrap
                if (createInvoiceModal) { // Check if createInvoiceModal is defined
                    createInvoiceModal.show();
                } else {
                    console.error("Modal element 'createInvoiceModal' is not defined.");
                    // Optionally, you could show an alert to the user or handle the error gracefully
                }
            }
        });
    }

    if (saveInvoiceButton) {
        saveInvoiceButton.addEventListener('click', function() {
            submitInvoice();
        });
    }

    if (invoiceCreationStatus === 'success') {
        sessionStorage.removeItem('invoiceCreationStatus'); // Remove the flag
        sessionStorage.removeItem('downloadUrl'); // Clean up

        Swal.fire({
            icon: 'success',
            title: 'Succes',
            text: 'Factuur werd succesvol aangemaakt.',
            footer: downloadUrl ? `<a href="${downloadUrl}" target="_blank">Download de factuur</a>` : ''
        });
    }

    if (table) {
        table.addEventListener('click', function(event) {
            const row = event.target.closest('tr');
            if (row && row.querySelector('td')) {
                openDetailModal(row);
            }
        });
    }

    document.addEventListener('click', function(event) {
        if (event.target.matches('.edit-btn-goed-te-keuren-door-assistent')) {
            const eventId = event.target.getAttribute('data-event-id');
            openEditModal(eventId);
        }
    });

    document.addEventListener('click', function(event) {
        if (event.target.matches('.edit-btn-geweigerd-door-apotheek')) {
            const eventId = event.target.getAttribute('data-event-id');
            openEditModal(eventId);
        }
    });

    document.addEventListener('click', function(event) {
        if (event.target.matches('.accept_apotheek_event')) {
            const eventId = event.target.closest('tr').getAttribute('data-event-id');
            fetch(`/invoice/admin/accept_apotheek_event/${eventId}/`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCookie('csrftoken')
                    },
                    body: JSON.stringify({
                        event_id: eventId
                    })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'success') {
                        window.location.reload(); // Reload the page to reflect changes
                    } else {
                        alert(`Error: ${data.error}`);
                    }
                })
                .catch(error => {
                    alert(`An error occurred: ${error.message}`);
                });
        }
    });

    // Handle form submission to update the event
    if (editEventForm) {
        editEventForm.addEventListener('submit', function(event) {
            event.preventDefault(); // Prevent default form submission

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

                        const modal = bootstrap.Modal.getInstance(document.getElementById('editEventModal'));
                        if (modal) {
                            modal.hide(); // Hide the modal on success
                        }

                        // Set a flag in localStorage or sessionStorage
                        localStorage.setItem('eventEditSuccess', 'true');
                        window.location.reload(); // Reload the page to reflect changes

                    } else {
                        alert(`Error: ${data.error}`);
                    }
                })
                .catch(error => {
                    alert(`An error occurred: ${error.message}`);
                });
        });
    }

    badges.forEach(function(badge) {
        badge.addEventListener('click', function() {

            const invoiceId = badge.dataset.invoiceId;
            fetch('/invoice/admin/toggle_invoice_status_factuur_assistent/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCookie('csrftoken'), // Ensure you pass the CSRF token
                    },
                    body: JSON.stringify({
                        'invoice_id': invoiceId
                    }),
                })
                .then(response => response.json())
                .then(data => {
                    if (data.status) {
                        badge.classList.remove('text-bg-warning');
                        badge.classList.add('text-bg-success');
                        badge.textContent = 'Betaald';
                    } else {
                        badge.classList.remove('text-bg-success');
                        badge.classList.add('text-bg-warning');
                        badge.textContent = 'Te Betalen';
                    }
                     // Check if the current URL ends with the desired path
                    if (
                      currentUrl.endsWith('/invoice/admin/overview_all_invoices_assistenten_admin/')
                    ) {
                        location.reload(); // Refresh the page
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert('Er is een fout opgetreden bij het bijwerken van de factuurstatus.');
                });
        });
    });

    badgesApotheek.forEach(function(badge) {
        badge.addEventListener('click', function() {

            const invoiceId = badge.dataset.invoiceId;
            fetch('/invoice/admin/toggle_invoice_status_factuur_apotheek/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCookie('csrftoken'), // Ensure you pass the CSRF token
                    },
                    body: JSON.stringify({
                        'invoice_id': invoiceId
                    }),
                })
                .then(response => response.json())
                .then(data => {
                    if (data.status) {
                        badge.classList.remove('text-bg-warning');
                        badge.classList.add('text-bg-success');
                        badge.textContent = 'Betaald';
                    } else {
                        badge.classList.remove('text-bg-success');
                        badge.classList.add('text-bg-warning');
                        badge.textContent = 'Te Betalen';
                    }

                     // Refresh the page if needed
                    if (window.location.pathname.endsWith('/invoice/admin/overview_all_invoices_apotheken_admin/')) {
                        window.location.reload();
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert('Er is een fout opgetreden bij het bijwerken van de factuurstatus.');
                });
        });
    });

    if (editLinkModalCheck) {
        editLinkModal = new bootstrap.Modal(document.getElementById('editLinkModal'));
    }

    if (addNewLinkButton) {
        addNewLinkButton.addEventListener('click', function() {
            // Reset the form and modal title
            document.getElementById('editLinkForm').reset();
            document.getElementById('editModalLinkId').value = '';
            document.getElementById('editLinkModalLabel').textContent = 'Nieuwe Link Toevoegen';

            // Get the data attributes for IDs
            const assistentId = addNewLinkButton.getAttribute('data-assistent');
            const apotheekId = addNewLinkButton.getAttribute('data-apotheek');

            // Prepopulate the fields
            const assistentSelect = document.getElementById('id_assistent');
            const apotheekSelect = document.getElementById('id_apotheek');

            if (assistentId) {
                // Set the value of the assistent dropdown and disable it
                assistentSelect.value = assistentId;
                assistentSelect.disabled = true;
            } else {
                assistentSelect.disabled = false; // Enable dropdown if not prepopulated
            }

            if (apotheekId) {
                // Set the value of the apotheek dropdown and disable it
                apotheekSelect.value = apotheekId;
                apotheekSelect.disabled = true;
            } else {
                apotheekSelect.disabled = false; // Enable dropdown if not prepopulated
            }

            // Show the modal
            if (editLinkModal) {
                editLinkModal.show();
            }

        });
    }

    if (document.getElementById('editLinkForm')) {
        document.getElementById('editLinkForm').addEventListener('submit', function(e) {
            e.preventDefault(); // Prevent default form submission

            const form = this;

            // Temporarily enable the disabled fields
            const assistentSelect = document.getElementById('id_assistent');
            const apotheekSelect = document.getElementById('id_apotheek');

            const wasAssistentDisabled = assistentSelect.disabled;
            const wasApotheekDisabled = apotheekSelect.disabled;

            if (wasAssistentDisabled) assistentSelect.disabled = false;
            if (wasApotheekDisabled) apotheekSelect.disabled = false;

            // Collect form data
            const formData = new FormData(form);

            // Re-disable the fields if they were originally disabled
            if (wasAssistentDisabled) assistentSelect.disabled = true;
            if (wasApotheekDisabled) apotheekSelect.disabled = true;

            fetch(form.action, {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-CSRFToken': form.querySelector('[name=csrfmiddlewaretoken]').value,
                    },
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        // Handle success (e.g., close modal, show success message, etc.)
                        if (editLinkModal) {
                            editLinkModal.hide();
                        }

                        location.reload(); // Reload the page to show updated data
                    } else {
                        // Handle error (e.g., show error messages)
                        alert('An error occurred while saving the link.');
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert('An error occurred while saving the link.');
                });
        });
    }

    dropdownItemsInvoiceStatus.forEach(item => {
        item.addEventListener('click', function(event) {
            event.preventDefault(); // Prevent the default action of the link

            const status = this.getAttribute('data-status');
            filterInvoices(status);
        });
    });

    dropdownItemsInvoiceApotheekStatus.forEach(item => {
        item.addEventListener('click', function(event) {
            event.preventDefault(); // Prevent the default action of the link

            const status = this.getAttribute('data-status');
            filterInvoicesApotheek(status);
        });
    });

    if (select) {
        select.addEventListener('change', function () {
            const selectedValue = this.value.split(' ')[1];  // Haalt het nummer op van de optie (10, 25, 50)
            const url = new URL(window.location.href);
            url.searchParams.set('limit', selectedValue);  // Voegt de limit-parameter toe aan de URL
            window.location.href = url.toString();  // Stuurt de gebruiker naar de nieuwe URL met de parameter
        });
    };

    if (searchFieldInvoiceTable && invoiceTable) {
        searchFieldInvoiceTable.addEventListener("keyup", function() {
            let input = searchFieldInvoiceTable;
            let filter = input.value.toUpperCase(); // Zoek niet hoofdlettergevoelig
            let rows = invoiceTable.getElementsByTagName("tr");

            // Loop door alle rijen van de tabel (behalve de headers) en verberg degene die niet overeenkomen met de zoekterm
            for (let i = 1; i < rows.length; i++) { // Start bij 1 om de header over te slaan
                let shouldShow = false;
                // Loop door alle kolommen in een rij
                let columns = rows[i].getElementsByTagName("td");
                for (let j = 0; j < columns.length; j++) {
                    if (columns[j]) {
                        let txtValue = columns[j].textContent || columns[j].innerText;
                        if (txtValue.toUpperCase().indexOf(filter) > -1) {
                            shouldShow = true;
                            break; // Stop met zoeken in de huidige rij als er een match is
                        }
                    }
                }
                // Verberg of toon de rij op basis van het zoekresultaat
                rows[i].style.display = shouldShow ? "" : "none";
            }
        });
    }

});

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

function submitInvoice() {
        const form = document.getElementById('invoiceForm');
        const formData = new FormData(form);
        let createInvoiceModal;

        // Collect selected events and their corresponding totals from the modal
        const selectedEvents = Array.from(document.querySelectorAll('input[name="select_event"]:checked')).map(checkbox => ({
            id: checkbox.value,
            totaalbedragWerk: checkbox.closest('tr').querySelector('td:nth-child(7)').textContent.trim().replace('€ ', '') // Adjust if necessary
        }));

        if (formData.get('factuurnummer') && formData.get('factuurdatum') && selectedEvents.length > 0) {
            selectedEvents.forEach((event, index) => {
                formData.append(`selected_events[${index}][id]`, event.id);
                formData.append(`selected_events[${index}][totaalbedragWerk]`, event.totaalbedragWerk);
            });

            fetch('/invoice/create_invoice/', {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                    }
                })
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'success') {
                        // Show the create invoice modal using Bootstrap
                        if (createInvoiceModal) { // Check if createInvoiceModal is defined
                            createInvoiceModal.hide();
                        } else {
                            console.error("Modal element 'createInvoiceModal' is not defined.");
                            // Optionally, you could show an alert to the user or handle the error gracefully
                        }
                        // Store success flag and download URL
                        sessionStorage.setItem('invoiceCreationStatus', 'success');
                        sessionStorage.setItem('downloadUrl', data.download_url); // Ensure this URL is included in the response
                        window.location.reload(); // Reload the page to see the changes
                    } else {
                        if (createInvoiceModal) { // Check if createInvoiceModal is defined
                            createInvoiceModal.hide();
                        } else {
                            console.error("Modal element 'createInvoiceModal' is not defined.");
                            // Optionally, you could show an alert to the user or handle the error gracefully
                        }
                        Swal.fire({
                            icon: 'error',
                            title: 'Foutmelding',
                            text: data.message
                        });
                    }
                })
                .catch(error => {
                    if (createInvoiceModal) { // Check if createInvoiceModal is defined
                        createInvoiceModal.hide();
                    } else {
                        console.error("Modal element 'createInvoiceModal' is not defined.");
                        // Optionally, you could show an alert to the user or handle the error gracefully
                    }
                    console.error('Error:', error);
                    Swal.fire({
                        icon: 'error',
                        title: 'Foutmelding',
                        text: 'Er is een fout opgetreden bij het verzenden van de aanvraag.'
                    });
                });
        } else {
            if (createInvoiceModal) { // Check if createInvoiceModal is defined
                createInvoiceModal.hide();
            } else {
                console.error("Modal element 'createInvoiceModal' is not defined.");
                // Optionally, you could show an alert to the user or handle the error gracefully
            }
            Swal.fire({
                icon: 'warning',
                title: 'Ongeldige Invoer',
                text: 'Vul alstublieft alle velden in en selecteer minstens één event.'
            });
        }
    }

function submitInvoiceApotheek() {
        const form = document.getElementById('invoiceFormApotheek');
        const formData = new FormData(form);
        let createInvoiceApotheekModal;

        // Collect selected events and their corresponding totals from the modal
        const selectedEvents = Array.from(document.querySelectorAll('input[name="select_event"]:checked')).map(checkbox => ({
            id: checkbox.value,
            totaalbedragWerk: checkbox.closest('tr').querySelector('td:nth-child(8)').textContent.trim().replace('€ ', '') // Adjust if necessary
        }));

        if (formData.get('factuurnummer') && formData.get('factuurdatum') && selectedEvents.length > 0) {
            selectedEvents.forEach((event, index) => {
                formData.append(`selected_events[${index}][id]`, event.id);
                formData.append(`selected_events[${index}][totaalbedragWerk]`, event.totaalbedragWerk);
            });

            fetch('/invoice/admin/create_invoice_apotheek/', {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                    }
                })
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'success') {
                        createInvoiceApotheekModal.hide();
                        // Store success flag and download URL
                        sessionStorage.setItem('invoiceApotheekCreationStatus', 'success');
                        sessionStorage.setItem('downloadUrlApotheek', data.download_url); // Ensure this URL is included in the response
                        window.location.reload(); // Reload the page to see the changes
                    } else {
                        createInvoiceApotheekModal.hide(); // Hide the modal
                        Swal.fire({
                            icon: 'error',
                            title: 'Foutmelding',
                            text: data.message
                        });
                    }
                })
                .catch(error => {
                    createInvoiceApotheekModal.hide(); // Hide the modal
                    console.error('Error:', error);
                    Swal.fire({
                        icon: 'error',
                        title: 'Foutmelding',
                        text: 'Er is een fout opgetreden bij het verzenden van de aanvraag.'
                    });
                });
        } else {
            createInvoiceApotheekModal.hide(); // Hide the modal
            Swal.fire({
                icon: 'warning',
                title: 'Ongeldige Invoer',
                text: 'Vul alstublieft alle velden in en selecteer minstens één event.'
            });
        }
    }

function openDetailModal(row) {
        const datum = row.cells[0].textContent;
        const startuur = row.cells[1].textContent;
        const einduur = row.cells[2].textContent;
        const pauzeduur = row.cells[3].textContent;

        // Extract additional data attributes from the row
        const link = row.getAttribute('data-link');
        const aanwezigeTijd = row.getAttribute('data-aanwezige-tijd');
        const gewerkteTijd = row.getAttribute('data-gewerkte-tijd');
        const uurtariefAssistent = row.getAttribute('data-uurtarief-assistent');
        const uurtariefApotheek = row.getAttribute('data-uurtarief-apotheek');
        const afstandInKilometers = row.getAttribute('data-afstand-in-kilometers');
        const kilometervergoeding = row.getAttribute('data-kilometervergoeding');
        const totaalbedragWerk = row.getAttribute('data-totaalbedrag-werk');
        const bedragFietsvergoeding = row.getAttribute('data-bedrag-fietsvergoeding');
        const totaalbedrag_zonder_fietsvergoeding = row.getAttribute('data-totaalbedrag-zonder-fietsvergoeding');
        const totaalbedrag = row.getAttribute('data-totaalbedrag');

        // Populate the detail modal with the row data
        document.getElementById('detailFactuurOpenstaandAssistent_event_date').textContent = datum;
        document.getElementById('detailFactuurOpenstaandAssistent_start_time').textContent = startuur;
        document.getElementById('detailFactuurOpenstaandAssistent_end_time').textContent = einduur;
        document.getElementById('detailFactuurOpenstaandAssistent_pauzeduur').textContent = pauzeduur;
        document.getElementById('detailFactuurOpenstaandAssistent_aanwezige_tijd').textContent = aanwezigeTijd;
        document.getElementById('detailFactuurOpenstaandAssistent_gewerkte_tijd').textContent = gewerkteTijd;
        document.getElementById('detailFactuurOpenstaandAssistent_uurtarief').textContent = '€ ' + uurtariefAssistent;
        document.getElementById('detailFactuurOpenstaandAssistent_totaalbedrag_zonder_fietsvergoeding').textContent = '€ ' + totaalbedrag_zonder_fietsvergoeding;

        // Show or hide the kilometervergoeding section
        const kilometervergoedingElement = document.getElementById('detailFactuurOpenstaandAssistent_kilometervergoeding');
        const afstandInKilometersElement = document.getElementById('detailFactuurOpenstaandAssistent_afstand_in_kilometers');
        const bedragFietsvergoedingElement = document.getElementById('detailFactuurOpenstaandAssistent_totale_kilometervergoeding');
        const totaalBedragElement = document.getElementById('detailFactuurOpenstaandAssistent_totaalbedrag');
        if (kilometervergoeding === 'True') {
            afstandInKilometersElement.textContent = afstandInKilometers; // Or any appropriate message
            afstandInKilometersElement.parentElement.style.display = 'block'; // Show the element
            bedragFietsvergoedingElement.textContent = '€ ' + bedragFietsvergoeding;
            bedragFietsvergoedingElement.parentElement.style.display = 'block'; // Show the element
            totaalBedragElement.textContent = '€ ' + totaalbedrag;
            totaalBedragElement.parentElement.style.display = 'block';
        } else {
            afstandInKilometersElement.parentElement.style.display = 'none'; // Hide the element
            bedragFietsvergoedingElement.parentElement.style.display = 'none';
            totaalBedragElement.parentElement.style.display = 'none';
        }

        // Show the detail modal
        const detailModalElement = document.getElementById('detailFactuurOpenstaandAssistent');
        const detailModal = new bootstrap.Modal(detailModalElement);
        detailModal.show();
    }

function filterInvoices(status) {
        // Fetch the invoices based on the selected status
        fetch(`/invoice/admin/get_filtered_invoices/?status=${status}`)
            .then(response => response.json())
            .then(data => {
                updateTable(data);
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Er is een fout opgetreden bij het ophalen van de facturen.');
            });
    }

function filterInvoicesApotheek(status) {
        // Fetch the invoices based on the selected status
        fetch(`/invoice/admin/get_filtered_invoices_to_apotheek/?status=${status}`)
            .then(response => response.json())
            .then(data => {
                updateTableApotheekInvoices(data);
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Er is een fout opgetreden bij het ophalen van de facturen.');
            });
    }

function updateTable(invoices) {
    const invoiceTableBody = document.querySelector('#invoiceTable tbody'); // Ensure this selector matches your HTML
    if (!invoiceTableBody) {
        console.error('Table body not found.');
        return;
    }
    invoices.sort((a, b) => {
        // Eerst sorteren op invoice_date
        const dateComparison = parseDate(b.invoice_date) - parseDate(a.invoice_date);

        if (dateComparison !== 0) {
            return dateComparison; // Als de datums niet gelijk zijn, gebruik de datum-sortering
        }

        // Als de datums gelijk zijn, sorteren op last_name (alfabetisch)
        const lastNameA = a.invoice_created_by_name.toLowerCase();
        const lastNameB = b.invoice_created_by_name.toLowerCase();

        if (lastNameA < lastNameB) return -1;
        if (lastNameA > lastNameB) return 1;
        return 0; // Als beide gelijk zijn
    });

    // Clear existing rows
    invoiceTableBody.innerHTML = '';

    // Add new rows
    invoices.forEach(invoice => {
        const isPaid = invoice.invoice_paid === 'Betaald';

        const row = document.createElement('tr');
        row.innerHTML = `
            <td class="text-center"><a href="${invoice.invoice_pdf_url}">${invoice.invoice_number}</a></td>
            <td class="text-center">
                <div class="d-flex align-items-center">
                    <div class="avatar me-2">
                        <img src="${invoice.invoice_created_by_picture_url || '/static/assets/img/avatars/default.jpg'}" class="w-px-40 h-auto rounded-circle" />
                    </div>
                    <div>${invoice.invoice_created_by_name}<br><small>${invoice.invoice_created_by_company}</small></div>
                </div>
            </td>
            <td class="text-center">€ ${invoice.invoice_amount}</td>
            <td class="text-center">€ ${invoice.invoice_btw}</td>
            <td class="text-center">${invoice.invoice_date}</td>
            <td class="text-center">
                <span class="badge text-bg-${isPaid ? 'success' : 'warning'} toggle-status-factuur-assistent" data-invoice-id="${invoice.id}">
                    ${isPaid ? 'Betaald' : 'Te Betalen'}
                </span>
            </td>
        `;
        invoiceTableBody.appendChild(row);
    });

    // Reattach event listeners for the badges
    const badges = document.querySelectorAll('.toggle-status-factuur-assistent');
    badges.forEach(badge => {

        badge.addEventListener('click', function() {
            const invoiceId = badge.dataset.invoiceId;

            fetch('/invoice/admin/toggle_invoice_status_factuur_assistent/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken'),
                },
                body: JSON.stringify({ 'invoice_id': invoiceId }),
            })
            .then(response => response.json())
            .then(data => {
                if (data.status) {
                    badge.classList.remove('text-bg-warning');
                    badge.classList.add('text-bg-success');
                    badge.textContent = 'Betaald';
                } else {
                    badge.classList.remove('text-bg-success');
                    badge.classList.add('text-bg-warning');
                    badge.textContent = 'Te Betalen';
                }

                // Refresh the page if needed
                if (window.location.pathname.endsWith('/invoice/admin/overview_all_invoices_assistenten_admin/')) {
                    window.location.reload();
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Er is een fout opgetreden bij het bijwerken van de factuurstatus.');
            });
        });
    });
}

function updateTableApotheekInvoices(invoices) {
    const invoiceTableBody = document.querySelector('#invoiceTable tbody'); // Ensure this selector matches your HTML
    if (!invoiceTableBody) {
        console.error('Table body not found.');
        return;
    }
    console.log(Array.isArray(invoices), invoices);
    console.log(invoices)
    console.log(typeof(invoices))
    invoices.invoices.sort((a, b) => {
        // Eerst sorteren op invoice_date
        const dateComparison = parseDate(b.invoice_date) - parseDate(a.invoice_date);

        if (dateComparison !== 0) {
            return dateComparison; // Als de datums niet gelijk zijn, gebruik de datum-sortering
        }

        // Als de datums gelijk zijn, sorteren op last_name (alfabetisch)
        const lastNameA = a.invoice_created_by_name.toLowerCase();
        const lastNameB = b.invoice_created_by_name.toLowerCase();

        if (lastNameA < lastNameB) return -1;
        if (lastNameA > lastNameB) return 1;
        return 0; // Als beide gelijk zijn
    });
    console.log(invoices)

    // Clear existing rows
    invoiceTableBody.innerHTML = '';

    // Add new rows
    invoices.invoices.forEach(invoice => {
        const isPaid = invoice.invoice_paid === 'Betaald';

        const row = document.createElement('tr');
        row.innerHTML = `
            <td class="text-center"><a href="${invoice.invoice_pdf_url}">${invoice.invoice_number}</a></td>
            <td class="text-center">
                <div class="d-flex align-items-center">
                    <div class="avatar me-2">
                        <img src="${invoice.invoice_created_by_picture_url || '/static/assets/img/avatars/default.jpg'}" class="w-px-40 h-auto rounded-circle" />
                    </div>
                    <div>${invoice.invoice_created_by_name}<br><small>${invoice.invoice_created_by_company}</small></div>
                </div>
            </td>
            <td class="text-center">€ ${invoice.invoice_amount}</td>
            <td class="text-center">€ ${invoice.invoice_btw}</td>
            <td class="text-center">${invoice.invoice_date}</td>
            <td class="text-center">
                <span class="badge text-bg-${isPaid ? 'success' : 'warning'} toggle-status-factuur-apotheek" data-invoice-id="${invoice.id}">
                    ${isPaid ? 'Betaald' : 'Te Betalen'}
                </span>
            </td>
        `;
        invoiceTableBody.appendChild(row);
    });

    // Reattach event listeners for the badges
    const badges = document.querySelectorAll('.toggle-status-factuur-apotheek');
    console.log(badges)
    badges.forEach(badge => {
        badge.addEventListener('click', function() {
            const invoiceId = badge.dataset.invoiceId;

            fetch('/invoice/admin/toggle_invoice_status_factuur_apotheek/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken'),
                },
                body: JSON.stringify({ 'invoice_id': invoiceId }),
            })
            .then(response => response.json())
            .then(data => {
                if (data.status) {
                    badge.classList.remove('text-bg-warning');
                    badge.classList.add('text-bg-success');
                    badge.textContent = 'Betaald';
                } else {
                    badge.classList.remove('text-bg-success');
                    badge.classList.add('text-bg-warning');
                    badge.textContent = 'Te Betalen';
                }

                // Refresh the page if needed
                if (window.location.pathname.endsWith('/invoice/admin/overview_all_invoices_apotheken_admin/')) {
                    window.location.reload();
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Er is een fout opgetreden bij het bijwerken van de factuurstatus.');
            });
        });
    });
}

function parseDate(dateStr) {
    const [day, month, year] = dateStr.split('/').map(Number);
    return new Date(year, month - 1, day); // month is zero-based in JavaScript Date
}

function sortTable(columnIndex) {
   var table, rows, switching, i, x, y, shouldSwitch, direction, switchcount = 0;
   table = document.getElementById("invoiceTable");
   switching = true;
   direction = "asc"; // Begin met oplopende volgorde

   while (switching) {
      switching = false;
      rows = table.rows;

      // Loop over de rijen, behalve de eerste (de header)
      for (i = 1; i < (rows.length - 1); i++) {
         shouldSwitch = false;
         x = rows[i].getElementsByTagName("TD")[columnIndex];
         y = rows[i + 1].getElementsByTagName("TD")[columnIndex];

         // Afhankelijk van de kolomindex, behandel de waarden anders (getal, datum, tekst)
         if (columnIndex === 2 || columnIndex === 3) { // Voor kolommen 3 en 4 (getallen)
            var numX = parseFloat(x.innerHTML.replace('€', '').replace(',', '.'));
            var numY = parseFloat(y.innerHTML.replace('€', '').replace(',', '.'));
            if (direction == "asc") {
               if (numX > numY) {
                  shouldSwitch = true;
                  break;
               }
            } else if (direction == "desc") {
               if (numX < numY) {
                  shouldSwitch = true;
                  break;
               }
            }
         } else if (columnIndex === 4) { // Voor kolom 5 (datum)
            var dateX = new Date(x.innerHTML.split('/').reverse().join('-')); // Verander d/m/Y naar Y-m-d
            var dateY = new Date(y.innerHTML.split('/').reverse().join('-'));
            if (direction == "asc") {
               if (dateX > dateY) {
                  shouldSwitch = true;
                  break;
               }
            } else if (direction == "desc") {
               if (dateX < dateY) {
                  shouldSwitch = true;
                  break;
               }
            }
         } else { // Voor andere kolommen (tekst)
            if (direction == "asc") {
               if (x.innerHTML.toLowerCase() > y.innerHTML.toLowerCase()) {
                  shouldSwitch = true;
                  break;
               }
            } else if (direction == "desc") {
               if (x.innerHTML.toLowerCase() < y.innerHTML.toLowerCase()) {
                  shouldSwitch = true;
                  break;
               }
            }
         }
      }

      if (shouldSwitch) {
         rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
         switching = true;
         switchcount++;
      } else {
         // Als er geen switch heeft plaatsgevonden en de richting 'asc' was, wijzig naar 'desc'
         if (switchcount == 0 && direction == "asc") {
            direction = "desc";
            switching = true;
         }
      }
   }
}

