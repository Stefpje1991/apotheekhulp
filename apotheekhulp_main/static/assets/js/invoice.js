document.addEventListener('DOMContentLoaded', function () {
    // Function to fetch event data and populate the modal
    window.openEditModal = function (eventId) {
        const eventContainer = document.getElementById('row-id');
        if (eventContainer){
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
                    const modal = new bootstrap.Modal(modalElement);
                    console.log(modal)
                    modal.show();
                } else {
                    alert(`Error: ${data.error}`);
                }
            })
            .catch(error => {
                alert(`An error occurred: ${error.message}`);
            });
    };

    // Function to open and populate the detail modal on table row click
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

// Include SweetAlert2 library if not already included in your HTML
// <script src="https://cdn.jsdelivr.net/npm/sweetalert2@11"></script>

    const buttonCreateInvoiceApotheek = document.getElementById('createInvoiceButton_apotheek');
const saveInvoiceApotheekButton = document.getElementById('saveInvoiceApotheekButton');
const createInvoiceApotheekModalElement = document.getElementById('createInvoiceApotheekModal');

let createInvoiceApotheekModal;

if (createInvoiceApotheekModalElement) {
    createInvoiceApotheekModal = new bootstrap.Modal(createInvoiceApotheekModalElement);
}

if (buttonCreateInvoiceApotheek) {
    buttonCreateInvoiceApotheek.addEventListener('click', function () {
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
        saveInvoiceApotheekButton.addEventListener('click', function () {
            submitInvoiceApotheek();
        });
    }

    function submitInvoiceApotheek() {
        const form = document.getElementById('invoiceFormApotheek');
        const formData = new FormData(form);

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

    // Check sessionStorage for the flag and show the success alert if necessary
    const invoiceApotheekCreationStatus = sessionStorage.getItem('invoiceCreationStatus');
    const downloadUrlApotheek = sessionStorage.getItem('downloadUrlApotheek'); // Retrieve the download URL

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


    const buttonCreateInvoiceAssistent = document.getElementById('createInvoiceButton_assistent');
    const saveInvoiceButton = document.getElementById('saveInvoiceButton');
    const createInvoiceModalElement = document.getElementById('createInvoiceModal');
    if(createInvoiceModalElement){
        const createInvoiceModal = new bootstrap.Modal(createInvoiceModalElement);
    }


    if (buttonCreateInvoiceAssistent) {
        buttonCreateInvoiceAssistent.addEventListener('click', function () {
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
                createInvoiceModal.show();
            }
        });
    }

    if (saveInvoiceButton) {
        saveInvoiceButton.addEventListener('click', function () {
            submitInvoice();
        });
    }

    function submitInvoice() {
        const form = document.getElementById('invoiceForm');
        const formData = new FormData(form);

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
                    createInvoiceModal.hide();
                    // Store success flag and download URL
                    sessionStorage.setItem('invoiceCreationStatus', 'success');
                    sessionStorage.setItem('downloadUrl', data.download_url); // Ensure this URL is included in the response
                    window.location.reload(); // Reload the page to see the changes
                } else {
                    createInvoiceModal.hide(); // Hide the modal
                    Swal.fire({
                        icon: 'error',
                        title: 'Foutmelding',
                        text: data.message
                    });
                }
            })
            .catch(error => {
                createInvoiceModal.hide(); // Hide the modal
                console.error('Error:', error);
                Swal.fire({
                    icon: 'error',
                    title: 'Foutmelding',
                    text: 'Er is een fout opgetreden bij het verzenden van de aanvraag.'
                });
            });
        } else {
            createInvoiceModal.hide(); // Hide the modal
            Swal.fire({
                icon: 'warning',
                title: 'Ongeldige Invoer',
                text: 'Vul alstublieft alle velden in en selecteer minstens één event.'
            });
        }
    }

    // Check sessionStorage for the flag and show the success alert if necessary
    const invoiceCreationStatus = sessionStorage.getItem('invoiceCreationStatus');
    const downloadUrl = sessionStorage.getItem('downloadUrl'); // Retrieve the download URL

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



    // Handle click events for the table rows to show the detail modal
    const table = document.getElementById('tbl_nog_te_factureren_door_assistent_obj');
    if (table) {
        table.addEventListener('click', function (event) {
            const row = event.target.closest('tr');
            if (row && row.querySelector('td')) {
                openDetailModal(row);
            }
        });
    }

    // Existing code for handling "Bewerken" buttons and form submissions
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
    // Check if urlContainer exists before accessing its attributes
    const urlContainer = document.getElementById('urlContainer');
    if (urlContainer) {
        const baseEditLinkUrl = urlContainer.getAttribute('data-edit-link-url');

        // Check if baseEditLinkUrl exists
        if (baseEditLinkUrl) {
            const editButtons = document.querySelectorAll('.edit-link-assistent-apotheek-btn');
                // Access the URL pattern from the data attribute

            editButtons.forEach(button => {
                button.addEventListener('click', function () {
                    const row = this.closest('tr');
                    const linkId = row.getAttribute('data-link-id');
                    const assistentName = row.querySelector('td:nth-child(1)').textContent.trim();
                    const apotheekName = row.querySelector('td:nth-child(2)').textContent.trim();
                    const uurtariefAssistent = row.querySelector('td:nth-child(4)').textContent.trim().replace('€ ', '');
                    const uurtariefApotheek = row.querySelector('td:nth-child(5)').textContent.trim().replace('€ ', '');
                    const kilometervergoeding = row.querySelector('td:nth-child(6) i').classList.contains('fa-check');
                    const afstandInKilometers = row.querySelector('td:nth-child(7)').textContent.trim();

                    // Populate modal fields immediately
                    const modalLinkId = document.getElementById('editModalLinkId');
                    const modalAssistent = document.getElementById('id_assistent');
                    const modalApotheek = document.getElementById('id_apotheek');
                    const modalUurtariefAssistent = document.getElementById('id_uurtariefAssistent');
                    const modalUurtariefApotheek = document.getElementById('id_uurtariefApotheek');
                    const modalKilometervergoeding = document.getElementById('id_kilometervergoeding');
                    const modalAfstandInKilometers = document.getElementById('id_afstandInKilometers');

                    modalLinkId.value = linkId;
                    modalAssistent.value = assistentName;
                    modalApotheek.value = apotheekName;
                    modalUurtariefAssistent.value = uurtariefAssistent;
                    modalUurtariefApotheek.value = uurtariefApotheek;
                    modalKilometervergoeding.checked = kilometervergoeding;
                    modalAfstandInKilometers.value = afstandInKilometers;

                    // Update the form action URL
                    const formAction = baseEditLinkUrl.replace('/0/', `/${linkId}/`);
                    document.getElementById('editLinkForm').setAttribute('action', formAction);

                    // Show the modal
                    const editModal = new bootstrap.Modal(document.getElementById('editLinkModal'));
                    editModal.show();
                });
            });
        }
    }

    // Handle the form submission
    const editLinkForm = document.getElementById('editLinkForm');
    if(editLinkForm){

    editLinkForm.addEventListener('submit', function(event) {
        event.preventDefault(); // Prevent the default form submission

        const formData = {
            uurtariefAssistent: document.getElementById('id_uurtariefAssistent').value,
            uurtariefApotheek: document.getElementById('id_uurtariefApotheek').value,
            afstandInKilometers: document.getElementById('id_afstandInKilometers').value,
            kilometervergoeding: document.getElementById('id_kilometervergoeding').checked ? 'on' : 'off'
        };
        const formAction = editLinkForm.getAttribute('action');

        fetch(formAction, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value // Ensure CSRF token is included
            },
            body: JSON.stringify(formData)
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                // Optionally, refresh or update the page content
                location.reload(); // Refresh the page or update the content as needed
            } else {
                alert('Error updating link: ' + data.error);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred while updating the link');
        });
    });
    }

    const badges = document.querySelectorAll('.toggle-status-factuur-assistent');

    badges.forEach(function(badge) {
        console.log("BADGE")
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
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Er is een fout opgetreden bij het bijwerken van de factuurstatus.');
            });
        });
    });


});
