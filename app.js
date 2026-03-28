document.addEventListener("DOMContentLoaded", () => {
    const uploadForm = document.getElementById("upload-form");
    const fileInput = document.getElementById("pdf-file");
    const langSelect = document.getElementById("lang-select");
    const resultsDiv = document.getElementById("results");
    const summarizeBtn = document.getElementById("summarize-btn");
    const btnText = document.getElementById("btn-text");
    const spinner = document.getElementById("spinner");
    const fileNameDisplay = document.getElementById("file-name-display");

    fileInput.addEventListener("change", () => {
        if (fileInput.files.length > 0) {
            fileNameDisplay.textContent = fileInput.files[0].name;
        } else {
            fileNameDisplay.textContent = "No file selected";
        }
    });

    uploadForm.addEventListener("submit", async (e) => {
        e.preventDefault();

        const file = fileInput.files[0];
        if (!file) {
            alert("Please select a PDF file to upload.");
            return;
        }

        btnText.textContent = "Processing...";
        spinner.style.display = "inline-block";
        summarizeBtn.disabled = true;
        resultsDiv.style.display = "none";
        resultsDiv.classList.remove("visible");
        resultsDiv.innerHTML = "";

        const formData = new FormData();
        formData.append("file", file);
        formData.append("lang", langSelect.value);

        try {
            const response = await fetch("http://127.0.0.1:8000/upload", {
                method: "POST",
                body: formData,
            });

            if (!response.ok) {
                const err = await response.json();
                throw new Error(err.detail || "Something went wrong on the server.");
            }

            const data = await response.json();
            const selectedLangText = langSelect.options[langSelect.selectedIndex].text;

            let html = `
                <h3 class="mb-3">Your Simplified Summary</h3>
                <div class="summary-card">
                    <h5>Summary (${selectedLangText})</h5>
                    <p>${data.summary.replace(/\n/g, '<br>')}</p>
                </div>
            `;

            resultsDiv.innerHTML = html;
            resultsDiv.style.display = "block";
            setTimeout(() => {
                resultsDiv.classList.add("visible");
            }, 10);

        } catch (error) {
            resultsDiv.innerHTML = `
                <div class="alert alert-danger">
                    <strong>Error:</strong> ${error.message}
                </div>
            `;
            resultsDiv.style.display = "block";
            setTimeout(() => {
                resultsDiv.classList.add("visible");
            }, 10);
        } finally {
            btnText.textContent = "Summarize Report";
            spinner.style.display = "none";
            summarizeBtn.disabled = false;
        }
    });
});