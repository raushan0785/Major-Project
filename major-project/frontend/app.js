
const API_URL = "http://127.0.0.1:8000";
let currentMethod = 'audio';
let transcriptionEdited = false;

console.log("App.js loaded!");

// --- Auth State ---
function getToken() {
    return localStorage.getItem("token");
}

function setToken(token) {
    localStorage.setItem("token", token);
}

function removeToken() {
    localStorage.removeItem("token");
}

function checkAuth() {
    console.log("Checking auth...");
    const token = getToken();
    if (token) {
        console.log("Token found, showing dashboard");
        showDashboard();
    } else {
        console.log("No token, showing auth");
        showAuth();
    }
}

function getUserInfo() {
    return localStorage.getItem("user_name") || "User";
}

// --- UI Navigation ---
function showAuth() {
    document.getElementById("auth-section").classList.remove("hidden");
    document.getElementById("dashboard-section").classList.add("hidden");
    // Ensure one form is shown
    if (document.getElementById("login-form").classList.contains("hidden") &&
        document.getElementById("signup-form").classList.contains("hidden")) {
        toggleAuth('login');
    }
}

function showDashboard() {
    document.getElementById("auth-section").classList.add("hidden");
    document.getElementById("dashboard-section").classList.remove("hidden");
    const userDisplay = document.getElementById("user-display-name");
    if (userDisplay) userDisplay.innerText = getUserInfo();
    loadSRSList();
}

// Made global to be accessible via onclick if needed
window.toggleAuth = function (mode) {
    console.log("Toggling auth to:", mode);
    if (mode === 'login') {
        document.getElementById("login-form").classList.remove("hidden");
        document.getElementById("signup-form").classList.add("hidden");
    } else {
        document.getElementById("login-form").classList.add("hidden");
        document.getElementById("signup-form").classList.remove("hidden");
    }
}

window.switchMethod = function (method) {
    currentMethod = method;
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));

    // Update tabs
    const tabs = document.querySelectorAll('.tab-btn');
    if (method === 'audio' && tabs[0]) tabs[0].classList.add('active');
    if (method === 'text' && tabs[1]) tabs[1].classList.add('active');

    if (method === 'audio') {
        document.getElementById('audio-input-area').classList.remove('hidden');
        document.getElementById('text-input-area').classList.add('hidden');
    } else {
        document.getElementById('audio-input-area').classList.add('hidden');
        document.getElementById('text-input-area').classList.remove('hidden');
    }
}

// --- Loading & Toast Utils ---
function showLoading(elementId) {
    const el = document.getElementById(elementId);
    if (el) el.classList.remove("hidden");
}

function hideLoading(elementId) {
    const el = document.getElementById(elementId);
    if (el) el.classList.add("hidden");
}

function showToast(message, type = "info") {
    const toast = document.getElementById("toast");
    if (!toast) return;
    toast.innerText = message;
    toast.className = "show";

    if (type === "error") toast.style.backgroundColor = "#cf6679";
    else if (type === "success") toast.style.backgroundColor = "#03dac6";
    else toast.style.backgroundColor = "#bb86fc";

    setTimeout(() => { toast.className = toast.className.replace("show", ""); }, 3000);
}

function clearAuthAndShowLogin() {
    removeToken();
    localStorage.removeItem("user_name");
    showAuth();
    showToast("Session expired. Please login again.", "error");
}

// --- API Calls ---

window.login = async function () {
    console.log("Login clicked");
    const emailInput = document.getElementById("login-email");
    const passwordInput = document.getElementById("login-password");
    const btn = document.getElementById("login-btn");

    const email = emailInput.value;
    const password = passwordInput.value;

    if (!email || !password) return showToast("Please enter email and password", "error");

    btn.disabled = true;
    btn.innerText = "Logging in...";

    try {
        const response = await fetch(`${API_URL}/auth/login`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email, password })
        });

        if (!response.ok) {
            const data = await response.json();
            throw new Error(data.detail || "Login failed");
        }

        const data = await response.json();
        setToken(data.access_token);
        localStorage.setItem("user_name", email.split('@')[0]);

        showToast("Login Successful!", "success");
        setTimeout(showDashboard, 500);
    } catch (err) {
        console.error("Login error:", err);
        showToast(err.message, "error");
    } finally {
        btn.disabled = false;
        btn.innerText = "Login";
    }
}

window.signup = async function () {
    console.log("Signup clicked");
    const name = document.getElementById("signup-name").value;
    const email = document.getElementById("signup-email").value;
    const password = document.getElementById("signup-password").value;
    const btn = document.getElementById("signup-btn");

    if (!email || !password || !name) return showToast("Please fill all fields", "error");

    btn.disabled = true;
    btn.innerText = "Signing up...";

    try {
        const response = await fetch(`${API_URL}/auth/signup`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                email,
                password,
                full_name: name
            })
        });

        if (!response.ok) {
            const data = await response.json();
            throw new Error(data.detail || "Signup failed");
        }

        showToast("Account created! Please login.", "success");
        window.toggleAuth('login');
        document.getElementById("login-email").value = email;
    } catch (err) {
        console.error("Signup error:", err);
        showToast(err.message, "error");
    } finally {
        btn.disabled = false;
        btn.innerText = "Sign Up";
    }
}

window.logout = function () {
    removeToken();
    localStorage.removeItem("user_name");
    showAuth();
    showToast("Logged out", "info");
}

window.transcribeAudio = async function () {
    const fileInput = document.getElementById("audio-file");
    const file = fileInput.files[0];
    const btn = document.getElementById("transcribe-btn");

    if (!file) return showToast("Please select a file", "error");

    btn.disabled = true;
    showLoading("transcribe-loading");
    document.getElementById("transcription-result").classList.add("hidden");

    const formData = new FormData();
    formData.append("file", file);

    try {
        const token = getToken();
        const response = await fetch(`${API_URL}/transcribe/`, {
            method: "POST",
            headers: { "Authorization": `Bearer ${token}` },
            body: formData
        });

        if (!response.ok) throw new Error("Transcription failed");

        const data = await response.json();

        document.getElementById("transcription-result").classList.remove("hidden");
        document.getElementById("transcription-text").value = data.text;
        document.getElementById("transcription-id").value = data.transcription_id;
        transcriptionEdited = false;
        document.getElementById("transcription-text").addEventListener("input", () => { transcriptionEdited = true; });
        showToast("Audio transcribed!", "success");

    } catch (err) {
        showToast(err.message, "error");
    } finally {
        hideLoading("transcribe-loading");
        btn.disabled = false;
    }
}

window.enableEdit = function () {
    const textarea = document.getElementById("transcription-text");
    textarea.removeAttribute("readonly");
    textarea.focus();
    document.getElementById("edit-btn").style.display = "none";
    transcriptionEdited = true; // Since editing is enabled, assume it might be edited
}

window.generateSRS = async function () {
    const templateName = document.getElementById("template-select").value;
    const btn = document.getElementById("generate-btn");
    let payload = { template_name: templateName };

    if (currentMethod === 'audio') {
        if (transcriptionEdited) {
            const text = document.getElementById("transcription-text").value;
            if (!text) return showToast("Please transcribe audio first", "error");
            payload.input_text = text;
        } else {
            const transcriptionId = document.getElementById("transcription-id").value;
            if (!transcriptionId) return showToast("Please transcribe audio first", "error");
            payload.transcription_id = transcriptionId;
        }
    } else {
        const text = document.getElementById("direct-text").value;
        if (!text) return showToast("Please enter requirements", "error");
        payload.input_text = text;
    }

    await generateSRSWithPayload(payload, btn);
}

window.generateSRSWithSelected = function () {
    // Ensure selectedSuggestionText is derived from the currently selected radio,
    // in case the page was cached and the default auto-select didn't run.
    const container = document.getElementById("grammar-suggestions");
    if (container) {
        const selectedRadio = container.querySelector('input[name="grammar-suggestion"]:checked');
        if (selectedRadio) {
            const index = parseInt(selectedRadio.value, 10);
            const suggestionItems = container.querySelectorAll(".suggestion-item");
            if (suggestionItems[index]) {
                const textMatch = suggestionItems[index].querySelector(".suggestion-text");
                if (textMatch) selectedSuggestionText = textMatch.textContent;
            }
        }
    }
    if (!selectedSuggestionText || typeof selectedSuggestionText !== "string") {
        showToast("Please select a suggestion first", "error");
        return;
    }
    
    // Close the modal
    closeGrammarModal();
    
    // Set up the payload with the selected suggestion
    const templateName = document.getElementById("template-select").value;
    const payload = { 
        template_name: templateName,
        input_text: selectedSuggestionText
    };
    
    // Trigger SRS generation directly (no button to disable since we're in modal)
    generateSRSWithPayload(payload);
}

async function generateSRSWithPayload(payload, btn = null) {
    if (btn) btn.disabled = true;
    showLoading("generate-loading");

    try {
        const token = getToken();
        // Updated route to match backend
        const response = await fetch(`${API_URL}/generate_srs`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`
            },
            body: JSON.stringify(payload)
        });

        if (response.status === 401) {
            clearAuthAndShowLogin();
            return;
        }

        if (!response.ok) {
            const errData = await response.json();
            const detail = errData && Object.prototype.hasOwnProperty.call(errData, "detail") ? errData.detail : null;
            const msg = (typeof detail === "string" && detail.trim()) ? detail : JSON.stringify(detail ?? errData ?? "Generation failed");
            throw new Error(msg);
        }

        const data = await response.json();
        showToast("SRS Generated Successfully!", "success");
        loadSRSList();

    } catch (err) {
        showToast(err.message, "error");
    } finally {
        hideLoading("generate-loading");
        if (btn) btn.disabled = false;
    }
}

window.loadSRSList = async function () {
    showLoading("list-loading");
    try {
        const token = getToken();
        if (!token) return;

        const response = await fetch(`${API_URL}/generate_srs/list`, {
            headers: { "Authorization": `Bearer ${token}` }
        });

        if (!response.ok) throw new Error("Failed to load list");

        const list = await response.json();
        const tbody = document.getElementById("srs-list-body");
        if (tbody) {
            tbody.innerHTML = "";
            if (list.length === 0) {
                tbody.innerHTML = "<tr><td colspan='4' style='text-align:center'>No documents yet. Generate one!</td></tr>";
            } else {
                list.forEach(item => {
                    const date = new Date(item.created_at).toLocaleDateString();
                    const textShort = item.input_text ? item.input_text.substring(0, 50) + "..." : "Audio Transcription";

                    const tr = document.createElement("tr");
                    tr.innerHTML = `
                        <td>${textShort}</td>
                        <td><span class="badge">${item.template_used}</span></td>
                        <td>${date}</td>
                        <td>
                            <button onclick="downloadSRS('${item.srs_id}', this)" class="secondary-btn small-btn">Download PDF</button>
                        </td>
                    `;
                    tbody.appendChild(tr);
                });
            }
        }

    } catch (err) {
        console.error(err);
        showToast("Failed to load history", "error");
    } finally {
        hideLoading("list-loading");
    }
}

window.downloadSRS = function (srsId, btnElement) {
    const originalText = btnElement.innerText;
    btnElement.innerText = "Downloading...";
    btnElement.disabled = true;

    fetch(`${API_URL}/export/${srsId}`, {
        headers: { "Authorization": `Bearer ${getToken()}` }
    })
        .then(async resp => {
            if (resp.status === 401) {
                clearAuthAndShowLogin();
                throw new Error("Session expired. Please login again.");
            }
            if (resp.status === 200) return resp.blob();
            const errText = await resp.text().catch(() => null);
            throw new Error(errText ? errText : `Download failed (HTTP ${resp.status})`);
        })
        .then(blob => {
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = url;
            a.download = `srs_${srsId}.pdf`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            showToast("Download started", "success");
        })
        .catch(err => {
            showToast("Download failed: " + err.message, "error");
        })
        .finally(() => {
            btnElement.innerText = originalText;
            btnElement.disabled = false;
        });
}

// --- Analysis Modules (Gap / Market) ---
function getCurrentRequirementText() {
    if (currentMethod === 'audio') {
        const el = document.getElementById("transcription-text");
        return el ? el.value : "";
    }
    const el = document.getElementById("direct-text");
    return el ? el.value : "";
}

function openAnalysisModal() {
    document.getElementById("analysis-modal").classList.remove("hidden");
    document.getElementById("analysis-output").textContent = "";
    showElement("analysis-error", false);
    hideElement("analysis-loading");
}

window.closeAnalysisModal = function () {
    document.getElementById("analysis-modal").classList.add("hidden");
    document.getElementById("analysis-output").textContent = "";
    hideElement("analysis-error");
    hideElement("analysis-loading");
}

async function generateAnalysisModule(moduleName) {
    const token = getToken();
    if (!token) {
        showToast("Please login first", "error");
        return;
    }

    const inputText = getCurrentRequirementText();
    if (!inputText || inputText.trim().length < 10) {
        showToast("Please enter requirements first", "error");
        return;
    }

    openAnalysisModal();
    showLoading("analysis-loading");
    hideElement("analysis-error");

    try {
        const titleMap = {
            "gap": "📉 Gap Analysis",
            "market": "📊 Market Analysis"
        };
        const titleEl = document.getElementById("analysis-modal-title");
        if (titleEl && titleMap[moduleName]) titleEl.textContent = titleMap[moduleName];

        const response = await fetch(`${API_URL}/analysis/${moduleName}`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`
            },
            body: JSON.stringify({ input_text: inputText })
        });

        if (response.status === 401) {
            clearAuthAndShowLogin();
            return;
        }

        if (!response.ok) {
            const errData = await response.json().catch(() => null);
            const detail = errData && Object.prototype.hasOwnProperty.call(errData, "detail") ? errData.detail : null;
            const msg = (typeof detail === "string" && detail.trim()) ? detail : JSON.stringify(detail ?? errData ?? "Analysis failed");
            throw new Error(msg);
        }

        const data = await response.json();
        document.getElementById("analysis-output").textContent = data.analysis_text || "";
        showToast("Analysis generated successfully!", "success");
    } catch (err) {
        showElement("analysis-error", true);
        document.getElementById("analysis-error").innerText = "Error: " + err.message;
    } finally {
        hideLoading("analysis-loading");
    }
}

window.showGapAnalysis = function () {
    generateAnalysisModule("gap");
}

window.showMarketAnalysis = function () {
    generateAnalysisModule("market");
}

// --- Grammar Correction ---
let currentGrammarText = "";
let selectedSuggestionText = "";

window.checkGrammar = async function () {
    // Get the text to check
    let textToCheck = "";
    
    if (currentMethod === 'audio') {
        const transcriptionText = document.getElementById("transcription-text").value;
        if (!transcriptionText) {
            return showToast("Please transcribe audio first", "error");
        }
        textToCheck = transcriptionText;
    } else {
        const directText = document.getElementById("direct-text").value;
        if (!directText) {
            return showToast("Please enter requirements first", "error");
        }
        textToCheck = directText;
    }
    
    if (textToCheck.length < 3) {
        return showToast("Text must be at least 3 characters long", "error");
    }
    
    currentGrammarText = textToCheck;
    selectedSuggestionText = "";
    
    // Show modal and loading state
    document.getElementById("grammar-modal").classList.remove("hidden");
    showLoading("grammar-loading");
    hideElement("grammar-error");
    
    document.getElementById("grammar-original").innerHTML = `
        <div class="original-box">
            <strong>Original Text:</strong>
            <textarea class="prompt-text-preview" rows="5" readonly>${escapeHtml(textToCheck)}</textarea>
        </div>
    `;
    
    try {
        const token = getToken();
        const response = await fetch(`${API_URL}/grammar/suggest-prompts`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`
            },
            body: JSON.stringify({ text: textToCheck })
        });
        
        if (response.status === 401) {
            clearAuthAndShowLogin();
            return;
        }

        if (!response.ok) {
            const errData = await response.json().catch(() => null);
            const detail = errData && Object.prototype.hasOwnProperty.call(errData, "detail") ? errData.detail : null;
            throw new Error((typeof detail === "string" && detail.trim()) ? detail : "Grammar correction failed");
        }
        
        const data = await response.json();
        renderGrammarSuggestions(data.suggestions);
        
    } catch (err) {
        console.error("Grammar check error:", err);
        showElement("grammar-error", true);
        document.getElementById("grammar-error").innerText = "Error: " + err.message;
    } finally {
        hideLoading("grammar-loading");
    }
}

function renderGrammarSuggestions(suggestions) {
    const container = document.getElementById("grammar-suggestions");
    container.innerHTML = "";
    
    if (!suggestions || suggestions.length === 0) {
        container.innerHTML = "<p>No suggestions available.</p>";
        return;
    }
    
    suggestions.forEach((suggestion, index) => {
        const suggestionDiv = document.createElement("div");
        suggestionDiv.className = "suggestion-item";
        
        const radioId = `suggestion-${index}`;
        const isDefaultSelected = index === 0;
        
        suggestionDiv.innerHTML = `
            <div class="suggestion-radio">
                <input type="radio" id="${radioId}" name="grammar-suggestion" value="${index}" 
                    ${isDefaultSelected ? "checked" : ""}
                    onchange="selectSuggestion(${index})">
                <label for="${radioId}">
                    <span class="suggestion-number">Option ${suggestion.option_number}:</span>
                    <span class="suggestion-text">${escapeHtml(suggestion.corrected_text)}</span>
                </label>
            </div>
            ${suggestion.explanation ? `<p class="suggestion-explanation">${escapeHtml(suggestion.explanation)}</p>` : ''}
        `;
        
        container.appendChild(suggestionDiv);
    });

    // Auto-select first suggestion for smoother flow
    if (suggestions[0] && suggestions[0].corrected_text) {
        selectedSuggestionText = suggestions[0].corrected_text;
    }
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function showElement(elementId, show = true) {
    const el = document.getElementById(elementId);
    if (el) {
        if (show) {
            el.classList.remove("hidden");
        } else {
            el.classList.add("hidden");
        }
    }
}

function hideElement(elementId) {
    showElement(elementId, false);
}

window.selectSuggestion = function (index) {
    const container = document.getElementById("grammar-suggestions");
    const suggestions = container.querySelectorAll(".suggestion-item");
    
    if (suggestions[index]) {
        const radio = suggestions[index].querySelector('input[type="radio"]');
        const textMatch = suggestions[index].querySelector('.suggestion-text');
        if (radio && textMatch) {
            selectedSuggestionText = textMatch.textContent;
        }
    }
}

window.useSelectedSuggestion = function () {
    if (!selectedSuggestionText) {
        showToast("Please select a suggestion", "error");
        return;
    }
    
    // Update the text field with the selected suggestion
    if (currentMethod === 'audio') {
        document.getElementById("transcription-text").value = selectedSuggestionText;
        transcriptionEdited = true;
    } else {
        document.getElementById("direct-text").value = selectedSuggestionText;
    }
    
    closeGrammarModal();
    showToast("Suggestion applied! Ready to generate SRS.", "success");
}

window.generateSRSWithSelected = function () {
    // Ensure selectedSuggestionText is derived from the currently selected radio,
    // in case the page was cached and the default auto-select didn't run.
    const container = document.getElementById("grammar-suggestions");
    if (container) {
        const selectedRadio = container.querySelector('input[name="grammar-suggestion"]:checked');
        if (selectedRadio) {
            const index = parseInt(selectedRadio.value, 10);
            const suggestionItems = container.querySelectorAll(".suggestion-item");
            if (suggestionItems[index]) {
                const textMatch = suggestionItems[index].querySelector(".suggestion-text");
                if (textMatch) selectedSuggestionText = textMatch.textContent;
            }
        }
    }
    if (!selectedSuggestionText || typeof selectedSuggestionText !== "string") {
        showToast("Please select a suggestion first", "error");
        return;
    }
    
    // Close the modal
    closeGrammarModal();
    
    // Set up the payload with the selected suggestion
    const templateName = document.getElementById("template-select").value;
    const payload = { 
        template_name: templateName,
        input_text: selectedSuggestionText
    };
    
    // Trigger SRS generation directly
    generateSRSWithPayload(payload);
}

window.closeGrammarModal = function () {
    document.getElementById("grammar-modal").classList.add("hidden");
    currentGrammarText = "";
    selectedSuggestionText = "";
    document.getElementById("grammar-suggestions").innerHTML = "";
    hideElement("grammar-error");
}

// Init
document.addEventListener("DOMContentLoaded", checkAuth);
