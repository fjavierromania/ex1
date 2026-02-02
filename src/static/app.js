document.addEventListener("DOMContentLoaded", () => {
  const activitiesList = document.getElementById("activities-list");
  const activitySelect = document.getElementById("activity");
  const signupForm = document.getElementById("signup-form");
  const messageDiv = document.getElementById("message");
  
  let allActivities = {}; // Store all activities for filtering

  // Function to fetch activities from API
  async function fetchActivities() {
    try {
      const response = await fetch("/activities");
      const activities = await response.json();
      allActivities = activities;

      // Clear loading message
      activitiesList.innerHTML = "";

      // Populate activities list
      Object.entries(activities).forEach(([name, details]) => {
        const activityCard = document.createElement("div");
        activityCard.className = "activity-card";

        const spotsLeft = details.max_participants - details.participants.length;
        const isFull = spotsLeft === 0;
        const status = isFull ? "full" : "available";

        const participantsList = details.participants.length > 0
          ? `<ul>${details.participants.map(p => `<li>${p}</li>`).join('')}</ul>`
          : '<p><em>No participants yet</em></p>';

        const participantsId = `participants-${name.replace(/\s+/g, "-")}`;

        activityCard.innerHTML = `
          <h4>${name} <span class="status-badge ${status}">${status}</span></h4>
          <p>${details.description}</p>
          <p><strong>Schedule:</strong> ${details.schedule}</p>
          <p><strong>Availability:</strong> ${spotsLeft} spots left</p>
          <div class="participants-section">
            <button class="participants-toggle" data-target="${participantsId}">
              <strong>Participants (${details.participants.length}/${details.max_participants})</strong>
              <span class="toggle-icon">▼</span>
            </button>
            <div id="${participantsId}" class="participants-list">
              ${participantsList}
            </div>
          </div>
        `;

        activitiesList.appendChild(activityCard);

        // Add expand/collapse functionality
        const toggleBtn = activityCard.querySelector(".participants-toggle");
        const participantsList_el = activityCard.querySelector(`#${participantsId}`);
        
        toggleBtn.addEventListener("click", () => {
          participantsList_el.classList.toggle("collapsed");
          toggleBtn.classList.toggle("active");
        });

        // Add option to select dropdown
        const option = document.createElement("option");
        option.value = name;
        option.textContent = name;
        activitySelect.appendChild(option);
      });
    } catch (error) {
      activitiesList.innerHTML = "<p>Failed to load activities. Please try again later.</p>";
      console.error("Error fetching activities:", error);
    }
  }

  // Handle form submission
  signupForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const email = document.getElementById("email").value;
    const activity = document.getElementById("activity").value;

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activity)}/signup?email=${encodeURIComponent(email)}`,
        {
          method: "POST",
        }
      );

      const result = await response.json();

      if (response.ok) {
        messageDiv.textContent = result.message;
        messageDiv.className = "success";
        signupForm.reset();
        fetchActivities(); // Refresh activities after signup
      } else {
        messageDiv.textContent = result.detail || "An error occurred";
        messageDiv.className = "error";
      }

      messageDiv.classList.remove("hidden");

      // Hide message after 5 seconds
      setTimeout(() => {
        messageDiv.classList.add("hidden");
      }, 5000);
    } catch (error) {
      messageDiv.textContent = "Failed to sign up. Please try again.";
      messageDiv.className = "error";
      messageDiv.classList.remove("hidden");
      console.error("Error signing up:", error);
    }
  });

  // Initialize app
  fetchActivities();
});
