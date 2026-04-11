/**
 * Landing page — department and doctor modals (fetch from public API).
 */
function openDeptModal(deptId) {
  fetch("/api/department/" + deptId)
    .then(function (r) {
      return r.json();
    })
    .then(function (data) {
      document.getElementById("deptModalTitle").textContent = data.name;
      document.getElementById("deptModalDesc").textContent = data.description;
      var list = document.getElementById("deptDoctorList");
      list.innerHTML = "";
      if (!data.doctors || !data.doctors.length) {
        list.innerHTML =
          '<li class="list-group-item text-muted">No doctors listed yet.</li>';
      } else {
        data.doctors.forEach(function (d) {
          var li = document.createElement("li");
          li.className = "list-row";
          li.innerHTML =
            "<div><strong>" +
            d.name +
            "</strong><br><small class='muted'>" +
            d.experience_years +
            "+ yrs</small></div>" +
            '<button type="button" class="btn btn-secondary btn-sm doctor-mini" data-id="' +
            d.id +
            '">Profile</button>';
          list.appendChild(li);
        });
      }
      window.HMSModal.open("deptModal");
      list.querySelectorAll(".doctor-mini").forEach(function (btn) {
        btn.addEventListener("click", function () {
          openDoctorModal(parseInt(btn.getAttribute("data-id"), 10));
        });
      });
    })
    .catch(function () {
      alert("Could not load department details.");
    });
}

function openDoctorModal(doctorId) {
  fetch("/api/doctor/" + doctorId)
    .then(function (r) {
      return r.json();
    })
    .then(function (data) {
      document.getElementById("doctorModalTitle").textContent = data.name;
      document.getElementById("doctorModalDept").textContent = data.department;
      document.getElementById("doctorModalBio").textContent = data.bio || "—";
      document.getElementById("doctorModalExp").textContent = data.experience_years;
      window.HMSModal.open("doctorModal");
    })
    .catch(function () {
      alert("Could not load doctor profile.");
    });
}

document.addEventListener("DOMContentLoaded", function () {
  document.querySelectorAll(".dept-card").forEach(function (btn) {
    btn.addEventListener("click", function () {
      openDeptModal(parseInt(btn.getAttribute("data-dept-id"), 10));
    });
  });
  document.querySelectorAll(".profile-btn").forEach(function (btn) {
    btn.addEventListener("click", function () {
      openDoctorModal(parseInt(btn.getAttribute("data-doctor-id"), 10));
    });
  });
  if (window.HMS_PRESELECT_DEPT) {
    openDeptModal(window.HMS_PRESELECT_DEPT);
  }
});
