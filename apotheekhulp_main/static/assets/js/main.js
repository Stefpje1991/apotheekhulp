'use strict';

const labelMappings = {
    afstandinkilometers: "Afstand in Kilometers",
    uurtariefassistent: "Uurtarief van Assistent",
    uurtariefapotheek: "Uurtarief aan Apotheek"
    // Add more mappings as needed
};

let menu, animate;

(function () {
  // Initialize menu
  //-----------------

  let layoutMenuEl = document.querySelectorAll('#layout-menu');
  layoutMenuEl.forEach(function (element) {
    menu = new Menu(element, {
      orientation: 'vertical',
      closeChildren: false
    });
    // Change parameter to true if you want scroll animation
    window.Helpers.scrollToActive((animate = false));
    window.Helpers.mainMenu = menu;
  });

  // Initialize menu togglers and bind click on each
  let menuToggler = document.querySelectorAll('.layout-menu-toggle');
  menuToggler.forEach(item => {
    item.addEventListener('click', event => {
      event.preventDefault();
      window.Helpers.toggleCollapsed();
    });
  });

  // Display menu toggle (layout-menu-toggle) on hover with delay
  let delay = function (elem, callback) {
    let timeout = null;
    elem.onmouseenter = function () {
      if (!Helpers.isSmallScreen()) {
        timeout = setTimeout(callback, 300);
      } else {
        timeout = setTimeout(callback, 0);
      }
    };

    elem.onmouseleave = function () {
      const menuToggle = document.querySelector('.layout-menu-toggle');
      if (menuToggle) {
        menuToggle.classList.remove('d-block');
      }
      clearTimeout(timeout);
    };
  };

  const layoutMenu = document.getElementById('layout-menu');
  if (layoutMenu) {
    delay(layoutMenu, function () {
      if (!Helpers.isSmallScreen()) {
        const menuToggle = document.querySelector('.layout-menu-toggle');
        if (menuToggle) {
          menuToggle.classList.add('d-block');
        }
      }
    });
  }

  // Display in main menu when menu scrolls
  let menuInnerContainer = document.getElementsByClassName('menu-inner');
  let menuInnerShadow = document.getElementsByClassName('menu-inner-shadow')[0];
  if (menuInnerContainer.length > 0 && menuInnerShadow) {
    menuInnerContainer[0].addEventListener('ps-scroll-y', function () {
      if (this.querySelector('.ps__thumb-y').offsetTop) {
        menuInnerShadow.style.display = 'block';
      } else {
        menuInnerShadow.style.display = 'none';
      }
    });
  }

  // Init helpers & misc
  // --------------------

  // Init BS Tooltip
  const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
  tooltipTriggerList.forEach(function (tooltipTriggerEl) {
    return new bootstrap.Tooltip(tooltipTriggerEl);
  });

  // Accordion active class
  const accordionActiveFunction = function (e) {
    if (e.type === 'show.bs.collapse') {
      e.target.closest('.accordion-item').classList.add('active');
    } else if (e.type === 'hide.bs.collapse') {
      e.target.closest('.accordion-item').classList.remove('active');
    }
  };

  const accordionTriggerList = [].slice.call(document.querySelectorAll('.accordion'));
  accordionTriggerList.forEach(function (accordionTriggerEl) {
    accordionTriggerEl.addEventListener('show.bs.collapse', accordionActiveFunction);
    accordionTriggerEl.addEventListener('hide.bs.collapse', accordionActiveFunction);
  });

  // Auto update layout based on screen size
  window.Helpers.setAutoUpdate(true);

  // Toggle Password Visibility
  window.Helpers.initPasswordToggle();

  // Speech To Text
  window.Helpers.initSpeechToText();

  // Manage menu expanded/collapsed with templateCustomizer & local storage
  //------------------------------------------------------------------

  if (window.Helpers.isSmallScreen()) {
    return;
  }

  window.Helpers.setCollapsed(true, false);
})();

const roleField = document.getElementById('id_role');
const assistentForm = document.getElementById('assistent-form');
const apotheekForm = document.getElementById('apotheek-form');

if (roleField) {
  roleField.addEventListener('change', function() {
    const selectedRole = this.value;
    if (assistentForm && apotheekForm) {
      assistentForm.style.display = selectedRole === '1' ? 'block' : 'none';
      apotheekForm.style.display = selectedRole === '2' ? 'block' : 'none';
    }
  });
}

function deleteProfilePicture() {
  const deleteProfilePictureForm = document.getElementById('deleteProfilePictureForm');
  if (deleteProfilePictureForm) {
    deleteProfilePictureForm.submit();
  }
}

function previewImage(event) {
  const reader = new FileReader();
  reader.onload = function() {
    const output = document.getElementById('uploadedAvatar');
    if (output) {
      output.src = reader.result;
      alert("Profielfoto is geladen maar nog niet opgeslaan");
    }
  };
  if (event.target.files[0]) {
    reader.readAsDataURL(event.target.files[0]);
  }
}

document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll('.accept-btn').forEach(button => {
        button.addEventListener('click', function(event) {
            event.preventDefault(); // Prevent the default button behavior

            const eventId = this.getAttribute('data-event-id');
            updateStatus(eventId, 'Accepted');
        });
    });

    document.querySelectorAll('.decline-btn').forEach(button => {
        button.addEventListener('click', function(event) {
            event.preventDefault(); // Prevent the default button behavior

            const eventId = this.getAttribute('data-event-id');
            updateStatus(eventId, 'Declined');
        });
    });

    const tableRows = document.querySelectorAll("#tbl_assistenten tbody tr");

    tableRows.forEach(function (row) {
        row.addEventListener("click", function () {
            if (event.target.closest('.edit-btn')) {
                return;
            }
            // Fetch data from the clicked row
            const firstName = row.getAttribute("data-first-name");
            const lastName = row.getAttribute("data-last-name");
            const email = row.getAttribute("data-email");
            const phoneNumber = row.getAttribute("data-phone-number");
            const status = row.getAttribute("data-status");
            const btwNummer = row.getAttribute("data-btw-nummer");
            const btwPlichtig = row.getAttribute("data-btw-plichtig");
            const naamBedrijf = row.getAttribute("data-naam-bedrijf");
            const straatBedrijf = row.getAttribute("data-straat-bedrijf");
            const huisnummerBedrijf = row.getAttribute("data-huisnummer-bedrijf");
            const postcodeBedrijf = row.getAttribute("data-postcode-bedrijf");
            const stadBedrijf = row.getAttribute("data-stad-bedrijf");

            // Set the modal content with the fetched data
            document.getElementById("modalFirstName").textContent = firstName || "N/A";
            document.getElementById("modalLastName").textContent = lastName || "N/A";
            document.getElementById("modalEmail").textContent = email || "N/A";
            document.getElementById("modalPhoneNumber").textContent = phoneNumber || "N/A";
            document.getElementById("modalStatus").textContent = status || "N/A";
            document.getElementById("modalBtwNummer").textContent = btwNummer || "N/A";
            document.getElementById("modalBtwPlichtig").textContent = btwPlichtig || "N/A";
            document.getElementById("modalNaamBedrijf").textContent = naamBedrijf || "N/A";
            document.getElementById("modalStraatBedrijf").textContent = straatBedrijf || "N/A";
            document.getElementById("modalHuisnummerBedrijf").textContent = huisnummerBedrijf || "N/A";
            document.getElementById("modalPostcodeBedrijf").textContent = postcodeBedrijf || "N/A";
            document.getElementById("modalStadBedrijf").textContent = stadBedrijf || "N/A";

            // Show the modal
            var myModal = new bootstrap.Modal(document.getElementById('addLinkModal'));
            myModal.show();
        });
    });

        // Get the assistent and apotheek names from hidden inputs
    const assistentNameElement = document.getElementById("assistentName");
    const apotheekNameElement = document.getElementById("apotheekName");

    const assistentName = assistentNameElement ? assistentNameElement.value : null;
    const apotheekName = apotheekNameElement ? apotheekNameElement.value : null;


    var addLinkModal = document.getElementById('addLinkModal');
    if (addLinkModal) { // Ensure the modal exists on the page
        addLinkModal.addEventListener('show.bs.modal', function (event) {
            if (assistentName) {
                console.log("Assistent Name:", assistentName);
                const assistentDropdown = document.getElementById("id_assistent");
                for (let option of assistentDropdown.options) {
                    if (option.text.trim() === assistentName.trim()) {
                        option.selected = true;
                        break;
                    }
                }
            }

            if (apotheekName) {
                const apotheekDropdown = document.getElementById("id_apotheek");
                for (let option of apotheekDropdown.options) {
                    if (option.text.trim() === apotheekName.trim()) {
                        option.selected = true;
                        break;
                    }
                }
            }
        });
    }

    const table = document.getElementById("tbl_apotheken");
    const addLinkModalApotheek = document.getElementById('addLinkModalApotheek');


    if (table && addLinkModalApotheek) {
        table.addEventListener('click', function (event) {
            const target = event.target.closest('tr'); // Get the closest <tr> element
            if (target && target.hasAttribute('data-first-name')) {
                // Extract data attributes from the <tr>
                if (event.target.closest('.edit-btn')) {
                return;
                }
                const apotheekFirstName = target.getAttribute('data-first-name');
                const apotheekLastName = target.getAttribute('data-last-name');
                const apotheekEmail = target.getAttribute('data-email');
                const apotheekPhoneNumber = target.getAttribute('data-phone-number');
                const apotheekStatus = target.getAttribute('data-status');
                const apotheekBtwNummer = target.getAttribute('data-btw-nummer');
                const apotheekNaamBedrijf = target.getAttribute('data-naam-bedrijf');
                const apotheekStraatBedrijf = target.getAttribute('data-straat-bedrijf');
                const apotheekHuisnummerBedrijf = target.getAttribute('data-huisnummer-bedrijf');
                const apotheekPostcodeBedrijf = target.getAttribute('data-postcode-bedrijf');
                const apotheekStadBedrijf = target.getAttribute('data-stad-bedrijf');

                // Populate the modal with extracted data
                document.getElementById("modalFirstNameApotheek").textContent = apotheekFirstName;
                document.getElementById("modalLastNameApotheek").textContent = apotheekLastName;
                document.getElementById("modalEmailApotheek").textContent = apotheekEmail;
                document.getElementById("modalPhoneNumberApotheek").textContent = apotheekPhoneNumber;
                document.getElementById("modalStatusApotheek").textContent = apotheekStatus;
                document.getElementById("modalBtwNummerApotheek").textContent = apotheekBtwNummer;
                document.getElementById("modalNaamBedrijfApotheek").textContent = apotheekNaamBedrijf;
                document.getElementById("modalStraatBedrijfApotheek").textContent = apotheekStraatBedrijf;
                document.getElementById("modalHuisnummerBedrijfApotheek").textContent = apotheekHuisnummerBedrijf;
                document.getElementById("modalPostcodeBedrijfApotheek").textContent = apotheekPostcodeBedrijf;
                document.getElementById("modalStadBedrijfApotheek").textContent = apotheekStadBedrijf;

                // Show the modal
                var modal = new bootstrap.Modal(addLinkModalApotheek);
                modal.show();
            }
        });
    }
});

function closeModal() {
      // Reload the page to reset the form and hide the modal
      window.location.href = window.location.href.split('?')[0];
   }

function updateStatus(eventId, newStatus) {
    console.log('Updating event status...');
    console.log('Event ID:', eventId);
    console.log('New Status:', newStatus);

    fetch(`/invoice/update_event_status/${eventId}/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken') // Ensure the CSRF token is correct
        },
        body: JSON.stringify({ status_apotheek: newStatus })
    })
    .then(response => response.json())
    .then(data => {
        console.log('Response data:', data);
        if (data.success) {
            window.location.reload();
        } else {
            alert('Failed to update status: ' + (data.error || 'Unknown error'));
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred: ' + error.message);
    });
}


function updateStatusAssistent(eventId, newStatus) {
    console.log('Updating event status...');
    console.log('Event ID:', eventId);
    console.log('New Status:', newStatus);

    fetch(`/invoice/update_event_status_assistent/${eventId}/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken') // Ensure the CSRF token is correct
        },
        body: JSON.stringify({ status: newStatus })
    })
    .then(response => response.json())
    .then(data => {
        console.log('Response data:', data);
        if (data.success) {
            window.location.reload();
        } else {
            alert('Failed to update status: ' + (data.error || 'Unknown error'));
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred: ' + error.message);
    });
}

