const tg = window.Telegram.WebApp;
tg.expand();  
tg.ready();   

function openTab(tabId, event) {
    let pages = document.querySelectorAll('.page');
    pages.forEach(page => page.classList.remove('active'));

    let links = document.querySelectorAll('.tab-link');
    links.forEach(link => link.classList.remove('active'));

    document.getElementById(tabId).classList.add('active');
    if (event) {
        event.target.classList.add('active');
    }
}

const darkBtn = document.getElementById('dark-btn');
darkBtn.addEventListener('click', function() {
    document.body.classList.toggle('dark');
    if (document.body.classList.contains('dark')) {
        darkBtn.innerHTML = '<i class="fas fa-sun"></i> الوضع المضيء';
    } else {
        darkBtn.innerHTML = '<i class="fas fa-moon"></i> الوضع المظلم';
    }
});

const subjectsTemplate = [
    { id: "itgs111", code: "ITGS111", name: "مقدمة في تقنية المعلومات", image: "images/itgs111.png", description: "", pdf: "itgs111.pdf" },
    { id: "itgs113", code: "ITGS113", name: "الحلول التقنية", image: "images/itgs113.png", description: "", pdf: "" },
    { id: "itgs215", code: "ITGS215", name: "مقدمة في هندسة الشبكات", image: "images/itgs215.png", description: "", pdf: "" },
    { id: "itgs213", code: "ITGS213", name: "مقدمة في هندسة البرمجيات", image: "images/itgs213.png", description: "", pdf: "" },
    { id: "itgs126", code: "ITGS126", name: "تصميم الدوائر المنطقية", image: "images/itgs126.png", description: "", pdf: "" },
    { id: "itgs122", code: "ITGS122", name: "مقدمة في البرمجة", image: "images/itgs122.png", description: "", pdf: "" },
    { id: "itgs226", code: "ITGS226", name: "مقدمة في برمجة الانترنت", image: "images/itgs226.png", description: "", pdf: "" },
    { id: "itmm122", code: "ITMM122", name: "رياضة 2", image: "images/itmm122.png", description: "", pdf: "" },
    { id: "itgs217", code: "ITGS217", name: "تراكيب منفصلة", image: "images/itgs217.png", description: "", pdf: "" },
    { id: "itel121", code: "ITEL121", name: "لغة إنجليزية 2", image: "images/itel121.png", description: "", pdf: "" },
    { id: "itgs304", code: "ITGS304", name: "كتابة التقارير العلمية", image: "images/itgs304.png", description: "", pdf: "" },
    { id: "itar121", code: "ITAR121", name: "لغة عربية 2", image: "images/itar121.png", description: "", pdf: "" },
    { id: "itgs223", code: "ITGS223", name: "معمارية الحاسوب", image: "images/itgs223.png", description: "", pdf: "" },
    { id: "itgs220", code: "ITGS220", name: "تراكيب البيانات", image: "images/itgs220.png", description: "", pdf: "" },
    { id: "itgs242", code: "ITGS242", name: "مقدمة في علم البيانات", image: "images/itgs242.png", description: "", pdf: "" },
    { id: "itgs211", code: "ITGS211", name: "البرمجة الشيئية", image: "images/itgs211.png", description: "", pdf: "" },
    { id: "itgs219", code: "ITGS219", name: "التحليل العددي", image: "images/itgs219.png", description: "", pdf: "" },
    { id: "itgs228", code: "ITGS228", name: "مقدمة في قواعد البيانات", image: "images/itgs228.png", description: "", pdf: "" },
    { id: "itgs240", code: "ITGS240", name: "مقدمة في الذكاء الاصطناعي", image: "images/itgs240.png", description: "", pdf: "" },
    { id: "itgs224", code: "ITGS224", name: "أمن المعلومات", image: "images/itgs224.png", description: "", pdf: "" },
    { id: "itgs303", code: "ITGS303", name: "إدارة المشاريع", image: "images/itgs303.png", description: "", pdf: "" },
    { id: "itgs302", code: "ITGS302", name: "نظم التشغيل", image: "images/itgs302.png", description: "", pdf: "" },
    { id: "itgs301", code: "ITGS301", name: "تصميم وتحليل الخوارزميات", image: "images/itgs301.png", description: "", pdf: "" }
];

function renderSubjectsGrid() {
    const grid = document.getElementById('subjects-grid');
    if (!grid) return;

    grid.innerHTML = '';
    subjectsTemplate.forEach(subject => {
        const card = document.createElement('div');
        card.className = 'subject-card';
        card.onclick = () => openSubjectModal(subject.id);
        card.innerHTML = `
            <img src="${subject.image}" alt="${subject.name}">
            <div class="subject-card-title">
                <span class="subject-code">${subject.code}</span>
                ${subject.name}
            </div>
        `;
        grid.appendChild(card);
    });
}

function openSubjectModal(id) {
    const subject = subjectsTemplate.find(s => s.id === id);
    if (!subject) return;

    document.getElementById('modal-image').src = subject.image;
    document.getElementById('modal-image').alt = subject.name;
    document.getElementById('modal-title').textContent = `${subject.name} (${subject.code})`;

    const descEl = document.getElementById('modal-description');
    descEl.textContent = subject.description || "لم تتم إضافة شرح لهذه المادة بعد.";

    const pdfArea = document.getElementById('modal-pdf-area');
    if (subject.pdf) {
        pdfArea.innerHTML = `
            <iframe src="${subject.pdf}" class="pdf-frame"></iframe>
            <a href="${subject.pdf}" target="_blank" class="pdf-open-link"><i class="fas fa-file-pdf"></i> فتح ملف PDF في نافذة جديدة</a>
        `;
    } else {
        pdfArea.innerHTML = `<p class="modal-pdf-empty"><i class="fas fa-file-pdf"></i> لم تتم إضافة ملف PDF لهذه المادة بعد.</p>`;
    }

    document.getElementById('subject-modal').classList.add('open');
}

function closeSubjectModal() {
    document.getElementById('subject-modal').classList.remove('open');
}

document.getElementById('modal-close').addEventListener('click', closeSubjectModal);

document.getElementById('subject-modal').addEventListener('click', (e) => {
    if (e.target.id === 'subject-modal') {
        closeSubjectModal();
    }
});

document.addEventListener('DOMContentLoaded', () => {
    renderSubjectsGrid();
});
