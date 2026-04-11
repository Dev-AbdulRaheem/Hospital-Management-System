/**
 * Patient booking — load available slots via /patient/api/available-slots
 */
document.addEventListener("DOMContentLoaded", function () {
  var doctor = document.getElementById("doctor_id");
  var dateEl = document.getElementById("appointment_date");
  var slotSel = document.getElementById("time_slot");
  var help = document.getElementById("slotHelp");
  var submitBtn = document.getElementById("submitBtn");

  if (!doctor || !dateEl || !slotSel) return;

  var today = new Date();
  var todayISO = today.toISOString().split("T")[0];
  dateEl.min = todayISO;

  function loadSlots() {
    var did = doctor.value;
    var d = dateEl.value;
    slotSel.innerHTML = '<option value="">Loading…</option>';
    slotSel.disabled = true;
    submitBtn.disabled = true;
    help.textContent = "Slots update when you pick a doctor and a future date.";

    if (!did || !d) {
      slotSel.innerHTML = '<option value="">Select doctor and date first</option>';
      return;
    }

    var selectedDoctorOption = doctor.options[doctor.selectedIndex];
    var unavailStart = selectedDoctorOption.dataset.unavailStart;
    var unavailEnd = selectedDoctorOption.dataset.unavailEnd;

    if (unavailStart && unavailEnd) {
      var selectedDate = new Date(d);
      var unavailabilityStartDate = new Date(unavailStart);
      var unavailabilityEndDate = new Date(unavailEnd);

      if (selectedDate >= unavailabilityStartDate && selectedDate <= unavailabilityEndDate) {
        slotSel.innerHTML = '<option value="">Doctor unavailable</option>';
        help.textContent = "Doctor is unavailable on this date.";
        return;
      }
    }

    fetch(
      "/patient/api/available-slots?doctor_id=" +
        encodeURIComponent(did) +
        "&date=" +
        encodeURIComponent(d)
    )
      .then(function (r) {
        return r.json();
      })
      .then(function (data) {
        slotSel.innerHTML = "";
        if (data.message === "past_date") {
          help.textContent = "Choose today or a future date.";
          slotSel.innerHTML = '<option value="">—</option>';
          return;
        }
        var slots = data.slots || [];
        if (!slots.length) {
          slotSel.innerHTML = '<option value="">No slots left this day</option>';
          help.textContent = "Try another date or doctor.";
          return;
        }
        
        var currentHour = today.getHours();
        var currentMinute = today.getMinutes();

        slots.forEach(function (s) {
          var slotHour = parseInt(s.value.split(":")[0]);
          var slotMinute = parseInt(s.value.split(":")[1]);
          
          var opt = document.createElement("option");
          opt.value = s.value;
          opt.textContent = s.label;

          // Disable past time slots for the current date
          if (d === todayISO && (slotHour < currentHour || (slotHour === currentHour && slotMinute <= currentMinute))) {
            opt.disabled = true;
            opt.textContent += " (Past)";
          }
          slotSel.appendChild(opt);
        });
        slotSel.disabled = false;
        submitBtn.disabled = false;
        help.textContent = "Select a time and confirm.";
      })
      .catch(function () {
        slotSel.innerHTML = '<option value="">Error loading slots</option>';
        help.textContent = "Try again.";
      });
  }

  doctor.addEventListener("change", loadSlots);
  dateEl.addEventListener("change", loadSlots);
  loadSlots(); // Initial load
});
