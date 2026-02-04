// State Management
let currentStep = 1;
const totalSteps = 3;

// Navigation Logic
function nextStep(target) {
    if (target > totalSteps) return;

    // Hide current
    document.getElementById(`step${currentStep}`).classList.remove('active');
    document.querySelector(`.step[data-step="${currentStep}"]`).classList.remove('active');
    document.querySelector(`.step[data-step="${currentStep}"]`).classList.add('completed');

    // Show next
    currentStep = target;
    document.getElementById(`step${currentStep}`).classList.add('active');
    document.querySelector(`.step[data-step="${currentStep}"]`).classList.add('active');

    // Update Title
    const titles = ["", "بيانات الأطراف", "بيانات القرار والتظلم", "موضوع الدعوى"];
    document.getElementById('step-title').innerText = titles[currentStep];
}

function prevStep(target) {
    if (target < 1) return;

    document.getElementById(`step${currentStep}`).classList.remove('active');
    document.querySelector(`.step[data-step="${currentStep}"]`).classList.remove('active');

    currentStep = target;
    document.getElementById(`step${currentStep}`).classList.add('active');
    document.querySelector(`.step[data-step="${currentStep}"]`).classList.add('active');

    // Update Title
    const titles = ["", "بيانات الأطراف", "بيانات القرار والتظلم", "موضوع الدعوى"];
    document.getElementById('step-title').innerText = titles[currentStep];
}

function startWizard() {
    document.getElementById('hero').classList.add('hidden');
    document.getElementById('hero').classList.remove('active-section');

    document.getElementById('wizard').classList.remove('hidden');
}

function toggleGrievance(show) {
    const section = document.getElementById('grievance-fields');
    if (show) {
        section.style.display = 'block';
    } else {
        section.style.display = 'none';
    }
}

// API Interaction
async function submitCase() {
    // 1. Collect Data
    const form = document.getElementById('caseForm');
    const formData = new FormData(form);

    // Construct Description from fields for AI context
    const fullDescription = `
    موضوع الدعوى: ${formData.get('description')}
    
    بيانات القرار:
    رقم القرار: ${formData.get('decision_number')}
    تاريخ القرار: ${formData.get('decision_date')}
    تاريخ العلم: ${formData.get('incident_date')}
    
    بيانات التظلم:
    هل يوجد تظلم؟: ${formData.get('has_grievance')}
    رقم التظلم: ${formData.get('grievance_number')}
    تاريخ التظلم: ${formData.get('grievance_date')}
    نتيجة التظلم: ${formData.get('grievance_outcome')}
    `.trim();

    const payload = {
        title: "دعوى إدارية - " + (formData.get('decision_number') || "جديدة"),
        description: fullDescription,
        incident_date: formData.get('incident_date'), // Mapped
        grievance_date: formData.get('grievance_date') || null,
        court_type: "Administrative",
        request_type: formData.get('request_type'),
        plaintiff: {
            name: formData.get('plaintiff_name'),
            party_type: formData.get('plaintiff_type'),
            role: "PLAINTIFF"
        },
        defendant: {
            name: formData.get('defendant_name'), // Now "Decision Issuer"
            party_type: "GOVERNMENT",
            role: "DEFENDANT"
        }
    };

    // Append JSON as string
    const finalFormData = new FormData();
    finalFormData.append('data', JSON.stringify(payload)); // Send JSON data as a field

    // Append Files
    const fileInput = document.querySelector('input[name="documents"]');
    if (fileInput.files.length > 0) {
        for (let i = 0; i < fileInput.files.length; i++) {
            finalFormData.append('documents', fileInput.files[i]);
        }
    }

    // 2. Show Loading
    document.getElementById('wizard').classList.add('hidden');
    document.getElementById('loading').classList.remove('hidden');

    try {
        // 3. Call API
        const response = await fetch('/api/cases/submit_and_validate/', {
            method: 'POST',
            // headers: { 'Content-Type': 'multipart/form-data' }, // Let browser set boundary
            body: finalFormData
        });

        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.error || JSON.stringify(result));
        }

        // 4. Redirect to Success Page
        window.location.href = "/success/";

    } catch (error) {
        console.error("Submission Error:", error);
        alert(`عذراً، حدث خطأ أثناء تقديم الطلب:\n${error.message}`);
        document.getElementById('wizard').classList.remove('hidden');
        document.getElementById('loading').classList.add('hidden');
    }
}

function renderDashboard(data) {
    document.getElementById('loading').classList.add('hidden');
    document.getElementById('dashboard').classList.remove('hidden');

    // Status
    const statusDiv = document.getElementById('final-status');
    if (data.status === "ACCEPTED") {
        statusDiv.innerText = "الدعوى مقبولة شكلاً ✅";
        statusDiv.className = "status-badge status-accepted";
        document.getElementById('next-action-title').innerText = "يمكنك قيد الدعوى رسمياً عبر منصة معين.";
    } else {
        statusDiv.innerText = "الدعوى غير مقبولة ❌";
        statusDiv.className = "status-badge status-rejected";
        document.getElementById('next-action-title').innerText = "يجب عليك معالجة الملاحظات الإجرائية قبل القيد.";
    }

    // AI Reasoning
    const aiDiv = document.getElementById('ai-reasoning-body');
    const reasoningText = data.ai_insight.generated_reasoning || "لا يوجد تسبيب متاح.";
    aiDiv.innerHTML = `<p style="line-height: 1.8; color: #e2e8f0;">${reasoningText}</p>`;

    // Validation Steps
    const list = document.getElementById('validation-list');
    list.innerHTML = "";

    // If rejected, show reasons
    if (data.validation_details && data.validation_details.length > 0) {
        data.validation_details.forEach(reason => {
            const li = document.createElement('li');
            li.innerHTML = `<i class="fa-solid fa-circle-xmark" style="color: #f87171;"></i> ${reason.message}`;
            li.style = "padding: 10px 0; display: flex; align-items: center; gap: 10px;";
            list.appendChild(li);
        });
    } else {
        list.innerHTML = `
            <li style="padding: 10px 0; display: flex; align-items: center; gap: 10px;">
                <i class="fa-solid fa-check-circle" style="color: #34d399;"></i> التحقق من اختصاص المحكمة
            </li>
            <li style="padding: 10px 0; display: flex; align-items: center; gap: 10px;">
                <i class="fa-solid fa-check-circle" style="color: #34d399;"></i> التحقق من صحة التظلم
            </li>
             <li style="padding: 10px 0; display: flex; align-items: center; gap: 10px;">
                <i class="fa-solid fa-check-circle" style="color: #34d399;"></i> احتساب مدد التقادم (60 يوم)
            </li>
         `;
    }
}
