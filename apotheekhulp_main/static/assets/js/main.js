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

$(document).ready(function() {
  if ($('#calendar').length) { // Check if calendar element exists
    $('#calendar').fullCalendar({
      header: {
        left: 'prev,next today',
        center: 'title',
        right: 'month,agendaWeek,agendaDay'
      },
      defaultDate: '2024-08-01',
      editable: true,
    });
  }
});

document.addEventListener("DOMContentLoaded", function () {
    const tableRows = document.querySelectorAll("#tbl_assistenten tbody tr");

    const addLinkForm = document.getElementById('addLinkForm');
    const addLinkModal = new bootstrap.Modal(document.getElementById('addLinkModal'));
    var assistentId = document.getElementById('modalAssistentId').value;
    var apotheekId = document.getElementById('modalApotheekId').value;

    // Fetching data from data-* attributes
    const assistentName = document.getElementById('assistentData').dataset.assistentName;
    const apotheekName = document.getElementById('apotheekData').dataset.apotheekName;

    // Set Assistent data if available
    if (assistentName) {
        // Preselect the dropdown option by text content
        const assistentDropdown = document.querySelector('[name="assistent"]');
        for (let option of assistentDropdown.options) {
            if (option.textContent.trim() === assistentName.trim()) {
                option.selected = true;
                break;
            }
        }
    }
    // Set Apotheek data if available
    if (apotheekName) {
        // Preselect the dropdown option by text content
        const apotheekDropdown = document.querySelector('[name="apotheek"]');
        for (let option of apotheekDropdown.options) {
            if (option.textContent.trim() === apotheekName.trim()) {
                option.selected = true;
                break;
            }
        }
    }

    addLinkForm.addEventListener('submit', function (event) {
        event.preventDefault();

        const formData = new FormData(addLinkForm);

        fetch(addLinkForm.action, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                addLinkForm.reset();
                addLinkModal.hide();
                location.reload();
            } else {
                displayErrors(data.errors);
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
    });

    function displayErrors(errors) {
        const alertContainer = document.querySelector('#addLinkModal .alert');
        if (alertContainer) {
            alertContainer.innerHTML = '';
        }

        const alertDiv = document.createElement('div');
        alertDiv.className = 'alert alert-danger';
        for (const field in errors) {
            if (errors.hasOwnProperty(field)) {
                const errorMessages = errors[field];
                errorMessages.forEach(msg => {
                    const p = document.createElement('p');
                    p.textContent = `${msg}`;
                    alertDiv.appendChild(p);
                });
            }
        }
        const modalBody = document.querySelector('#addLinkModal .modal-body');
        modalBody.insertBefore(alertDiv, modalBody.firstChild);
    }

    tableRows.forEach(function (row) {
        row.addEventListener("click", function (event) {
            if (event.target.closest('.edit-btn')) {
                return;
            }

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

            document.getElementById("modalFirstName").textContent = firstName;
            document.getElementById("modalLastName").textContent = lastName;
            document.getElementById("modalEmail").textContent = email;
            document.getElementById("modalPhoneNumber").textContent = phoneNumber;
            document.getElementById("modalStatus").textContent = status;
            document.getElementById("modalBtwNummer").textContent = btwNummer || "N/A";
            document.getElementById("modalBtwPlichtig").textContent = btwPlichtig;
            document.getElementById("modalNaamBedrijf").textContent = naamBedrijf || "N/A";
            document.getElementById("modalStraatBedrijf").textContent = straatBedrijf || "N/A";
            document.getElementById("modalHuisnummerBedrijf").textContent = huisnummerBedrijf || "N/A";
            document.getElementById("modalPostcodeBedrijf").textContent = postcodeBedrijf || "N/A";
            document.getElementById("modalStadBedrijf").textContent = stadBedrijf || "N/A";

            var myModal = new bootstrap.Modal(document.getElementById('rowClickModal'));
            myModal.show();
        });
    });
});
