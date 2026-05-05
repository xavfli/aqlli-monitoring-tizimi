const messageBox = document.getElementById("messageBox");
const statusBadge = document.getElementById("statusBadge");
const videoFeed = document.getElementById("videoFeed");
let videoLoop = null;

function reconnectVideo() {
    if (!videoFeed) {
        return;
    }
    videoFeed.src = `/video_frame?t=${Date.now()}`;
}

function startVideoLoop() {
    if (videoLoop) {
        clearInterval(videoLoop);
    }
    videoLoop = setInterval(() => {
        reconnectVideo();
    }, 220);
}

if (videoFeed) {
    videoFeed.addEventListener("error", () => {
        setTimeout(reconnectVideo, 600);
    });
}

function setMessage(text, isError = false) {
    if (!messageBox) {
        return;
    }
    messageBox.textContent = text;
    messageBox.style.color = isError ? "#ffd8d2" : "#edf4f7";
}

function setBadge(running) {
    if (!statusBadge) {
        return;
    }
    statusBadge.textContent = running ? "Monitoring faol" : "Tizim kutish holatida";
    statusBadge.className = running ? "badge badge-live" : "badge badge-idle";
}

function setTextIfPresent(id, value) {
    const element = document.getElementById(id);
    if (element) {
        element.textContent = value;
    }
}

function getElementValue(id, fallback = "") {
    const element = document.getElementById(id);
    if (!element) {
        return fallback;
    }
    if ("value" in element) {
        return element.value;
    }
    return element.dataset.value || element.textContent || fallback;
}

function updateStatus(status) {
    setTextIfPresent("currentScore", status.average_score);
    setTextIfPresent("heroCurrentScore", status.average_score);
    setTextIfPresent("detectedFaces", status.max_detected_faces ?? 0);
    setTextIfPresent("presenceRatio", `${status.presence_ratio}%`);
    setTextIfPresent("attentionRatio", `${status.attention_ratio}%`);
    setTextIfPresent("movementRatio", `${status.movement_ratio}%`);
    setTextIfPresent("totalFrames", status.total_frames);
    setTextIfPresent("faceFrames", status.face_frames);
    setTextIfPresent("avgFaces", status.average_detected_faces ?? 0);
    setTextIfPresent("maxScore", status.max_score);
    setTextIfPresent("lastError", status.last_error || "Yo'q");
    setTextIfPresent("backendName", status.active_backend || "none");
    setTextIfPresent("activeCamera", status.active_camera_index);
    setTextIfPresent("activeSource", status.active_source_label || "webcam:auto");
    setTextIfPresent("phoneSuspects", status.event_totals?.phone_suspect ?? 0);
    setTextIfPresent("questionGestures", status.event_totals?.question_gesture ?? 0);
    setTextIfPresent("drowsySuspects", status.event_totals?.drowsy_suspect ?? 0);
    setTextIfPresent("lookingAway", status.event_totals?.looking_away ?? 0);
    updateParticipants(status.participant_summary || []);
    if (status.last_attempts?.length && !status.running) {
        setMessage(`Kamera topilmadi. Sinab ko'rilganlar: ${status.last_attempts.join(", ")}`, true);
    }
    setBadge(status.running);
}

function updateSummary(summary) {
    setTextIfPresent("summarySessions", summary.total_sessions);
    setTextIfPresent("summaryMeanScore", Number(summary.mean_score || 0).toFixed(1));
    setTextIfPresent("summaryPresence", `${Number(summary.mean_presence || 0).toFixed(1)}%`);
    setTextIfPresent("summaryBest", Number(summary.best_score || 0).toFixed(1));
}

function updateSessions(sessions) {
    const table = document.getElementById("sessionTable");
    if (!table) {
        return;
    }
    if (!sessions.length) {
        table.innerHTML = `<tr><td colspan="7">Hozircha sessiyalar mavjud emas.</td></tr>`;
        return;
    }
    table.innerHTML = sessions.map((session) => `
        <tr>
            <td>${session.id}</td>
            <td>${session.session_name}</td>
            <td>${session.started_at}</td>
            <td>${session.ended_at}</td>
            <td>${session.presence_ratio}%</td>
            <td>${session.average_score}</td>
            <td>${session.max_score}</td>
        </tr>
    `).join("");
}

function updateParticipants(participants) {
    const participantList = document.getElementById("participantList");
    if (!participantList) {
        return;
    }
    if (!participants?.length) {
        participantList.innerHTML = `<div class="participant-empty">Hozircha anonim trek statistikasi yo'q.</div>`;
        return;
    }
    participantList.innerHTML = participants.map((participant) => `
        <div class="participant-card">
            <div class="participant-title">${participant.display_name || participant.participant_id}</div>
            <div class="participant-meta">Track: <strong>${participant.participant_id}</strong></div>
            <div class="participant-meta">O'rtacha ball: <strong>${participant.average_score}</strong></div>
            <div class="participant-meta">Maksimal ball: <strong>${participant.max_score}</strong></div>
            <div class="participant-meta">Kadrlar ulushi: <strong>${participant.presence_ratio}%</strong></div>
            <div class="participant-meta">Telefon ehtimoli: <strong>${participant.event_counts?.phone_suspect ?? 0}</strong></div>
            <div class="participant-meta">Savol/qo'l ishorasi: <strong>${participant.event_counts?.question_gesture ?? 0}</strong></div>
            <div class="participant-meta">Uyquchanlik ehtimoli: <strong>${participant.event_counts?.drowsy_suspect ?? 0}</strong></div>
            <div class="participant-meta">Chalg'ish holati: <strong>${participant.event_counts?.looking_away ?? 0}</strong></div>
        </div>
    `).join("");
}

function updateStudentResults(studentResults) {
    const container = document.getElementById("studentResults");
    if (!container) {
        return;
    }
    if (!studentResults?.length) {
        container.innerHTML = `<div class="participant-empty">Hozircha talabalar bo'yicha oxirgi ball saqlanmagan.</div>`;
        return;
    }
    container.innerHTML = studentResults.map((student) => `
        <div class="participant-card">
            <div class="participant-title">${student.student_name}</div>
            <div class="participant-meta">Oxirgi ball: <strong>${student.average_score}</strong></div>
            <div class="participant-meta">Maksimal ball: <strong>${student.max_score}</strong></div>
            <div class="participant-meta">Mavjudlik: <strong>${student.presence_ratio}%</strong></div>
            <div class="participant-meta">Track: <strong>${student.participant_id}</strong></div>
        </div>
    `).join("");
}

function updateStudentRoster(studentRoster) {
    const container = document.getElementById("studentRoster");
    const table = document.getElementById("studentRosterTable");
    const select = document.getElementById("assignStudentName");
    if (select) {
        const currentValue = select.value;
        select.innerHTML = `<option value="">Ro'yxatdan tanlang</option>` + (studentRoster || []).map((student) => `
            <option value="${student.student_name}">${student.student_name}${student.group_name ? ` - ${student.group_name}` : ""}</option>
        `).join("");
        if (currentValue) {
            select.value = currentValue;
        }
    }
    if (table) {
        if (!studentRoster?.length) {
            table.innerHTML = `<tr><td colspan="4">Talabalar bazasi hozircha bo'sh.</td></tr>`;
        } else {
            table.innerHTML = studentRoster.map((student) => `
                <tr>
                    <td>${student.id}</td>
                    <td>${student.student_name}</td>
                    <td>${student.group_name || "Ko'rsatilmagan"}</td>
                    <td>${student.notes || ""}</td>
                </tr>
            `).join("");
        }
    }
    if (!container) {
        return;
    }
    if (!studentRoster?.length) {
        container.innerHTML = `<div class="participant-empty">Hozircha talabalar ro'yxati bo'sh.</div>`;
        return;
    }
    container.innerHTML = studentRoster.map((student) => `
        <div class="participant-card">
            <div class="participant-title">${student.student_name}</div>
            <div class="participant-meta">Guruh: <strong>${student.group_name || "Ko'rsatilmagan"}</strong></div>
        </div>
    `).join("");
}

async function postJson(url, payload) {
    const response = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload || {}),
    });
    return response.json();
}

const startBtn = document.getElementById("startBtn");
if (startBtn) {
    startBtn.addEventListener("click", async () => {
        const sessionName = getElementValue("sessionName", "Amaliy dars sessiyasi").trim();
        const cameraIndex = Number(getElementValue("cameraIndex", "-1") || -1);
        const cameraSource = getElementValue("cameraSource", "").trim();
        setMessage("Kamera ulanmoqda, bir necha soniya kuting...");
        const data = await postJson("/api/monitor/start", {
            session_name: sessionName,
            camera_index: cameraIndex,
            camera_source: cameraSource,
        });
        setMessage(data.message, !data.ok);
        if (data.status) {
            updateStatus(data.status);
        }
        reconnectVideo();
    });
}

const stopBtn = document.getElementById("stopBtn");
if (stopBtn) {
    stopBtn.addEventListener("click", async () => {
        const data = await postJson("/api/monitor/stop");
        setMessage(data.message, !data.ok);
        if (data.status) {
            updateStatus(data.status);
        }
        if (data.summary) {
            updateSummary(data.summary);
        }
        if (data.sessions) {
            updateSessions(data.sessions);
        }
        if (data.student_results) {
            updateStudentResults(data.student_results);
        }
        reconnectVideo();
    });
}

const resetBtn = document.getElementById("resetBtn");
if (resetBtn) {
    resetBtn.addEventListener("click", async () => {
        const sessionName = getElementValue("sessionName", "Amaliy dars sessiyasi").trim();
        const data = await postJson("/api/monitor/reset", { session_name: sessionName });
        setMessage(data.message, !data.ok);
        if (data.status) {
            updateStatus(data.status);
        }
        reconnectVideo();
    });
}

async function refreshDashboard() {
    const response = await fetch("/api/stats/current");
    const data = await response.json();
    updateStatus(data.status);
    updateSummary(data.summary);
    updateSessions(data.sessions);
    updateStudentResults(data.student_results);
    updateStudentRoster(data.student_roster);
}

const assignBtn = document.getElementById("assignBtn");
if (assignBtn) {
    assignBtn.addEventListener("click", async () => {
        const participantId = document.getElementById("assignParticipantId").value.trim();
        const studentName = document.getElementById("assignStudentName").value.trim();
        if (!participantId || !studentName) {
            setMessage("Track va talaba nomini to'ldiring", true);
            return;
        }
        const data = await postJson("/api/participants/assign", {
            participant_id: participantId,
            student_name: studentName,
        });
        setMessage(data.message, !data.ok);
        if (data.status) {
            updateStatus(data.status);
        }
    });
}

const addStudentBtn = document.getElementById("addStudentBtn");
if (addStudentBtn) {
    addStudentBtn.addEventListener("click", async () => {
        const studentName = document.getElementById("newStudentName").value.trim();
        const groupName = document.getElementById("newStudentGroup").value.trim();
        if (!studentName) {
            setMessage("Talaba nomini kiriting", true);
            return;
        }
        const data = await postJson("/api/students", {
            student_name: studentName,
            group_name: groupName,
        });
        setMessage(data.message, !data.ok);
        if (data.student_roster) {
            updateStudentRoster(data.student_roster);
        }
        if (data.ok) {
            document.getElementById("newStudentName").value = "";
            document.getElementById("newStudentGroup").value = "";
            document.getElementById("assignStudentName").value = studentName;
        }
    });
}

const saveCameraBtn = document.getElementById("saveCameraBtn");
if (saveCameraBtn) {
    saveCameraBtn.addEventListener("click", async () => {
        const roomName = document.getElementById("adminRoomName").value.trim();
        const cameraIndex = Number(document.getElementById("adminCameraIndex").value || -1);
        const cameraSource = document.getElementById("adminCameraSource").value.trim();
        const notes = document.getElementById("adminCameraNotes").value.trim();
        if (!roomName) {
            setMessage("Xona nomini kiriting", true);
            return;
        }
        setMessage("Kamera sozlamalari saqlanmoqda...");
        const data = await postJson("/api/admin/camera", {
            room_name: roomName,
            camera_index: cameraIndex,
            camera_source: cameraSource,
            notes,
        });
        setMessage(data.message, !data.ok);
    });
}

const defaultCameraPreset = document.getElementById("defaultCameraPreset");
if (defaultCameraPreset) {
    defaultCameraPreset.addEventListener("change", () => {
        if (!defaultCameraPreset.value) {
            return;
        }
        const preset = JSON.parse(defaultCameraPreset.value);
        document.getElementById("adminRoomName").value = preset.room || "E 102 xona";
        document.getElementById("adminCameraIndex").value = preset.index ?? -1;
        document.getElementById("adminCameraSource").value = preset.source || "";
        document.getElementById("adminCameraNotes").value = preset.notes || "";
        setMessage("Default kamera tanlandi. Saqlash uchun pastdagi tugmani bosing.");
    });
}

setInterval(refreshDashboard, 3000);
reconnectVideo();
if (videoFeed) {
    startVideoLoop();
}
