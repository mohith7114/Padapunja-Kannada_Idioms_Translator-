 
    let typingTimer;
    let activeTab = "kn"; // Default tab Kannada
    const inputBox = document.getElementById('inputText');
    const sidebar = document.getElementById('sidebar');
    const menuToggle = document.getElementById('menu-toggle');
    const closeMenu = document.getElementById('close-menu');

    // store last translation data for speech playback
    let lastTranslationData = { plainKn: '', plainEn: '' };

    menuToggle.addEventListener('click', () => sidebar.classList.remove('-translate-x-full'));
    closeMenu.addEventListener('click', () => sidebar.classList.add('-translate-x-full'));
    document.getElementById('sidebar-nav').addEventListener('click', e => {
      if (e.target.closest('button')) sidebar.classList.add('-translate-x-full');
    });

    // Tabs
    const tabKnBtn = document.getElementById("tab-kn");
    const tabEnBtn = document.getElementById("tab-en");
    tabKnBtn.addEventListener("click", () => {
      activeTab = "kn";
      tabKnBtn.classList.add("text-blue-600","border-b-2","border-blue-600");
      tabEnBtn.classList.remove("text-blue-600","border-b-2","border-blue-600");
      translate();
    });
    tabEnBtn.addEventListener("click", () => {
      activeTab = "en";
      tabEnBtn.classList.add("text-blue-600","border-b-2","border-blue-600");
      tabKnBtn.classList.remove("text-blue-600","border-b-2","border-blue-600");
      translate();
    });

    function toggleModal(id, show) {
      const modal = document.getElementById(id);
      show ? modal.classList.remove('hidden') : modal.classList.add('hidden');
    }

    inputBox.addEventListener('input', () => {
      clearTimeout(typingTimer);
      typingTimer = setTimeout(translate, 500);
    });

    
    // ========== UPDATED TRANSLATE FUNCTION  ==========
  
    async function translate() {
      const sentence = inputBox.value.trim();
      const outputDiv = document.getElementById('output');

      // reset lastTranslationData while fetching
      lastTranslationData = { plainKn: '', plainEn: '' };

      if (!sentence) {
        outputDiv.innerHTML = `<div class="text-center text-slate-400 pt-16"><i class="fas fa-language text-4xl"></i><p>Your translation will appear here.</p></div>`;
        return;
      }
      try {
        const res = await fetch('http://127.0.0.1:5000/translate', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ sentence })
        });
        const data = await res.json();

        // prepare plain text fallbacks for TTS
        let plainKannadaText = sentence;
        let plainEnglishText = data.literal_meaning_en || "";

        if (data.status === 'idiom_detected') {
          // These are the FINAL sentences with explanations
          plainKannadaText = data.full_sentence_kannada || sentence;
          plainEnglishText = data.full_sentence_english || data.literal_meaning_en || "";

          // --- NEW MULTI-IDIOM HTML ---
          let kannadaIdiomsHtml = '';
          let englishIdiomsHtml = '';

          // Loop over the new 'results_list' array
          data.results_list.forEach(item => {
            const idiomPhraseKn = item.result.idiom;
            const kannadaMeaning = item.result.explanation_kannada || "—";
            // Use the new translated field, fallback to the Kannada phrase
            const idiomPhraseEn = item.idiom_english_translation || idiomPhraseKn; 
            // This field already includes the auto-translate logic from app.py
            const englishMeaning = item.result.explanation_english || "—"; 

            kannadaIdiomsHtml += `
              <div class="p-3 bg-blue-50 border-l-4 border-blue-400 rounded-r-lg">
                <p class="font-semibold text-blue-700">ಪತ್ತೆಯಾದ ನುಡಿಗಟ್ಟು:</p>
                <p><span class="kannada-font">${idiomPhraseKn}</span></p>
                <p class="kannada-font"><strong>ಅರ್ಥ:</strong> ${kannadaMeaning}</p>
              </div>`;
            
            englishIdiomsHtml += `
              <div class="p-3 bg-blue-50 border-l-4 border-blue-400 rounded-r-lg">
                <p class="font-semibold text-blue-700">Detected Idiom:</p>
                <p>${idiomPhraseEn}</p> 
                <p><strong>Meaning:</strong> ${englishMeaning}</p>
              </div>`;
          });
          // --- END NEW MULTI-IDIOM HTML ---

          if (activeTab === "kn") {
            outputDiv.innerHTML = `
              <div class="space-y-4">
                <div class="p-3 bg-red-50 border-l-4 border-red-400 rounded-r-lg">
                  <p class="font-semibold text-red-700">ವಾಕ್ಯದ ಸಾಮಾನ್ಯ ಅರ್ಥ:</p>
                  <p class="mt-1 kannada-font">${sentence}</p> 
                </div>
                
                ${kannadaIdiomsHtml} 

                <div class="p-3 bg-green-50 border-l-4 border-green-400 rounded-r-lg">
                  <p class="font-semibold text-green-700">ವಿವರಣೆ (ಪೂರ್ಣ ಕನ್ನಡ ವಾಕ್ಯ):</p>
                  <p class="kannada-font">${plainKannadaText}</p> 
                </div>
              </div>`;
          } else {
            outputDiv.innerHTML = `
              <div class="space-y-4">
                <div class="p-3 bg-red-50 border-l-4 border-red-400 rounded-r-lg">
                  <p class="font-semibold text-red-700">Google Meaning:</p>
                  <p class="italic">${data.literal_meaning_en}</p>
                </div>
                
                ${englishIdiomsHtml}

                <div class="p-3 bg-green-50 border-l-4 border-green-400 rounded-r-lg">
                  <p class="font-semibold text-green-700">Actual Meaning:</p>
                  <p>${plainEnglishText}</p>
                </div>
              </div>`;
          }

        } else {
          // no idiom detected — This part is unchanged
          plainKannadaText = data.literal_meaning_kn || sentence;
          plainEnglishText = data.normal_translation || data.literal_meaning_en || "";

          if (activeTab === "kn") {
            outputDiv.innerHTML = `<div class="p-3 bg-gray-50 border-l-4 border-gray-400 rounded-r-lg">
              <p class="font-semibold text-gray-700">ಅನುವಾದ:</p>
              <p class="kannada-font">${plainKannadaText}</p>
            </div>`;
          } else {
            outputDiv.innerHTML = `<div class="p-3 bg-gray-50 border-l-4 border-gray-400 rounded-r-lg">
              <p class="font-semibold text-gray-700">Translation:</p>
              <p class="text-slate-600">${plainEnglishText}</p>
            </div>`;
          }
        }

        // store plain texts for use by speakOutput()
        lastTranslationData = {
          plainKn: plainKannadaText,
          plainEn: plainEnglishText
        };

      } catch (err) {
        console.error(err); // Log the actual error to the console
        outputDiv.innerHTML = `<div class="text-center text-red-500 pt-16"><i class="fas fa-exclamation-triangle text-4xl"></i><p>Could not fetch translation.</p></div>`;
        lastTranslationData = { plainKn: inputBox.value.trim(), plainEn: "" };
      }
    }
    // ===================================================================
    // ========== END OF UPDATED FUNCTION ==========
    // ===================================================================

    async function loadHistory() {
      try {
        const res = await fetch('http://127.0.0.1:5000/history');
        const history = await res.json();
        let html = "";
        if (history.length === 0) {
          html = `<p class="text-slate-500 text-center">Your history is empty.</p>`;
        } else {
          history.reverse().forEach(entry => {
            html += `<div class="p-3 border rounded-lg bg-slate-50 flex items-start space-x-2">
              <input type="checkbox" class="history-checkbox mt-1" value="${entry.timestamp}">
              <div>
                <p class="text-xs text-slate-400 mb-1">${entry.timestamp}</p>
                <p class="kannada-font font-semibold">📝 ${entry.original_sentence}</p>
                <p class="text-slate-600">➡️ ${entry.translation}</p>
              </div>
            </div>`;
          });
        }
        document.getElementById('history').innerHTML = html;
        toggleModal('history-modal', true);
      } catch {
        alert('Could not load history.');
      }
    }

    async function clearHistory() {
      if (!confirm("Clear all history?")) return;
      await fetch('http://127.0.0.1:5000/clear_history', { method: 'POST' });
      document.getElementById('history').innerHTML = `<p class="text-slate-500 text-center">History cleared.</p>`;
    }

    async function clearSelectedHistory() {
      const checkboxes = document.querySelectorAll('.history-checkbox:checked');
      if (checkboxes.length === 0) return alert("Select at least one entry.");
      const timestamps = Array.from(checkboxes).map(cb => cb.value);
      await fetch('http://127.0.0.1:5000/delete_history', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ timestamps })
      });
      loadHistory();
    }

    // Speak output using backend gTTS synthesize endpoint (will return mp3)
    async function speakOutput() {
      // choose which text to speak depending on active tab
      let text = "";
      let lang = "kn";

      if (activeTab === "en") {
        text = lastTranslationData.plainEn || lastTranslationData.plainKn || inputBox.value.trim();
        lang = "en";
      } else {
        text = lastTranslationData.plainKn || inputBox.value.trim();
        lang = "kn";
      }

      if (!text || text.trim().length === 0) {
        return alert("No text available to speak. Please translate a sentence first.");
      }

      try {
        // call backend /synthesize endpoint which uses gTTS (GET: text param, optional lang)
        const url = `http://127.0.0.1:5000/synthesize?text=${encodeURIComponent(text)}&lang=${encodeURIComponent(lang)}`;
        const resp = await fetch(url);
        if (!resp.ok) throw new Error("Synthesis failed");
        const blob = await resp.blob();
        const audioUrl = URL.createObjectURL(blob);
        const audio = new Audio(audioUrl);
        audio.play();
        // release object URL after playback
        audio.onended = () => URL.revokeObjectURL(audioUrl);
      } catch (err) {
        console.error(err);
        alert("Could not synthesize speech. Make sure the backend is running and /synthesize is accessible.");
      }
    }

    // fallback / unused direct browser TTS (kept for reference)
    function speakKannada() {
      const text = document.getElementById('output').innerText;
      const msg = new SpeechSynthesisUtterance(text);
      msg.lang = 'kn-IN';
      window.speechSynthesis.speak(msg);
    }

    function startMic() {
      const Recognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      if (!Recognition) return alert('Speech recognition not supported.');
      const recog = new Recognition();
      recog.lang = 'kn-IN';
      recog.onresult = e => {
        document.getElementById('inputText').value = e.results[0][0].transcript;
        translate();
      };
      recog.start();
    }

    function showFeedbackForm() { toggleModal('feedback-modal', true); }
    async function submitFeedback() {
      const text = document.getElementById('feedbackText').value;
      if (!text.trim()) return alert("Please enter feedback.");
      await fetch('http://127.0.0.1:5000/feedback', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ feedback: text })
      });
      alert('Feedback sent! Thank you.');
      document.getElementById('feedbackText').value = '';
      toggleModal('feedback-modal', false);
    }

    function showSuggestionForm() { 
    toggleModal('suggestion-modal', true); 
}

async function submitSuggestion() {
    const idiom = document.getElementById('suggestIdiom').value;
    const meaning = document.getElementById('suggestMeaning').value;
    const example = document.getElementById('suggestExample').value;

    if (!idiom  || !example) {
        return alert("Please fill in all fields.");
    }

    try {
        const response = await fetch('/suggest_idiom', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ idiom, meaning, example })
        });
        
        const result = await response.json();
        
        if (result.message) {
            alert(result.message);
            // Clear fields and close modal
            document.getElementById('suggestIdiom').value = '';
            document.getElementById('suggestMeaning').value = '';
            document.getElementById('suggestExample').value = '';
            toggleModal('suggestion-modal', false);
        } else if (result.error) {
            alert("Error: " + result.error);
        }
    } catch (e) {
        console.error(e);
        alert("Failed to submit suggestion.");
    }
}
 