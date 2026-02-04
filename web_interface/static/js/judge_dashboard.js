
async function approveCase(caseId) {
    if (!confirm('هل أنت متأكد من اعتماد هذه القضية؟')) return;

    try {
        const response = await fetch(`/api/cases/${caseId}/approve_case/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'Content-Type': 'application/json'
            }
        });

        if (response.ok) {
            alert('تم اعتماد القضية بنجاح');
            location.reload();
        } else {
            alert('حدث خطأ أثناء الاعتماد');
        }
    } catch (error) {
        console.error(error);
        alert('فشل الاتصال بالخادم');
    }
}

async function rejectCase(caseId) {
    const reason = prompt('الرجاء إدخال سبب الرفض:');
    if (reason === null) return; // Cancelled

    try {
        const response = await fetch(`/api/cases/${caseId}/reject_case/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ reason: reason })
        });

        if (response.ok) {
            alert('تم رفض القضية');
            location.reload();
        } else {
            alert('حدث خطأ أثناء الرفض');
        }
    } catch (error) {
        console.error(error);
        alert('فشل الاتصال بالخادم');
    }
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
