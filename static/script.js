
// Debug helper function
function debugLog(message, data = null, level = 'info') {
  const timestamp = new Date().toISOString();
  const logMessage = `[${timestamp}] [${level.toUpperCase()}] ${message}`;
  
  switch(level) {
    case 'error':
      console.error(logMessage, data || '');
      break;
    case 'warn':
      console.warn(logMessage, data || '');
      break;
    default:
      console.log(logMessage, data || '');
  }
  
  // Also display critical errors in UI
  if (level === 'error') {
    displayError(message, data);
  }
}

// Display error in UI
function displayError(message, details) {
  const errorContent = document.getElementById('debug-content');
  const errorPanel = document.getElementById('debug-panel');
  if (errorContent && errorPanel) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'debug-error';
    errorDiv.innerHTML = `
      <strong>Error:</strong> ${message}
      ${details ? `<br><small>${JSON.stringify(details)}</small>` : ''}
      <span class="debug-time">${new Date().toLocaleTimeString()}</span>
    `;
    errorContent.appendChild(errorDiv);
    errorPanel.style.display = 'block';
    
    // Auto-hide after 10 seconds
    setTimeout(() => {
      errorDiv.style.opacity = '0';
      setTimeout(() => errorDiv.remove(), 500);
    }, 10000);
  } else {
    console.error('Debug panel not found:', message, details);
  }
}

// Display debug info in UI
function displayDebug(message, level = 'info') {
  const debugContent = document.getElementById('debug-content');
  const debugPanel = document.getElementById('debug-panel');
  if (debugContent && debugPanel) {
    const debugDiv = document.createElement('div');
    debugDiv.style.color = level === 'error' ? '#ff6666' : '#0f0';
    debugDiv.innerHTML = `
      [${level.toUpperCase()}] ${message}
      <span class="debug-time">${new Date().toLocaleTimeString()}</span>
    `;
    debugContent.appendChild(debugDiv);
    debugPanel.style.display = 'block';
    
    // Auto-hide after 5 seconds for non-errors
    if (level !== 'error') {
      setTimeout(() => {
        debugDiv.style.opacity = '0';
        setTimeout(() => debugDiv.remove(), 500);
      }, 5000);
    }
  }
}

document.addEventListener("DOMContentLoaded", () => {
// Auto-redirect from 0.0.0.0 to localhost for microphone access
if (window.location.hostname === '0.0.0.0') {
  const newURL = window.location.href.replace('0.0.0.0', 'localhost');
  window.location.replace(newURL);
  return;
}

debugLog('Application initialized');

// --- Theme Switcher Logic ---
const themeToggleButton = document.getElementById('theme-toggle-button');
const body = document.body;

// Function to apply the saved theme
const applyTheme = () => {
  const savedTheme = localStorage.getItem('chirp-theme');
  if (savedTheme === 'dark') {
    body.classList.add('dark-mode');
  } else {
    body.classList.remove('dark-mode');
  }
};

// Function to toggle the theme
const toggleTheme = () => {
  body.classList.toggle('dark-mode');
  // Save the new theme preference
  if (body.classList.contains('dark-mode')) {
    localStorage.setItem('chirp-theme', 'dark');
  } else {
    localStorage.setItem('chirp-theme', 'light');
  }
};

// Add event listener to the button
if (themeToggleButton) {
  themeToggleButton.addEventListener('click', toggleTheme);
}

// Apply the theme on initial load
applyTheme();

// Test API connection on load
  fetch('/api/status')
    .then(response => response.json())
    .then(data => {
      debugLog('API Status Check:', data);
      displayDebug(`API Status: ${data.status}, TTS: ${data.tts_client}, Speech: ${data.speech_client}`);
      if (!data.tts_client || !data.speech_client) {
        displayError('Google Cloud clients not initialized', data);
      }
    })
    .catch(err => {
      debugLog('Failed to check API status', err, 'error');
      displayError('Cannot connect to API - is the server running?', err);
    });
  
  // --- High Score Logic ---
  const HIGH_SCORES_KEY = "chirp-high-scores-v2";
  const MAX_HIGH_SCORES = 5;

  const HIGH_SCORES_KEY_LEARNING = "chirp-high-scores-learning";

  function getHighScores() {
    try {
      const scoresJSON = localStorage.getItem(HIGH_SCORES_KEY);
      if (scoresJSON) {
        return JSON.parse(scoresJSON);
      }
    } catch (e) {
      debugLog("Could not parse high scores from localStorage", e, 'error');
      return getDefaultHighScores(); // Fallback
    }
    return getDefaultHighScores();
  }

  function saveHighScores(scores) {
    try {
      localStorage.setItem(HIGH_SCORES_KEY, JSON.stringify(scores));
    } catch (e) {
      debugLog("Could not save high scores to localStorage", e, 'error');
    }
  }

  function saveHighScoresLearning(scores) {
    try {
      localStorage.setItem(HIGH_SCORES_KEY_LEARNING, JSON.stringify(scores));
    } catch (e) {
      debugLog("Could not save high scores to localStorage", e, 'error');
    }
  }

  function getHighScoresLearning() {
    try {
      const scoresJSON = localStorage.getItem(HIGH_SCORES_KEY_LEARNING);
      if (scoresJSON) {
        return JSON.parse(scoresJSON);
      }
    } catch (error) {
      debugLog("Could not parse learning high scores from localStorage", error, 'error');
      return getDefaultHighScores(); // Fallback
    }
    return getDefaultHighScores();
  }

  function getDefaultHighScores() {
    // Return an empty array when no scores are in localStorage
    return [];
  }

  function displayHighScores() {
    const highScores = getHighScores();
    const tableBody = document.getElementById("high-scores-body");
    if (!tableBody) return; // Exit if table isn't on the page

    tableBody.innerHTML = ""; // Clear existing scores

    if (highScores.length === 0) {
      const row = document.createElement("tr");
      // Use colspan="3" to span all columns (Rank, Name, Score)
      row.innerHTML = `<td colspan="3" class="placeholder">No stars identified yet.</td>`;
      tableBody.appendChild(row);
    } else {
      highScores.forEach((entry, index) => {
        const row = document.createElement("tr");
        row.innerHTML = `
        <td>${index + 1}</td>
        <td>${entry.name}</td>
        <td>${entry.score}</td>
      `;
        tableBody.appendChild(row);
      });
    }
  }

  function displayHighScoresLearning() {
    const highScores = getHighScoresLearning();
    const tableBody = document.getElementById("high-scores-body-learning");

    if (!tableBody) return; // Exit if table isn't on the page

    tableBody.innerHTML = ""; // Clear existing scores

    if (highScores.length === 0) {
      const row = document.createElement("tr");
      row.innerHTML = `<td colspan="3" class="placeholder">No players identified yet.</td>`;
      tableBody.appendChild(row);
    } else {
      highScores.forEach((entry, index) => {
        const row = document.createElement("tr");
        row.innerHTML = `
        <td>${index + 1}</td>
        <td>${entry.name}</td>
        <td>${entry.score}</td>
      `;
        tableBody.appendChild(row);
      });
    } 
  }

  // Display scores on initial load
  displayHighScores();
  displayHighScoresLearning();

  // Reset button for Singing Contest scores
  const resetSingingScoresBtn = document.getElementById('reset-singing-scores');
  if (resetSingingScoresBtn) {
    resetSingingScoresBtn.addEventListener('click', () => {
      if (confirm('Are you sure you want to reset all singing contest scores? This cannot be undone.')) {
        localStorage.removeItem(HIGH_SCORES_KEY);
        displayHighScores();
        debugLog('Singing contest scores reset', null, 'info');
      }
    });
  }

  // Reset button for Language Learning scores
  const resetLearningScoresBtn = document.getElementById('reset-learning-scores');
  if (resetLearningScoresBtn) {
    resetLearningScoresBtn.addEventListener('click', () => {
      if (confirm('Are you sure you want to reset all language learning scores? This cannot be undone.')) {
        localStorage.removeItem(HIGH_SCORES_KEY_LEARNING);
        displayHighScoresLearning();
        debugLog('Language learning scores reset', null, 'info');
      }
    });
  }

  // --- Modal Logic ---
  const modal = document.getElementById("highscore-modal");
  const modalScoreText = document.getElementById("modal-score-text");
  const playerNameInput = document.getElementById("player-name-input");
  const saveButton = document.getElementById("modal-save-button");
  const cancelButton = document.getElementById("modal-cancel-button");

  const modalLearning = document.getElementById("highscore-modal-learning");
  const modalScoreTextLearning = document.getElementById("modal-score-text-learning");
  const playerNameInputLearning = document.getElementById("player-name-input-learning");
  const saveButtonLearning = document.getElementById("modal-save-button-learning");
  const cancelButtonLearning = document.getElementById("modal-cancel-button-learning");
  const scoreLearningInput = document.getElementById("score-learning");


  let resolvePromise = null;

  function showModal(score) {
    modalScoreText.textContent = `You scored ${score} points! Enter your name to save your score.`;
    playerNameInput.value = "";
    modal.style.display = "flex";
    playerNameInput.focus();
    return new Promise((resolve) => {
      resolvePromise = resolve;
    });
  }

  function hideModal() {
    modal.style.display = "none";
  }

  function handleSave() {
    const name = playerNameInput.value.trim();
    if (name && resolvePromise) {
      resolvePromise(name);
    } else if (resolvePromise) {
      resolvePromise(null); // Resolve with null if name is empty
    }
    hideModal();
    resolvePromise = null; // Reset promise resolver
  }

  function handleSavelearning() {
    const name = playerNameInputLearning.value.trim();
    const score = scoreLearningInput.value.trim();
    checkAndSaveHighScoreLearning(score, name)
    modalLearning.style.display = "none";
    resolvePromise = null;
  }

  function handleCancel() {
    if (resolvePromise) {
      resolvePromise(null); // Resolve with null if cancelled
    }
    hideModal();
    resolvePromise = null;
  }

  function handleCancelLearning() {
    if (resolvePromise) {
      resolvePromise(null); // Resolve with null if cancelled
    }
    modalLearning.style.display = "none";
    resolvePromise = null;
  }

  saveButton.addEventListener("click", handleSave);
  cancelButton.addEventListener("click", handleCancel);

  saveButtonLearning.addEventListener("click", handleSavelearning);
  cancelButtonLearning.addEventListener("click", handleCancelLearning)

  // Also allow submitting with Enter key
  playerNameInput.addEventListener("keyup", (event) => {
    if (event.key === "Enter") {
      handleSave();
    }
  });

  async function checkAndSaveHighScore(newScore) {
    const highScores = getHighScores();
    const lowestScore =
      highScores.length < MAX_HIGH_SCORES ? 0 : highScores[highScores.length - 1].score;

    if (newScore > lowestScore) {
      const name = await showModal(newScore); // Replaces prompt
      if (name) {
        const newEntry = { name: name, score: newScore };
        highScores.push(newEntry);
        highScores.sort((a, b) => b.score - a.score); // Sort descending
        const updatedHighScores = highScores.slice(0, MAX_HIGH_SCORES);
        saveHighScores(updatedHighScores);
        displayHighScores(); // Update the table
      }
    }
  }

  function checkAndSaveHighScoreLearning(newScore, name) {
    const highScores = getHighScoresLearning();
    const lowestScore =
      highScores.length < MAX_HIGH_SCORES ? 0 : highScores[highScores.length - 1].score;
  
    if (newScore > lowestScore) {
        const newEntry = { name: name, score: newScore };
        highScores.push(newEntry);
        highScores.sort((a, b) => b.score - a.score); // Sort descending
        const updatedHighScores = highScores.slice(0, MAX_HIGH_SCORES);
        saveHighScoresLearning(updatedHighScores);
        displayHighScoresLearning(); // Update the table
    }
  }

  // --- Tab Switching Logic ---
  const tabLinks = document.querySelectorAll(".tab-link");
  const tabPanes = document.querySelectorAll(".tab-pane");

  tabLinks.forEach((link) => {
    link.addEventListener("click", () => {
      const tabId = link.dataset.tab;

      // Deactivate all tabs
      tabLinks.forEach((l) => l.classList.remove("active"));
      tabPanes.forEach((p) => p.classList.remove("active"));

      // Activate the clicked tab
      link.classList.add("active");
      document.getElementById(tabId).classList.add("active");
    });
  });

  function normalizeText(text) {
    if (typeof text !== 'string') {
      return '';
    }
    return text
      .toLowerCase()
      .replace(/[^\w\s]/g, "")
      .trim();
  }

  function processWords(words) {
    return words.map((w) => ({
      ...w,
      word: normalizeText(w.word),
      startTime: parseFloat(w.startOffset || "0s"),
      endTime: parseFloat(w.endOffset || "0s"),
    }));
  }

  const songRefrains = {
    aranha: {
      time: 18,
      language: "en-US",
      text: `The lady spider climbed up the wall\nAlong came the rain and knocked her down\nThe rain has stopped and the sun is rising\nAnd the lady spider continues to climb`,
    },
    atirei: {
      time: 20,
      language: "en-US",
      text: `I threw a stick at the cat-cat\nBut the cat-cat didn't die-die-die\nMrs. Chica-ca was amazed-mazed by the meow\nThe meow that the cat gave - meow!`,
      words: processWords([
        {
          startOffset: "1.240s",
          endOffset: "2.520s",
          word: "Atirei",
        },
        {
          startOffset: "2.520s",
          endOffset: "2.600s",
          word: "o",
        },
        {
          startOffset: "2.600s",
          endOffset: "3s",
          word: "pau",
        },
        {
          startOffset: "3s",
          endOffset: "3.160s",
          word: "no",
        },
        {
          startOffset: "3.160s",
          endOffset: "4.200s",
          word: "gato,",
        },
        {
          startOffset: "4.240s",
          endOffset: "4.640s",
          word: "to,",
        },
        {
          startOffset: "4.640s",
          endOffset: "5.160s",
          word: "mas",
        },
        {
          startOffset: "5.160s",
          endOffset: "5.280s",
          word: "o",
        },
        {
          startOffset: "5.280s",
          endOffset: "6.320s",
          word: "gato",
        },
        {
          startOffset: "6.360s",
          endOffset: "6.680s",
          word: "to",
        },
        {
          startOffset: "6.680s",
          endOffset: "7.160s",
          word: "não",
        },
        {
          startOffset: "7.160s",
          endOffset: "7.880s",
          word: "morreu.",
        },
        {
          startOffset: "7.960s",
          endOffset: "8.400s",
          word: "reu,",
        },
        {
          startOffset: "8.440s",
          endOffset: "8.960s",
          word: "reu",
        },
        {
          startOffset: "9s",
          endOffset: "9.440s",
          word: "Dona",
        },
        {
          startOffset: "9.920s",
          endOffset: "10.220s",
          word: "Chica",
        },
        {
          startOffset: "10.220s",
          endOffset: "10.320s",
          word: "ca",
        },
        {
          startOffset: "10.920s",
          endOffset: "11.920s",
          word: "admirou",
        },
        {
          startOffset: "12.200s",
          endOffset: "12.320s",
          word: "se",
        },
        {
          startOffset: "12.320s",
          endOffset: "12.400s",
          word: "se",
        },
        {
          startOffset: "13.160s",
          endOffset: "13.480s",
          word: "Do",
        },
        {
          startOffset: "13.480s",
          endOffset: "14.200s",
          word: "miau,",
        },
        {
          startOffset: "14.240s",
          endOffset: "14.560s",
          word: "do",
        },
        {
          startOffset: "14.560s",
          endOffset: "15s",
          word: "miau",
        },
        {
          startOffset: "15s",
          endOffset: "15.200s",
          word: "que",
        },
        {
          startOffset: "15.200s",
          endOffset: "15.280s",
          word: "o",
        },
        {
          startOffset: "15.280s",
          endOffset: "15.760s",
          word: "gato",
        },
        {
          startOffset: "15.760s",
          endOffset: "16.200s",
          word: "deu.",
        },
        {
          startOffset: "16.280s",
          endOffset: "17.880s",
          word: "Miau.",
        },
      ]),
    },
    cravo: {
      time: 21,
      language: "en-US",
      text: `The carnation fought with the rose\nUnderneath a balcony\nThe carnation was wounded\nAnd the rose was shattered`,
      words: processWords([
        {
          startOffset: "1.240s",
          endOffset: "1.680s",
          word: "O",
        },
        {
          startOffset: "1.680s",
          endOffset: "2.800s",
          word: "cravo",
        },
        {
          startOffset: "2.800s",
          endOffset: "3.560s",
          word: "brigou",
        },
        {
          startOffset: "3.560s",
          endOffset: "3.760s",
          word: "com",
        },
        {
          startOffset: "3.760s",
          endOffset: "3.920s",
          word: "a",
        },
        {
          startOffset: "3.920s",
          endOffset: "5.080s",
          word: "rosa,",
        },
        {
          startOffset: "5.520s",
          endOffset: "7.240s",
          word: "debaixo",
        },
        {
          startOffset: "7.240s",
          endOffset: "7.400s",
          word: "de",
        },
        {
          startOffset: "7.400s",
          endOffset: "7.920s",
          word: "uma",
        },
        {
          startOffset: "7.920s",
          endOffset: "9.880s",
          word: "sacada,",
        },
        {
          startOffset: "10.040s",
          endOffset: "10.560s",
          word: "o",
        },
        {
          startOffset: "10.560s",
          endOffset: "11.680s",
          word: "cravo",
        },
        {
          startOffset: "11.680s",
          endOffset: "12.440s",
          word: "saiu",
        },
        {
          startOffset: "12.440s",
          endOffset: "14.400s",
          word: "ferido",
        },
        {
          startOffset: "14.440s",
          endOffset: "14.640s",
          word: "e",
        },
        {
          startOffset: "14.640s",
          endOffset: "15.120s",
          word: "a",
        },
        {
          startOffset: "15.120s",
          endOffset: "16.240s",
          word: "rosa",
        },
        {
          startOffset: "16.240s",
          endOffset: "18.960s",
          word: "despedaçada.",
        },
      ]),
    },
    jingle: {
      time: 7,
      language: "en-US",
      text: `Jingle bells, jingle bells\nJingle all the way\nOh what fun it is to ride\nIn a one horse open sleigh - hey!`,
      words: processWords([
        {
          startOffset: "0s",
          endOffset: "0.600s",
          word: "Jingle",
        },
        {
          startOffset: "0.600s",
          endOffset: "1.200s",
          word: "bells,",
        },
        {
          startOffset: "1.200s",
          endOffset: "1.720s",
          word: "jingle",
        },
        {
          startOffset: "1.720s",
          endOffset: "2.320s",
          word: "bells,",
        },
        {
          startOffset: "2.320s",
          endOffset: "3s",
          word: "jingle",
        },
        {
          startOffset: "3s",
          endOffset: "3.320s",
          word: "all",
        },
        {
          startOffset: "3.320s",
          endOffset: "3.520s",
          word: "the",
        },
        {
          startOffset: "3.520s",
          endOffset: "3.720s",
          word: "way.",
        },
        {
          startOffset: "4.720s",
          endOffset: "4.760s",
          word: "Oh,",
        },
        {
          startOffset: "4.760s",
          endOffset: "4.840s",
          word: "what",
        },
        {
          startOffset: "4.840s",
          endOffset: "4.920s",
          word: "fun",
        },
        {
          startOffset: "4.920s",
          endOffset: "4.960s",
          word: "it",
        },
        {
          startOffset: "4.960s",
          endOffset: "5.040s",
          word: "is",
        },
        {
          startOffset: "5.040s",
          endOffset: "5.080s",
          word: "to",
        },
        {
          startOffset: "5.080s",
          endOffset: "5.200s",
          word: "ride",
        },
        {
          startOffset: "5.200s",
          endOffset: "5.230s",
          word: "in",
        },
        {
          startOffset: "5.230s",
          endOffset: "5.280s",
          word: "a",
        },
        {
          startOffset: "5.280s",
          endOffset: "5.400s",
          word: "one",
        },
        {
          startOffset: "5.400s",
          endOffset: "5.520s",
          word: "horse",
        },
        {
          startOffset: "5.520s",
          endOffset: "5.680s",
          word: "open",
        },
        {
          startOffset: "5.680s",
          endOffset: "5.760s",
          word: "sleigh.",
        },
        {
          startOffset: "5.760s",
          endOffset: "5.800s",
          word: "Hey",
        },
      ]),
    },
    old: {
      time: 17,
      language: "en-US",
      text: `Old MacDonald had a farm\nE I E I O\nAnd on that farm he had a pig\nE I E I O\nWith an oink oink here\nAnd an oink oink there\nHere an oink there an oink\nEverywhere an oink oink`,
      words: processWords([
        {
          startOffset: "0s",
          endOffset: "0.360s",
          word: "Old",
        },
        {
          startOffset: "0.360s",
          endOffset: "1.280s",
          word: "MacDonald",
        },
        {
          startOffset: "1.280s",
          endOffset: "1.680s",
          word: "had",
        },
        {
          startOffset: "1.680s",
          endOffset: "1.840s",
          word: "a",
        },
        {
          startOffset: "1.840s",
          endOffset: "2.440s",
          word: "farm.",
        },
        {
          startOffset: "2.560s",
          endOffset: "2.960s",
          word: "E",
        },
        {
          startOffset: "2.960s",
          endOffset: "3.160s",
          word: "i",
        },
        {
          startOffset: "3.160s",
          endOffset: "3.480s",
          word: "e",
        },
        {
          startOffset: "3.480s",
          endOffset: "3.800s",
          word: "i",
        },
        {
          startOffset: "3.800s",
          endOffset: "4.280s",
          word: "o.",
        },
        {
          startOffset: "4.720s",
          endOffset: "5.080s",
          word: "And",
        },
        {
          startOffset: "5.080s",
          endOffset: "5.320s",
          word: "on",
        },
        {
          startOffset: "5.320s",
          endOffset: "5.640s",
          word: "that",
        },
        {
          startOffset: "5.640s",
          endOffset: "6s",
          word: "farm",
        },
        {
          startOffset: "6s",
          endOffset: "6.240s",
          word: "he",
        },
        {
          startOffset: "6.240s",
          endOffset: "6.640s",
          word: "had",
        },
        {
          startOffset: "6.640s",
          endOffset: "6.760s",
          word: "a",
        },
        {
          startOffset: "6.760s",
          endOffset: "7.400s",
          word: "pig.",
        },
        {
          startOffset: "7.560s",
          endOffset: "7.960s",
          word: "E",
        },
        {
          startOffset: "7.960s",
          endOffset: "8.240s",
          word: "i",
        },
        {
          startOffset: "8.240s",
          endOffset: "8.560s",
          word: "e",
        },
        {
          startOffset: "8.560s",
          endOffset: "8.880s",
          word: "i",
        },
        {
          startOffset: "8.880s",
          endOffset: "9.360s",
          word: "o.",
        },
        {
          startOffset: "9.880s",
          endOffset: "10.040s",
          word: "an",
        },
        {
          startOffset: "10.040s",
          endOffset: "10.360s",
          word: "oink",
        },
        {
          startOffset: "10.360s",
          endOffset: "10.640s",
          word: "oink",
        },
        {
          startOffset: "10.640s",
          endOffset: "10.960s",
          word: "here",
        },
        {
          startOffset: "10.960s",
          endOffset: "11.120s",
          word: "and",
        },
        {
          startOffset: "11.120s",
          endOffset: "11.280s",
          word: "an",
        },
        {
          startOffset: "11.280s",
          endOffset: "11.600s",
          word: "oink",
        },
        {
          startOffset: "11.600s",
          endOffset: "11.880s",
          word: "oink",
        },
        {
          startOffset: "11.880s",
          endOffset: "12.320s",
          word: "there.",
        },
        {
          startOffset: "12.480s",
          endOffset: "12.680s",
          word: "Here",
        },
        {
          startOffset: "12.680s",
          endOffset: "12.840s",
          word: "an",
        },
        {
          startOffset: "12.840s",
          endOffset: "13.120s",
          word: "oink",
        },
        {
          startOffset: "13.120s",
          endOffset: "13.360s",
          word: "there",
        },
        {
          startOffset: "13.360s",
          endOffset: "13.480s",
          word: "an",
        },
        {
          startOffset: "13.480s",
          endOffset: "13.800s",
          word: "oink",
        },
        {
          startOffset: "13.800s",
          endOffset: "14.280s",
          word: "everywhere",
        },
        {
          startOffset: "14.280s",
          endOffset: "14.400s",
          word: "an",
        },
        {
          startOffset: "14.400s",
          endOffset: "14.720s",
          word: "oink",
        },
        {
          startOffset: "14.720s",
          endOffset: "15s",
          word: "oink",
        },
      ]),
    },
    peixe: {
      time: 20,
      language: "en-US",
      text: `How can a living fish\nLive outside of cold water\nHow can a living fish\nLive outside of cold water\nHow can I live\nHow can I live\nWithout your, without your\nWithout your company`,
      words: processWords([
        { endOffset: "1.040s", word: "Como", confidence: 0.48399335 },
        {
          startOffset: "1.040s",
          endOffset: "1.520s",
          word: "pode",
        },
        {
          startOffset: "1.520s",
          endOffset: "1.600s",
          word: "um",
        },
        {
          startOffset: "1.600s",
          endOffset: "2.120s",
          word: "peixe",
        },
        {
          startOffset: "2.120s",
          endOffset: "2.680s",
          word: "vivo",
        },
        {
          startOffset: "2.680s",
          endOffset: "3.160s",
          word: "viver",
        },
        {
          startOffset: "3.160s",
          endOffset: "3.720s",
          word: "fora",
        },
        {
          startOffset: "3.720s",
          endOffset: "3.880s",
          word: "da",
        },
        {
          startOffset: "3.880s",
          endOffset: "4.240s",
          word: "água",
        },
        {
          startOffset: "4.240s",
          endOffset: "4.760s",
          word: "fria?",
        },
        {
          startOffset: "4.760s",
          endOffset: "5.320s",
          word: "Como",
        },
        {
          startOffset: "5.320s",
          endOffset: "5.760s",
          word: "pode",
        },
        {
          startOffset: "5.760s",
          endOffset: "5.800s",
          word: "um",
        },
        {
          startOffset: "5.800s",
          endOffset: "6.400s",
          word: "peixe",
        },
        {
          startOffset: "6.400s",
          endOffset: "6.960s",
          word: "vivo",
        },
        {
          startOffset: "6.960s",
          endOffset: "7.440s",
          word: "viver",
        },
        {
          startOffset: "7.440s",
          endOffset: "8s",
          word: "fora",
        },
        {
          startOffset: "8s",
          endOffset: "8.160s",
          word: "da",
        },
        {
          startOffset: "8.160s",
          endOffset: "8.560s",
          word: "água",
        },
        {
          startOffset: "8.560s",
          endOffset: "8.960s",
          word: "fria?",
        },
        {
          startOffset: "9.440s",
          endOffset: "9.560s",
          word: "Como",
        },
        {
          startOffset: "10.080s",
          endOffset: "10.560s",
          word: "poderei",
        },
        {
          startOffset: "10.560s",
          endOffset: "11.360s",
          word: "viver?",
        },
        {
          startOffset: "11.560s",
          endOffset: "11.800s",
          word: "Como",
        },
        {
          startOffset: "11.800s",
          endOffset: "12.720s",
          word: "poderei",
        },
        {
          startOffset: "12.720s",
          endOffset: "13.400s",
          word: "viver?",
        },
        {
          startOffset: "13.400s",
          endOffset: "13.760s",
          word: "Sem",
        },
        {
          startOffset: "13.760s",
          endOffset: "13.920s",
          word: "a",
        },
        {
          startOffset: "13.920s",
          endOffset: "14.440s",
          word: "tua,",
        },
        {
          startOffset: "14.440s",
          endOffset: "14.840s",
          word: "sem",
        },
        {
          startOffset: "14.840s",
          endOffset: "14.960s",
          word: "a",
        },
        {
          startOffset: "14.960s",
          endOffset: "15.520s",
          word: "tua,",
        },
        {
          startOffset: "15.520s",
          endOffset: "15.880s",
          word: "sem",
        },
        {
          startOffset: "15.880s",
          endOffset: "16.040s",
          word: "a",
        },
        {
          startOffset: "16.040s",
          endOffset: "16.600s",
          word: "tua",
        },
        {
          startOffset: "16.600s",
          endOffset: "17.560s",
          word: "companhia.",
        },
      ]),
    },
    sapo: {
      time: 10,
      language: "en-US",
      text: `Cururu frog, by the riverside\nWhen the frog sings, little sister\nIt's because he's cold`,
      words: processWords([
        {
          startOffset: "0.320s",
          endOffset: "0.840s",
          word: "Sapo",
        },
        {
          startOffset: "0.840s",
          endOffset: "1.840s",
          word: "cururu,",
        },
        {
          startOffset: "2.600s",
          endOffset: "3s",
          word: "na",
        },
        {
          startOffset: "3s",
          endOffset: "3.440s",
          word: "beira",
        },
        {
          startOffset: "3.440s",
          endOffset: "3.720s",
          word: "do",
        },
        {
          startOffset: "3.720s",
          endOffset: "4.160s",
          word: "rio,",
        },
        {
          startOffset: "4.840s",
          endOffset: "5.280s",
          word: "quando",
        },
        {
          startOffset: "5.280s",
          endOffset: "5.320s",
          word: "o",
        },
        {
          startOffset: "5.480s",
          endOffset: "6s",
          word: "sapo",
        },
        {
          startOffset: "6s",
          endOffset: "6.440s",
          word: "canta",
        },
        {
          startOffset: "6.440s",
          endOffset: "7.280s",
          word: "maninha,",
        },
        {
          startOffset: "7.280s",
          endOffset: "7.400s",
          word: "é",
        },
        {
          startOffset: "7.400s",
          endOffset: "8s",
          word: "porque",
        },
        {
          startOffset: "8s",
          endOffset: "8.280s",
          word: "tem",
        },
        {
          startOffset: "8.280s",
          endOffset: "8.800s",
          word: "frio.",
        },
      ]),
    },
    spider: {
      time: 17,
      language: "en-US",
      text: `Itsy-bitsy spider, went up the water spout\nDown came the rain and washed the spider out\nOut came the sunshine and dried up all the rain`,
      words: processWords([
        {
          startOffset: "0.280s",
          endOffset: "1.400s",
          word: "Itsy-bitsy",
        },
        {
          startOffset: "1.400s",
          endOffset: "2.520s",
          word: "spider",
        },
        {
          startOffset: "2.520s",
          endOffset: "2.840s",
          word: "went",
        },
        {
          startOffset: "2.840s",
          endOffset: "3.160s",
          word: "up",
        },
        {
          startOffset: "3.160s",
          endOffset: "3.400s",
          word: "the",
        },
        {
          startOffset: "3.400s",
          endOffset: "3.960s",
          word: "water",
        },
        {
          startOffset: "3.960s",
          endOffset: "4.680s",
          word: "spout.",
        },
        {
          startOffset: "5.320s",
          endOffset: "5.960s",
          word: "Down",
        },
        {
          startOffset: "5.960s",
          endOffset: "6.400s",
          word: "came",
        },
        {
          startOffset: "6.400s",
          endOffset: "6.600s",
          word: "the",
        },
        {
          startOffset: "6.600s",
          endOffset: "7.240s",
          word: "rain",
        },
        {
          startOffset: "7.680s",
          endOffset: "7.960s",
          word: "and",
        },
        {
          startOffset: "7.960s",
          endOffset: "8.360s",
          word: "washed",
        },
        {
          startOffset: "8.360s",
          endOffset: "8.480s",
          word: "the",
        },
        {
          startOffset: "8.480s",
          endOffset: "9.320s",
          word: "spider",
        },
        {
          startOffset: "9.320s",
          endOffset: "9.920s",
          word: "out.",
        },
        {
          startOffset: "10.640s",
          endOffset: "11.120s",
          word: "Out",
        },
        {
          startOffset: "11.120s",
          endOffset: "11.560s",
          word: "came",
        },
        {
          startOffset: "11.560s",
          endOffset: "11.720s",
          word: "the",
        },
        {
          startOffset: "11.720s",
          endOffset: "12.880s",
          word: "sunshine",
        },
        {
          startOffset: "12.880s",
          endOffset: "13.040s",
          word: "and",
        },
        {
          startOffset: "13.040s",
          endOffset: "13.520s",
          word: "dried",
        },
        {
          startOffset: "13.520s",
          endOffset: "13.760s",
          word: "up",
        },
        {
          startOffset: "13.760s",
          endOffset: "14.080s",
          word: "all",
        },
        {
          startOffset: "14.080s",
          endOffset: "14.320s",
          word: "the",
        },
        {
          startOffset: "14.320s",
          endOffset: "15.200s",
          word: "rain.",
        },
      ]),
    },
    thunderstruck: {
      time: 15,
      language: "en-US",
      text: `Thunder! Thunder! Thunder!\nThunderstruck!\nYeah yeah yeah\nThunderstruck!`,
    },
    sweet_child: {
      time: 15,
      language: "en-US",
      text: `Sweet child o' mine\nSweet love of mine\nWhere do we go now\nWhere do we go`,
    },
    livin_on_a_prayer: {
      time: 15,
      language: "en-US",
      text: `Whoa we're halfway there\nWhoa livin' on a prayer\nTake my hand we'll make it I swear\nWhoa livin' on a prayer`,
    },
    bohemian_rhapsody: {
      time: 15,
      language: "en-US",
      text: `Is this the real life\nIs this just fantasy\nCaught in a landslide\nNo escape from reality`,
    },
    dont_stop_believin: {
      time: 15,
      language: "en-US",
      text: `Don't stop believin'\nHold on to that feelin'\nStreetlight people\nDon't stop believin'`,
    },
    shape_of_you: {
      time: 15,
      language: "en-US",
      text: `I'm in love with the shape of you\nWe push and pull like a magnet do\nAlthough my heart is falling too\nI'm in love with your body`,
    },
    in_the_end: {
      time: 15,
      language: "en-US",
      text: `I tried so hard and got so far\nBut in the end it doesn't even matter\nI had to fall to lose it all\nBut in the end it doesn't even matter`,
    },
    like_a_prayer: {
      time: 15,
      language: "en-US",
      text: `Like a prayer you know I'll take you there\nIt's like a dream to me\nWhen you call my name it's like a little prayer\nI'm down on my knees I wanna take you there`,
    },
    shake_it_off: {
      time: 15,
      language: "en-US",
      text: `Cause the players gonna play play play play play\nAnd the haters gonna hate hate hate hate hate\nBaby I'm just gonna shake shake shake shake shake\nShake it off shake it off`,
    },
    wish: {
      time: 13,
      language: "en-US",
      text: `We wish you a Merry Christmas\nWe wish you a Merry Christmas\nWe wish you a Merry Christmas\nAnd a happy new year`,
      words: processWords([
        {
          startOffset: "0.640s",
          endOffset: "1.080s",
          word: "We",
        },
        {
          startOffset: "1.080s",
          endOffset: "1.560s",
          word: "wish",
        },
        {
          startOffset: "1.560s",
          endOffset: "1.800s",
          word: "you",
        },
        {
          startOffset: "1.800s",
          endOffset: "1.920s",
          word: "a",
        },
        {
          startOffset: "1.920s",
          endOffset: "2.360s",
          word: "Merry",
        },
        {
          startOffset: "2.360s",
          endOffset: "3.280s",
          word: "Christmas.",
        },
        {
          startOffset: "3.280s",
          endOffset: "3.680s",
          word: "We",
        },
        {
          startOffset: "3.680s",
          endOffset: "4.160s",
          word: "wish",
        },
        {
          startOffset: "4.160s",
          endOffset: "4.360s",
          word: "you",
        },
        {
          startOffset: "4.360s",
          endOffset: "4.520s",
          word: "a",
        },
        {
          startOffset: "4.520s",
          endOffset: "4.960s",
          word: "Merry",
        },
        {
          startOffset: "4.960s",
          endOffset: "5.840s",
          word: "Christmas.",
        },
        {
          startOffset: "5.880s",
          endOffset: "6.280s",
          word: "We",
        },
        {
          startOffset: "6.280s",
          endOffset: "6.760s",
          word: "wish",
        },
        {
          startOffset: "6.760s",
          endOffset: "7s",
          word: "you",
        },
        {
          startOffset: "7s",
          endOffset: "7.120s",
          word: "a",
        },
        {
          startOffset: "7.120s",
          endOffset: "7.520s",
          word: "Merry",
        },
        {
          startOffset: "7.520s",
          endOffset: "8.440s",
          word: "Christmas",
        },
        {
          startOffset: "8.480s",
          endOffset: "8.760s",
          word: "and",
        },
        {
          startOffset: "8.760s",
          endOffset: "8.880s",
          word: "a",
        },
        {
          startOffset: "8.880s",
          endOffset: "9.680s",
          word: "happy",
        },
        {
          startOffset: "9.680s",
          endOffset: "10.120s",
          word: "new",
        },
        {
          startOffset: "10.120s",
          endOffset: "11s",
          word: "year.",
        },
      ]),
    },
  };

  const captionButton = document.getElementById("caption-button");
  const captionOutput = document.getElementById("caption-output");
  const finalScoreOutput = document.getElementById("final-score-output");
  const refrainOutput = document.getElementById("refrain-output");
  const countdownOverlay = document.getElementById("countdown-overlay");
  const countdownOverlayText = document.getElementById("countdown-overlay-text");
  
  // Wait a bit for tabs to render, then find elements
  const initializeSongSelect = () => {
    const songSelect = document.querySelector("#song-select");
    
    if (!songSelect) {
      console.error('Song select dropdown not found!');
      debugLog('Song select dropdown not found! Retrying in 500ms...', null, 'warn');
      setTimeout(initializeSongSelect, 500);
      return;
    }
    
    const songSelectTrigger = songSelect.querySelector(".select-trigger");
    const songOptions = songSelect.querySelectorAll(".option");
    const selectedText = songSelectTrigger ? songSelectTrigger.querySelector("span") : null;
    
    console.log('✅ Song selection elements found:', {
      select: !!songSelect,
      trigger: !!songSelectTrigger,
      options: songOptions.length,
      selectedText: !!selectedText
    });
    debugLog(`Song selection elements loaded: Select=${!!songSelect}, Trigger=${!!songSelectTrigger}, Options=${songOptions.length}`, null, 'info');
    
    // Setup song selection dropdown
    setupSongSelection(songSelect, songSelectTrigger, songOptions, selectedText);
  };
  
  // Initialize after a short delay to ensure DOM is ready
  setTimeout(initializeSongSelect, 100);

  // Timer and Progress Bar elements
  const countdownText = document.getElementById("countdown-text");
  const progressBar = document.getElementById("progress-bar");

  // Timer variables
  let countdownInterval;
  let preRecordingCountdownInterval;
  let recordingDuration = 15; // Default duration
  let currentSongKey = null; // To hold the currently selected song key
  let timingGuideEnabled = true; // Default to enabled
  let timingGuideInterval = null;
  let recordingStartTime = null;

  // By default, the button is disabled.
  if (captionButton) {
    captionButton.disabled = true;
  }

  // Load timing guide preference from localStorage
  const timingGuideToggle = document.getElementById('timing-guide-toggle');
  if (timingGuideToggle) {
    const savedPreference = localStorage.getItem('chirp-timing-guide');
    if (savedPreference !== null) {
      timingGuideEnabled = savedPreference === 'true';
      timingGuideToggle.checked = timingGuideEnabled;
    }
    
    timingGuideToggle.addEventListener('change', (e) => {
      timingGuideEnabled = e.target.checked;
      localStorage.setItem('chirp-timing-guide', timingGuideEnabled);
      debugLog(`Timing guide ${timingGuideEnabled ? 'enabled' : 'disabled'}`);
      
      // Refresh the refrain display if a song is selected
      if (currentSongKey) {
        updateRefrainDisplay();
      }
    });
  }

  // Function to update refrain display with or without highlighting
  function updateRefrainDisplay() {
    if (!currentSongKey || !refrainOutput) return;
    
    const songData = songRefrains[currentSongKey];
    if (!songData || !songData.text) {
      refrainOutput.classList.remove('visible');
      return;
    }

    const lines = songData.text.split('\n');
    
    if (timingGuideEnabled && songData.time) {
      // Show with highlighting capability
      refrainOutput.innerHTML = '';
      refrainOutput.classList.add('with-highlighting');
      
      const duration = songData.time;
      const timePerLine = duration / lines.length;
      
      lines.forEach((line, index) => {
        const lineSpan = document.createElement('div');
        lineSpan.className = 'lyric-line';
        lineSpan.dataset.index = index;
        lineSpan.dataset.startTime = (index * timePerLine).toFixed(1);
        lineSpan.dataset.endTime = ((index + 1) * timePerLine).toFixed(1);
        lineSpan.textContent = line;
        
        refrainOutput.appendChild(lineSpan);
      });
    } else {
      // Show plain text
      refrainOutput.textContent = songData.text;
      refrainOutput.classList.remove('with-highlighting');
    }
    
    refrainOutput.classList.add('visible');
  }

  // Function to highlight the current line being sung (karaoke style)
  function highlightCurrentLine(elapsedSeconds) {
    if (!timingGuideEnabled || !currentSongKey) {
      debugLog(`Highlighting skipped: enabled=${timingGuideEnabled}, song=${currentSongKey}`, null, 'warn');
      return;
    }
    
    const lyricLines = refrainOutput.querySelectorAll('.lyric-line');
    if (lyricLines.length === 0) {
      debugLog('No lyric lines found for highlighting', null, 'warn');
      return;
    }
    
    // Only log every second to avoid spam
    if (Math.floor(elapsedSeconds * 10) % 10 === 0) {
      debugLog(`Highlighting at ${elapsedSeconds.toFixed(1)}s with ${lyricLines.length} lines`);
    }
    
    lyricLines.forEach((line, index) => {
      const startTime = parseFloat(line.dataset.startTime);
      const endTime = parseFloat(line.dataset.endTime);
      
      line.classList.remove('current', 'sung');
      
      if (elapsedSeconds >= startTime && elapsedSeconds < endTime) {
        line.classList.add('current');
        debugLog(`Line ${index} CURRENT (${startTime}s-${endTime}s) at ${elapsedSeconds.toFixed(1)}s`);
      } else if (elapsedSeconds >= endTime) {
        line.classList.add('sung');
      }
    });
  }

  // Function to setup song selection (called after elements are found)
  function setupSongSelection(songSelect, songSelectTrigger, songOptions, selectedText) {
    console.log('🎵 Setting up song selection event listeners...');
    
    if (songSelectTrigger) {
      songSelectTrigger.addEventListener("click", function(e) {
        e.preventDefault();
        e.stopPropagation();
        console.log('🎵 Song dropdown trigger clicked!');
        debugLog('Song dropdown clicked', null, 'info');
        displayDebug('Dropdown clicked');
        songSelect.classList.toggle("open");
        console.log('Dropdown open state:', songSelect.classList.contains('open'));
      }, true); // Use capture phase
      console.log('✅ Click listener added to song select trigger');
    } else {
      console.error('❌ Song select trigger not found - cannot add click handler');
    }

    if (songOptions && songOptions.length > 0) {
      songOptions.forEach((option, index) => {
        option.addEventListener("click", function(e) {
          e.preventDefault();
          e.stopPropagation();
          console.log(`🎵 Song option clicked: ${option.dataset.value}`);
          debugLog(`Song selected: ${option.dataset.value}`, null, 'info');
          displayDebug(`Selected: ${option.textContent.trim()}`);

          // --- AGGRESSIVE CLEANUP ---
          // Force stop any previous recording state before starting a new one.
          stopRecordingTimer();
          if (preRecordingCountdownInterval) {
            clearInterval(preRecordingCountdownInterval);
            preRecordingCountdownInterval = null;
          }
          if (socket && socket.readyState !== WebSocket.CLOSED) {
            socket.close();
          }
          if (captionButton) {
            captionButton.textContent = start_singing;
            captionButton.disabled = true; // Will be re-enabled shortly
          }
          // --- END CLEANUP ---
          
          // Remove selected class from any previously selected option
          songOptions.forEach((opt) => opt.classList.remove("selected"));

          // Add selected class to the clicked option
          option.classList.add("selected");

          // Update the trigger text and stored value
          if (selectedText) {
            selectedText.textContent = option.textContent.trim();
          }
          if (songSelect) {
            songSelect.dataset.value = option.dataset.value;
          }
          currentSongKey = option.dataset.value; // Update the current song key

          const songData = songRefrains[currentSongKey];

          // Set the recording duration and update UI
          recordingDuration = songData.time || 15;
          if (countdownText) {
            countdownText.textContent = recordingDuration;
          }

          // Update the refrain text display with timing guide if enabled
          updateRefrainDisplay();

          // Enable the button
          if (captionButton) {
            captionButton.disabled = false;
          }

          // Close the dropdown
          songSelect.classList.remove("open");
        }, true); // Use capture phase
      });
      console.log(`✅ Click listeners added to ${songOptions.length} song options`);
    } else {
      console.error('❌ No song options found!');
    }

    // Close the dropdown if clicking outside of it
    document.addEventListener("click", function(e) {
      if (songSelect && !songSelect.contains(e.target)) {
        songSelect.classList.remove("open");
      }
    });
    
    console.log('✅ Song selection setup complete!');
  }

  let socket;
  let audioContext;
  let input;
  let globalStream;

  const start_singing = "Start Singing";
  const stop_singing = "Stop Singing";

  // This will accumulate the final transcript and word details
  let finalTranscript = "";
  let finalWords = [];

  function calculateScore(userWords, originalRefrainData) {
    // If we have the detailed timing data for the original song, use the new method
    if (typeof originalRefrainData === "object" && originalRefrainData.words) {
      return calculateDetailedScore(userWords, originalRefrainData.words);
    } else {
      // Fallback to the old rhythm-based scoring for other songs
      return calculateRhythmScore(userWords, originalRefrainData);
    }
  }

  function calculateDetailedScore(userWords, originalWords) {
    if (userWords.length === 0 || originalWords.length === 0) {
      return {
        overallScore: 0,
        confidenceScore: 0,
        accuracyScore: 0,
        timingScore: 0,
      };
    }

    // 1. Normalize start times for both sequences
    const userStartTime = userWords[0].startTime;
    const originalStartTime = originalWords[0].startTime;

    const normalizedUserWords = userWords.map((w) => ({
      ...w,
      word: normalizeText(w.word),
      relativeStart: w.startTime - userStartTime,
    }));

    const normalizedOriginalWords = originalWords.map((w) => ({
      ...w,
      // word is already pre-normalized in the data structure
      relativeStart: w.startTime - originalStartTime,
    }));

    // 2. Align words and calculate metrics
    let matches = 0;
    let totalConfidence = 0;
    let totalTimingError = 0;
    const maxTimingError = 1.0; // Max timing error in seconds for a word to get a timing score of 0

    let originalIndex = 0;
    for (const userWord of normalizedUserWords) {
      // Find the user's word in the remaining original words
      for (let j = originalIndex; j < normalizedOriginalWords.length; j++) {
        if (userWord.word === normalizedOriginalWords[j].word) {
          const originalWord = normalizedOriginalWords[j];
          matches++;
          totalConfidence += userWord.confidence;

          const timingError = Math.abs(
            userWord.relativeStart - originalWord.relativeStart,
          );
          totalTimingError += timingError;

          originalIndex = j + 1; // Move to the next word to enforce order
          break; // Found match, move to the next user word
        }
      }
    }

    // --- 3. Calculate final scores (0-100) ---

    // Accuracy: More forgiving calculation based on matches vs. total words
    const accuracyScore = (matches / Math.max(userWords.length, originalWords.length)) * 100;

    // Confidence: Average confidence of the words that were matched
    const avgConfidence = matches > 0 ? totalConfidence / matches : 0;
    const confidenceScore = avgConfidence * 100;

    // Timing: Lower average error is better.
    let timingScore = 0;
    if (matches > 0) {
      const avgTimingError = totalTimingError / matches;
      // Scale the score. If avg error is 0, score is 100. If avg error is >= maxTimingError, score is 0.
      timingScore = Math.max(0, (1 - avgTimingError / maxTimingError) * 100);
    }

    // 4. Overall Score (weighted average)
    const overallScore = Math.min(
      100,
      accuracyScore * 0.5 + // 50%
        confidenceScore * 0.3 + // 30%
        timingScore * 0.2, // 20%
    );

    return {
      overallScore: Math.round(overallScore),
      confidenceScore: Math.round(confidenceScore),
      accuracyScore: Math.round(accuracyScore),
      timingScore: Math.round(timingScore), // The new score component
    };
  }

  // Renamed original function to be used as a fallback
  function calculateRhythmScore(userWords, originalRefrain) {
    if (userWords.length === 0) {
      return {
        overallScore: 0,
        confidenceScore: 0,
        accuracyScore: 0,
        rhythmScore: 0,
      };
    }

    const originalWords = normalizeText(originalRefrain).split(/\s+/);
    const sungWords = userWords.map((w) => normalizeText(w.word));

    // Simple alignment and scoring
    let matches = 0;
    let totalConfidence = 0;
    const pauseDurations = [];

    let originalIndex = 0;
    for (let i = 0; i < userWords.length; i++) {
      // Find the best match in the original text
      let found = false;
      for (let j = originalIndex; j < originalWords.length; j++) {
        if (sungWords[i] === originalWords[j]) {
          matches++;
          totalConfidence += userWords[i].confidence;
          originalIndex = j + 1;
          found = true;
          break;
        }
      }
      // Calculate pauses between consecutive words
      if (i > 0) {
        const pause = userWords[i].startTime - userWords[i - 1].endTime;
        if (pause > 0) {
          // Only consider positive pauses
          pauseDurations.push(pause);
        }
      }
    }

    // --- Score Calculation ---

    // 1. Accuracy Score (0-100)
    const accuracyScore = (matches / originalWords.length) * 100;

    // 2. Confidence Score (0-100)
    const avgConfidence = matches > 0 ? totalConfidence / matches : 0;
    const confidenceScore = avgConfidence * 100;

    // 3. Rhythm Score (0-100)
    let rhythmScore = 0;
    if (pauseDurations.length > 1) {
      const meanPause =
        pauseDurations.reduce((a, b) => a + b, 0) / pauseDurations.length;
      const variance =
        pauseDurations
          .map((p) => Math.pow(p - meanPause, 2))
          .reduce((a, b) => a + b, 0) / pauseDurations.length;
      const stdDev = Math.sqrt(variance);
      // Inverse of standard deviation, scaled to 0-100. A lower std dev (more consistent rhythm) is better.
      // The scaling factor (e.g., 0.5) is arbitrary and can be tuned.
      rhythmScore = Math.max(0, 100 - (stdDev / 0.5) * 100);
    } else if (pauseDurations.length > 0) {
      rhythmScore = 80; // High score for a single, consistent pause
    }

    // 4. Overall Score (weighted average)
    const overallScore = Math.min(
      100,
      accuracyScore * 0.5 + // 50% weight
        confidenceScore * 0.3 + // 30% weight
        rhythmScore * 0.2, // 20% weight
    );

    return {
      overallScore: Math.round(overallScore),
      confidenceScore: Math.round(confidenceScore),
      accuracyScore: Math.round(accuracyScore),
      rhythmScore: Math.round(rhythmScore),
    };
  }

  function startRecordingTimer() {
    let remainingTime = recordingDuration;
    recordingStartTime = Date.now();

    const updateTimer = () => {
      countdownText.textContent = remainingTime;
      const progressPercentage = (remainingTime / recordingDuration) * 100;
      progressBar.style.width = `${progressPercentage}%`;
    };

    updateTimer(); // Initial display

    countdownInterval = setInterval(() => {
      remainingTime--;
      updateTimer();

      if (remainingTime < 0) {
        clearInterval(countdownInterval);
        // Automatically trigger the stop action
        if (captionButton.textContent === stop_singing) {
          captionButton.click();
        }
      }
    }, 1000);
    
    // Update lyric highlighting every 50ms (faster, more responsive) if timing guide is enabled
    debugLog(`Checking highlighting conditions: enabled=${timingGuideEnabled}, song=${currentSongKey}`);
    if (timingGuideEnabled && currentSongKey) {
      debugLog('Starting lyric highlighting timer');
      timingGuideInterval = setInterval(() => {
        const elapsedSeconds = (Date.now() - recordingStartTime) / 1000;
        highlightCurrentLine(elapsedSeconds);
      }, 50); // Changed from 100ms to 50ms for more responsive highlighting
    } else {
      debugLog(`Lyric highlighting NOT started: enabled=${timingGuideEnabled}, song=${currentSongKey}`, null, 'warn');
    }
  }

  function stopRecordingTimer() {
    if (countdownInterval) {
      clearInterval(countdownInterval);
      countdownInterval = null;
      debugLog('Recording timer cleared.', null, 'warn');
    }
    if (timingGuideInterval) {
      clearInterval(timingGuideInterval);
      timingGuideInterval = null;
    }
    
    // Reset all lyric highlighting
    if (refrainOutput) {
      const lyricLines = refrainOutput.querySelectorAll('.lyric-line');
      lyricLines.forEach(line => {
        line.classList.remove('current', 'sung');
      });
    }
    
    if(progressBar) progressBar.style.width = "100%"; // Reset for next time
    if(countdownText) countdownText.textContent = recordingDuration;
    recordingStartTime = null;
  }

  captionButton.addEventListener("click", async () => {
    if (captionButton.textContent === start_singing) {
      try {
        // Hide score from previous rounds
        finalScoreOutput.style.display = "none";
        captionButton.disabled = true; // Disable button during countdown
        
        // Show overlay
        countdownOverlay.classList.remove('hidden');
        countdownOverlayText.textContent = "Get ready...";

        let countdown = 3;

        // This timeout creates a small delay so "Get ready..." is visible for a moment.
        setTimeout(() => {
            preRecordingCountdownInterval = setInterval(() => {
                if (countdown > 0) {
                    countdownOverlayText.textContent = countdown;
                    countdown--;
                } else {
                    clearInterval(preRecordingCountdownInterval);
                    preRecordingCountdownInterval = null;
                    
                    // Hide overlay and start
                    countdownOverlay.classList.add('hidden');
                    captionOutput.textContent = "Sing now!";
                    captionButton.textContent = stop_singing;
                    captionButton.disabled = false; // Re-enable button

                    // Start the recording timer
                    startRecordingTimer();

                    // Actually start recording
                    startRecording();
                }
            }, 1000);
        }, 1000); // 1 second delay for "Get ready..."

      } catch (err) {
        debugLog('Failed to start recording', err, 'error');
        displayError('Failed to start recording', err);
        if (preRecordingCountdownInterval) {
            clearInterval(preRecordingCountdownInterval);
            preRecordingCountdownInterval = null;
        }
        captionButton.textContent = start_singing;
        captionButton.disabled = false;
        stopRecordingTimer();
        countdownOverlay.classList.add('hidden'); // Hide on error
      }
    } else {
      stopRecording();
    }
  });
  
  function startRecording() {
    debugLog('Starting recording...');
    displayDebug('Starting recording...');
    
    // --- Original logic starts here ---
    finalTranscript = ""; // Reset transcript
    finalWords = []; // Reset words
    
    // Show caption output immediately
    captionOutput.textContent = "";
    captionOutput.classList.add('visible');
    
    const language = songRefrains[currentSongKey]?.language || "en-US"; // Default to en-US
    const wsProtocol = window.location.protocol === "https:" ? "wss://" : "ws://";
    const wsUrl = `${wsProtocol}${window.location.host}/listen?language_code=${language}`;
    socket = new WebSocket(wsUrl);

    socket.onopen = () => {
      captionOutput.textContent = "🎤 Listening...";
      
      // Check if getUserMedia is supported
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        const currentURL = window.location.href;
        const isLocalhost = window.location.hostname === 'localhost' ||
                           window.location.hostname === '127.0.0.1' ||
                           window.location.hostname === '[::1]';
        const isHTTPS = window.location.protocol === 'https:';
        
        let errorMsg = "⚠️ Microphone access requires a secure connection!\n\n";
        
        if (!isLocalhost && !isHTTPS) {
          errorMsg += "Current URL: " + currentURL + "\n\n";
          errorMsg += "Please access this app via:\n";
          errorMsg += "• http://localhost:8080 (recommended)\n";
          errorMsg += "• http://127.0.0.1:8080\n";
          errorMsg += "• Or set up HTTPS";
        } else {
          errorMsg += "Your browser doesn't support audio recording.\n";
          errorMsg += "Please use Chrome, Firefox, or Edge.";
        }
        
        captionOutput.textContent = errorMsg;
        debugLog(errorMsg, null, 'error');
        displayError('Microphone Access Blocked', errorMsg);
        captionButton.textContent = start_singing;
        captionButton.disabled = false;
        return;
      }
      
      navigator.mediaDevices
        .getUserMedia({ audio: true, video: false })
        .then(async (stream) => {
          globalStream = stream;
          audioContext = new (window.AudioContext ||
            window
.webkitAudioContext)();

          // Load the audio processor worklet
          await audioContext.audioWorklet.addModule(
            "/static/audio-processor.js",
          );
          const workletNode = new AudioWorkletNode(
            audioContext,
            "audio-processor",
          );

          // The worklet will post messages with the processed audio buffer
          workletNode.port.onmessage = (event) => {
            if (socket.readyState === WebSocket.OPEN) {
              // Send the Int16Array buffer from the worklet
              socket.send(event.data);
            }
          };

          input = audioContext.createMediaStreamSource(globalStream);
          input.connect(workletNode);
          workletNode.connect(audioContext.destination);
        })
        .catch((err) => {
          console.error("Error getting audio stream:", err);
          captionOutput.textContent =
            "Error: Could not access microphone. Please grant permission.";
          captionButton.textContent = start_singing;
        });
    };

    socket.onmessage = (event) => {
      const data = JSON.parse(event.data);

      if (data.isFinal) {
        // Accumulate final results
        finalTranscript += data.transcript + " ";
        finalWords.push(...data.words);
        // Show real-time final transcript
        captionOutput.textContent = finalTranscript.trim() || "🎤 Listening...";
        captionOutput.classList.add('visible');
      } else {
        // Display the interim transcript in real-time
        const currentText = finalTranscript + data.transcript;
        captionOutput.textContent = currentText.trim() || "🎤 Listening...";
        captionOutput.classList.add('visible');
      }
    };

    socket.onclose = () => {
      stopRecordingTimer(); // Ensure timer is hidden on close
      captionButton.textContent = start_singing;
      captionButton.disabled = false; // Re-enable button

      // --- Show transcribed text ---
      if (finalTranscript) {
        captionOutput.textContent = finalTranscript;
        captionOutput.classList.add('visible');
      } else {
        captionOutput.textContent = "No audio detected :(";
        captionOutput.classList.add('visible');
      }

      // --- Perform Scoring ---
      const originalRefrain = songRefrains[currentSongKey];
      if (originalRefrain && finalWords.length > 0) {
        const score = calculateScore(finalWords, originalRefrain);
        checkAndSaveHighScore(score.overallScore);
        let scoreHtml =
          `Score: <span class="score-value">${score.overallScore}/100</span><br>` +
          `(Accuracy: <span class="score-value">${score.accuracyScore}</span>, Confidence: <span class="score-value">${score.confidenceScore}</span>`;

        if (score.timingScore !== undefined) {
          scoreHtml += `, Timing: <span class="score-value">${score.timingScore}</span>)`;
        } else if (score.rhythmScore !== undefined) {
          scoreHtml += `, Rhythm: <span class="score-value">${score.rhythmScore}</span>)`;
        } else {
          scoreHtml += `)`;
        }
        finalScoreOutput.innerHTML = scoreHtml; // Use innerHTML to render spans
        finalScoreOutput.style.display = "block"; // Show the container
      }
    };

    socket.onerror = (err) => {
      console.error("WebSocket Error:", err);
      captionOutput.textContent =
        "Error: Could not connect to the server. Is it running?";
      captionButton.textContent = start_singing;
      captionButton.disabled = false; // Re-enable button
    };
  }
  
  function stopRecording() {
    debugLog('Stopping recording...');
    displayDebug('Stopping recording...');
    
    stopRecordingTimer();
    captionButton.textContent = "Processing...";
    captionButton.disabled = true;

    // Stop the audio source locally
    if (globalStream) {
      globalStream.getTracks().forEach((track) => track.stop());
    }
    if (audioContext) {
      audioContext.close();
    }

    // Signal the server that we are done sending audio
    if (socket && socket.readyState === WebSocket.OPEN) {
      socket.send(JSON.stringify({ action: "stop" }));
    }
  }

  // Game elements
  const listenBtn = document.getElementById('listen-btn');
  const checkBtn = document.getElementById('check-btn');
  const feedbackEl = document.getElementById('feedback');
  const audioPlayer = document.getElementById('audio-player');
  const answerInput = document.getElementById('answer-input');
  const playAgainBtn = document.getElementById('play-again-btn');

  let currentPhrase = '';
  let playerName = '';
  let isFetching = false;
  let roundTimerStart = 0;
  let recentRounds = [];

  if (listenBtn) {
    listenBtn.addEventListener("click", function(e) {
      e.preventDefault();
      console.log('🎧 Play Phrase button clicked!');
      debugLog('Play Phrase clicked', null, 'info');
      displayDebug('Fetching phrase...');
      playsound();
    });
    console.log('✅ Listen button initialized');
    debugLog('Listen button initialized', null, 'info');
  } else {
    console.error('❌ Listen button not found - cannot add event listener');
    debugLog('Listen button NOT FOUND', null, 'error');
  }
  
  if (checkBtn) {
    checkBtn.addEventListener('click', checkAnswer);
  }
  if (playAgainBtn) {
    playAgainBtn.addEventListener('click', resetGame);
  }

  const languageSelectLearning = document.getElementById('language-select-learning');
  let selectedLanguage = 'en-US'; // Default
  let originalPhraseText = ''; // Store the original phrase in the selected language

  // Language names for display
  const languageNames = {
    'en-US': 'English',
    'ja-JP': 'Japanese',
    'es-ES': 'Spanish',
    'pt-BR': 'Portuguese',
    'de-DE': 'German'
  };

  if (languageSelectLearning) {
    const trigger = languageSelectLearning.querySelector('.select-trigger');
    const options = languageSelectLearning.querySelectorAll('.option');
    const selectedText = trigger.querySelector('span');

    trigger.addEventListener('click', () => {
      languageSelectLearning.classList.toggle('open');
    });

    options.forEach(option => {
      option.addEventListener('click', () => {
        selectedLanguage = option.dataset.value;
        selectedText.innerHTML = option.innerHTML;
        options.forEach(opt => opt.classList.remove('selected'));
        option.classList.add('selected');
        languageSelectLearning.classList.remove('open');
        resetGame();
      });
    });

    document.addEventListener('click', (e) => {
      if (!languageSelectLearning.contains(e.target)) {
        languageSelectLearning.classList.remove('open');
      }
    });
  }

  const levenshtein = (s1, s2) => {
      s1 = s1.toLowerCase();
      s2 = s2.toLowerCase();
      const costs = [];
      for (let i = 0; i <= s1.length; i++) {
          let lastValue = i;
          for (let j = 0; j <= s2.length; j++) {
              if (i === 0) costs[j] = j;
              else if (j > 0) {
                  let newValue = costs[j - 1];
                  if (s1.charAt(i - 1) !== s2.charAt(j - 1)) {
                      newValue = Math.min(Math.min(newValue, lastValue), costs[j]) + 1;
                  }
                  costs[j - 1] = lastValue;
                  lastValue = newValue;
              }
          }
          if (i > 0) costs[s2.length] = lastValue;
      }
      return costs[s2.length];
  };

  async function playsound() {
    if (!listenBtn) {
      console.error('Listen button not found!');
      return;
    }
    
    listenBtn.disabled = true;
    listenBtn.textContent = 'Loading...';

    try {
      console.log(`📡 API Request: GET /api/new-phrase?language=${selectedLanguage}`);
      debugLog(`API Request: GET /api/new-phrase?language=${selectedLanguage}`, null, 'info');
      displayDebug(`Fetching new phrase in ${selectedLanguage}...`);
      
      const response = await fetch(`/api/new-phrase?language=${selectedLanguage}`);
      
      console.log(`📡 API Response: ${response.status} ${response.statusText}`);
      debugLog(`API Response: ${response.status} ${response.statusText}`, null, response.ok ? 'info' : 'error');
      
      if (!response.ok) {
        throw new Error(`API Error: ${response.status} ${response.statusText}`);
      }
      
      const data = await response.json();
      console.log('📡 Phrase received:', data.phrase);
      debugLog(`Phrase received: "${data.phrase}"`, null, 'info');
      
      currentPhrase = data.phrase;
      originalPhraseText = data.phrase; // Store the original phrase
      await synthesizeAndPlay(currentPhrase);
    } catch (error) {
      console.error('❌ Error fetching new phrase:', error);
      debugLog('Error fetching new phrase', error, 'error');
      displayError('Failed to fetch phrase', error.message);
      if (feedbackEl) {
        feedbackEl.textContent = 'Error fetching phrase: ' + error.message;
      }
    } finally {
      isFetching = false;
      if (listenBtn) {
        listenBtn.disabled = false;
        listenBtn.textContent = 'Play Phrase';
      }
    }
  }

  async function synthesizeAndPlay(text) {
    try {
      debugLog('API Request: POST /api/synthesize', { text: text.substring(0, 50) + '...', language: selectedLanguage });
      displayDebug('Synthesizing audio...');
      const response = await fetch('/api/synthesize', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: text, language: selectedLanguage }),
      });
      debugLog(`API Response: ${response.status} ${response.statusText}`);
      if (!response.ok) throw new Error(`Synthesis failed: ${response.status} ${response.statusText}`);
      const audioBlob = await response.blob();
      const audioUrl = URL.createObjectURL(audioBlob);
      debugLog('Audio blob created, size:', audioBlob.size);
      displayDebug(`Audio ready (${audioBlob.size} bytes)`);
      audioPlayer.src = audioUrl;
      audioPlayer.play();
    } catch (error) {
      console.error('Error synthesizing audio:', error);
      feedbackEl.textContent = 'Error generating audio.';
    }
  }

  audioPlayer.onended = () => {
      roundTimerStart = new Date();
      answerInput.disabled = false;
      checkBtn.disabled = false;
      answerInput.focus();
  };

  async function checkAnswer() {
      const responseTime = (new Date() - roundTimerStart) / 1000;
      const userAnswer = answerInput.value;

      const distance = levenshtein(userAnswer, currentPhrase);
      const accuracyScore = Math.max(0, 80 - (distance * 5));
      const timeBonus = Math.max(0, 20 - (responseTime * 2));
      const roundScore = Math.round(accuracyScore + timeBonus);

      // Get English translation if not already in English
      let feedbackHTML = `
          <span class="round-score">Your score: ${roundScore}</span>
          <span class="breakdown">
              (Accuracy: ${Math.round(accuracyScore)} + Time Bonus: ${Math.round(timeBonus)})
          </span>
      `;

      if (selectedLanguage !== 'en-US') {
        // Show original phrase in selected language
        feedbackHTML += `
          <div class="correct-phrase">
              <strong>Original phrase (${languageNames[selectedLanguage]}):</strong> ${originalPhraseText}
          </div>
        `;
        
        // Get English translation using the translation API
        try {
          feedbackHTML += `
            <div class="english-translation">
                <strong>English meaning:</strong> <span id="translation-loading">Translating...</span>
            </div>
          `;
          
          feedbackEl.innerHTML = feedbackHTML;
          
          // Extract language code from selectedLanguage (e.g., "es-ES" -> "es")
          const sourceLang = selectedLanguage.split('-')[0];
          
          // Request translation from backend
          const translateResponse = await fetch('/api/translate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              text: originalPhraseText,
              source_language: sourceLang
            })
          });
          
          if (translateResponse.ok) {
            const translationData = await translateResponse.json();
            // Update the translation text
            const translationEl = document.getElementById('translation-loading');
            if (translationEl) {
              translationEl.textContent = translationData.translated;
              translationEl.id = ''; // Remove the loading ID
            }
          } else {
            const translationEl = document.getElementById('translation-loading');
            if (translationEl) {
              translationEl.textContent = '(Translation unavailable)';
            }
          }
        } catch (error) {
          console.error('Translation error:', error);
          const translationEl = document.getElementById('translation-loading');
          if (translationEl) {
            translationEl.textContent = '(Translation error)';
          }
        }
      } else {
        // Already in English
        feedbackHTML += `
          <div class="correct-phrase">
              <strong>Correct phrase:</strong> ${currentPhrase}
          </div>
        `;
        feedbackEl.innerHTML = feedbackHTML;
      }

      listenBtn.disabled = true;
      checkBtn.disabled = true;
      answerInput.disabled = true;
      playAgainBtn.style.display = 'block';

      const scoreLearning = Math.round(accuracyScore)  + Math.round(timeBonus);

      modalScoreTextLearning.textContent = `You scored ${scoreLearning} points! Enter your name to save your score.`;
      scoreLearningInput.value = scoreLearning;
      playerNameInputLearning.value = "";
      modalLearning.style.display = "flex";
      playerNameInputLearning.focus();
  }

  function resetGame() {
      feedbackEl.innerHTML = '';
      answerInput.value = '';
      playAgainBtn.style.display = 'none';
      listenBtn.disabled = false;
  }


  /* Call Analysis Logic */

  // Translation data for different languages
  const translations = {
    en: [
      "My name is Bruno, good morning. How can I help you?",
      "Good morning. I'm calling because my bill came with 50 reais in additional services that I didn't contract, and to make it worse, I traveled to Santos and Belo Horizonte last week and had no signal at all, it's absurd.",
      "I perfectly understand your frustration, ma'am. I apologize for the inconvenience. Just a moment, please, I'll check your account.",
      "Hmm.",
      "Right, I found it here. There was indeed a billing error and we registered instability in the coverage of those regions.",
      "And so?",
      "I've already reversed the amount charged incorrectly and for the service failure, I'm applying a 40% discount on your next bill as compensation right now. Is that okay?",
      "Wow, 40%? Perfect, that's great. Resolved then, thank you very much.",
      "I thank you for the contact. Have a great day."
    ],
    es: [
      "Mi nombre es Bruno, buenos días. ¿En qué puedo ayudarle?",
      "Buenos días. Llamo porque mi factura vino con 50 reales en servicios adicionales que no contraté, y para empeorar, viajé a Santos y Belo Horizonte la semana pasada y no tuve señal, es absurdo.",
      "Entiendo perfectamente su frustración, señora. Le pido disculpas por las molestias. Un momento, por favor, verificaré su cuenta.",
      "Hmm.",
      "Bien, lo encontré aquí. Efectivamente hubo un error de facturación y registramos inestabilidad en la cobertura de esas regiones.",
      "¿Y entonces?",
      "Ya he revertido el monto cobrado incorrectamente y por la falla del servicio, estoy aplicando un descuento del 40% en su próxima factura como compensación ahora mismo. ¿Le parece bien?",
      "¡Vaya, 40%! Perfecto, así sí. Resuelto entonces, muchas gracias.",
      "Yo le agradezco el contacto. Que tenga un excelente día."
    ],
    fr: [
      "Je m'appelle Bruno, bonjour. Comment puis-je vous aider?",
      "Bonjour. J'appelle parce que ma facture est venue avec 50 reais de services supplémentaires que je n'ai pas contractés, et pour aggraver les choses, j'ai voyagé à Santos et Belo Horizonte la semaine dernière et je n'avais aucun signal, c'est absurde.",
      "Je comprends parfaitement votre frustration, madame. Je m'excuse pour le désagrément. Un instant, s'il vous plaît, je vais vérifier votre compte.",
      "Hmm.",
      "D'accord, je l'ai trouvé ici. Il y a effectivement eu une erreur de facturation et nous avons enregistré une instabilité de la couverture dans ces régions.",
      "Et alors?",
      "J'ai déjà annulé le montant facturé incorrectement et pour la panne de service, j'applique maintenant une réduction de 40% sur votre prochaine facture en compensation. Cela vous convient-il?",
      "Wow, 40%? Parfait, c'est génial. Résolu alors, merci beaucoup.",
      "Je vous remercie du contact. Passez une excellente journée."
    ],
    de: [
      "Mein Name ist Bruno, guten Morgen. Wie kann ich Ihnen helfen?",
      "Guten Morgen. Ich rufe an, weil meine Rechnung 50 Reais für zusätzliche Dienste enthielt, die ich nicht beauftragt habe, und um es noch schlimmer zu machen, bin ich letzte Woche nach Santos und Belo Horizonte gereist und hatte überhaupt kein Signal, das ist absurd.",
      "Ich verstehe Ihre Frustration vollkommen, gnädige Frau. Ich entschuldige mich für die Unannehmlichkeiten. Einen Moment bitte, ich werde Ihr Konto überprüfen.",
      "Hmm.",
      "Richtig, ich habe es hier gefunden. Es gab tatsächlich einen Abrechnungsfehler und wir haben Instabilität in der Abdeckung dieser Regionen registriert.",
      "Und dann?",
      "Ich habe den falsch berechneten Betrag bereits rückerstattet und für den Serviceausfall gewähre ich Ihnen jetzt sofort einen Rabatt von 40% auf Ihre nächste Rechnung als Entschädigung. Ist das in Ordnung?",
      "Wow, 40%? Perfekt, das ist großartig. Dann gelöst, vielen Dank.",
      "Ich danke Ihnen für den Kontakt. Haben Sie einen schönen Tag."
    ],
    it: [
      "Mi chiamo Bruno, buongiorno. Come posso aiutarla?",
      "Buongiorno. Chiamo perché la mia fattura è arrivata con 50 reais di servizi aggiuntivi che non ho contrattato, e per peggiorare le cose, ho viaggiato a Santos e Belo Horizonte la settimana scorsa e non avevo alcun segnale, è assurdo.",
      "Capisco perfettamente la sua frustrazione, signora. Mi scuso per l'inconveniente. Solo un momento, per favore, controllerò il suo account.",
      "Hmm.",
      "Giusto, l'ho trovato qui. C'è stato effettivamente un errore di fatturazione e abbiamo registrato instabilità nella copertura di quelle regioni.",
      "E allora?",
      "Ho già stornato l'importo addebitato in modo errato e per il guasto del servizio, sto applicando ora uno sconto del 40% sulla sua prossima fattura come compensazione. Va bene?",
      "Wow, 40%? Perfetto, è fantastico. Risolto allora, grazie mille.",
      "La ringrazio per il contatto. Buona giornata."
    ],
    ja: [
      "私の名前はブルーノです、おはようございます。どのようにお手伝いできますか？",
      "おはようございます。契約していない追加サービスに50レアルの請求があったので電話しています。さらに悪いことに、先週サントスとベロオリゾンテに旅行したのですが、まったく信号がありませんでした。ばかげています。",
      "お客様のご不満は十分に理解しております。ご不便をおかけして申し訳ございません。少々お待ちください、お客様のアカウントを確認いたします。",
      "うーん。",
      "はい、こちらで見つかりました。確かに請求エラーがあり、それらの地域でのカバレッジの不安定性を記録しました。",
      "それで？",
      "誤って請求された金額はすでに返金しました。そして、サービス障害に対する補償として、次回の請求書に40％の割引を適用しています。よろしいですか？",
      "えっ、40%？完璧です、素晴らしいです。それでは解決ですね、どうもありがとうございます。",
      "ご連絡ありがとうございました。良い一日をお過ごしください。"
    ],
    zh: [
      "我叫布鲁诺，早上好。我能帮您什么？",
      "早上好。我打电话是因为我的账单中有50雷亚尔的额外服务费用，而这些服务我并没有订购。更糟糕的是，上周我去了桑托斯和贝洛奥里藏特，完全没有信号，太荒谬了。",
      "我完全理解您的沮丧，女士。对于给您带来的不便，我深表歉意。请稍等，我来查看您的账户。",
      "嗯。",
      "好的，我在这里找到了。确实存在计费错误，我们记录了这些地区的覆盖不稳定。",
      "然后呢？",
      "我已经退还了错误收取的金额，作为服务故障的补偿，我现在正在为您的下一张账单申请40%的折扣。可以吗？",
      "哇，40%？太好了，这样就好。那就解决了，非常感谢。",
      "感谢您的联系。祝您有美好的一天。"
    ],
    ko: [
      "제 이름은 브루노입니다, 좋은 아침입니다. 어떻게 도와드릴까요?",
      "좋은 아침입니다. 제가 계약하지 않은 추가 서비스에 50헤알이 청구되어 전화드렸습니다. 더 나쁜 것은 지난주에 산투스와 벨루오리존치를 여행했는데 전혀 신호가 없었습니다. 말도 안 됩니다.",
      "고객님의 불만을 완전히 이해합니다. 불편을 끼쳐 드려 죄송합니다. 잠시만 기다려 주십시오, 계정을 확인하겠습니다.",
      "음.",
      "네, 여기서 찾았습니다. 실제로 청구 오류가 있었고 해당 지역의 커버리지 불안정성을 기록했습니다.",
      "그래서요?",
      "이미 잘못 청구된 금액을 환불했으며, 서비스 장애에 대한 보상으로 지금 바로 다음 청구서에 40% 할인을 적용하고 있습니다. 괜찮으신가요?",
      "와, 40%요? 완벽해요, 정말 좋네요. 그럼 해결됐네요, 정말 감사합니다.",
      "연락 주셔서 감사합니다. 좋은 하루 보내세요."
    ]
  };

  let currentTranslationLanguage = 'en';

  // Setup translation language selector
  const translationLanguageSelect = document.getElementById('translation-language-select');
  if (translationLanguageSelect) {
    const trigger = translationLanguageSelect.querySelector('.select-trigger');
    const options = translationLanguageSelect.querySelectorAll('.option');
    const selectedText = trigger.querySelector('span');

    trigger.addEventListener('click', () => {
      translationLanguageSelect.classList.toggle('open');
    });

    options.forEach(option => {
      option.addEventListener('click', () => {
        currentTranslationLanguage = option.dataset.value;
        selectedText.innerHTML = option.innerHTML;
        options.forEach(opt => opt.classList.remove('selected'));
        option.classList.add('selected');
        translationLanguageSelect.classList.remove('open');
        
        // Update translations if analysis is already displayed
        updateTranslations();
      });
    });

    document.addEventListener('click', (e) => {
      if (!translationLanguageSelect.contains(e.target)) {
        translationLanguageSelect.classList.remove('open');
      }
    });
  }

  function updateTranslations() {
    const translationElements = document.querySelectorAll('.translation-text');
    const translationTexts = translations[currentTranslationLanguage];
    
    if (translationElements.length > 0 && translationTexts) {
      translationElements.forEach((element, index) => {
        if (translationTexts[index]) {
          element.textContent = translationTexts[index];
        }
      });
    }
  }

  document.getElementById('analyze-sentiment-button').addEventListener('click', function() {
  var analysisContainer = document.getElementById('analysis-container');
  var loadingSpinner = document.getElementById('loading-spinner');
  var analysisMessage = document.getElementById('analysis-message');
  var analyzeButton = document.getElementById('analyze-sentiment-button');
  var analysisTable = document.getElementById('analysis-table');


  // Hide button and show loading spinner
  analyzeButton.style.display = 'none';
  analysisContainer.style.display = 'block';
  loadingSpinner.style.display = 'block';
  analysisMessage.style.display = 'none';

  setTimeout(function() {
    // Hide loading spinner and show message
    loadingSpinner.style.display = 'none';
    analysisMessage.style.display = 'block';
    analysisTable.style.display = 'block';
    
    // Apply translations
    updateTranslations();
  }, 4000);
  });
});
