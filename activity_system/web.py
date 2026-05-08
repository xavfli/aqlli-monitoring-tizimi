import os

from flask import Flask, Response, jsonify, redirect, render_template, request, send_file, session, url_for

from .config import BASE_DIR
from .database import (
    add_student_roster,
    delete_session,
    export_sessions_csv,
    fetch_camera_settings,
    fetch_recent_sessions,
    fetch_session_by_id,
    fetch_session_participant_results,
    fetch_student_latest_results,
    fetch_student_roster,
    fetch_summary,
    init_db,
    save_camera_settings,
)
from .monitor import ActivityMonitor


monitor = ActivityMonitor()


def create_app() -> Flask:
    app = Flask(
        __name__,
        template_folder=str(BASE_DIR / "templates"),
        static_folder=str(BASE_DIR / "static"),
    )
    app.secret_key = os.getenv("SECRET_KEY", "dars-monitoring-admin-key")
    init_db()

    @app.route("/")
    def index():
        return render_template(
            "index.html",
            summary=fetch_summary(),
            sessions=fetch_recent_sessions(),
            student_results=fetch_student_latest_results(),
            student_roster=fetch_student_roster(),
            camera_settings=fetch_camera_settings(),
            status=monitor.get_status(),
        )

    @app.route("/events")
    def events_page():
        return render_template(
            "events.html",
            summary=fetch_summary(),
            sessions=fetch_recent_sessions(),
            student_results=fetch_student_latest_results(),
            student_roster=fetch_student_roster(),
            camera_settings=fetch_camera_settings(),
            status=monitor.get_status(),
        )

    @app.route("/results")
    def results_page():
        sessions = fetch_recent_sessions(limit=100)
        requested_id = request.args.get("session_id", type=int)
        selected_session = None
        if requested_id:
            selected_session = fetch_session_by_id(requested_id)
        if selected_session is None and sessions:
            selected_session = sessions[0]
        participant_results = (
            fetch_session_participant_results(int(selected_session["id"]))
            if selected_session
            else []
        )
        return render_template(
            "results.html",
            sessions=sessions,
            selected_session=selected_session,
            participant_results=participant_results,
            summary=fetch_summary(),
        )

    @app.post("/results/delete/<int:session_id>")
    def delete_results_session(session_id: int):
        delete_session(session_id)
        return redirect(url_for("results_page"))

    @app.route("/admin")
    def admin_page():
        if not session.get("admin_logged_in"):
            return redirect(url_for("admin_login"))
        return render_template(
            "admin.html",
            camera_settings=fetch_camera_settings(),
            status=monitor.get_status(),
        )

    @app.route("/admin/login", methods=["GET", "POST"])
    def admin_login():
        error = ""
        if request.method == "POST":
            password = (request.form.get("password") or "").strip()
            expected_password = os.getenv("ADMIN_PASSWORD", "admin123")
            if password == expected_password:
                session["admin_logged_in"] = True
                return redirect(url_for("admin_page"))
            error = "Parol noto'g'ri. Qayta urinib ko'ring."
        return render_template("admin_login.html", error=error)

    @app.route("/admin/logout")
    def admin_logout():
        session.pop("admin_logged_in", None)
        return redirect(url_for("admin_login"))

    @app.route("/video_feed")
    def video_feed():
        return Response(
            monitor.generate_mjpeg(),
            mimetype="multipart/x-mixed-replace; boundary=frame",
        )

    @app.get("/video_frame")
    def video_frame():
        try:
            frame = monitor.get_frame_bytes()
            return Response(frame, mimetype="image/jpeg")
        except Exception as exc:
            return jsonify({"ok": False, "message": str(exc)}), 500

    @app.post("/api/monitor/start")
    def start_monitor():
        payload = request.get_json(silent=True) or {}
        session_name = payload.get("session_name") or "Amaliy dars sessiyasi"
        camera_index = int(payload.get("camera_index", 0))
        camera_source = payload.get("camera_source") or ""
        if not camera_source and camera_index == -1:
            settings = fetch_camera_settings()
            camera_index = int(settings.get("camera_index", -1))
            camera_source = settings.get("camera_source") or ""
        try:
            monitor.start(
                camera_index=camera_index,
                session_name=session_name,
                camera_source=camera_source,
            )
        except RuntimeError as exc:
            return jsonify({"ok": False, "message": str(exc), "status": monitor.get_status()}), 400
        return jsonify({"ok": True, "message": "Monitoring boshlandi", "status": monitor.get_status()})

    @app.post("/api/monitor/stop")
    def stop_monitor():
        saved_payload = monitor.stop(save=True)
        return jsonify(
            {
                "ok": True,
                "message": "Monitoring to'xtatildi va sessiya saqlandi",
                "saved": saved_payload,
                "results_url": url_for(
                    "results_page",
                    session_id=saved_payload.get("saved_session_id"),
                )
                if saved_payload and saved_payload.get("saved_session_id")
                else url_for("results_page"),
                "summary": fetch_summary(),
                "sessions": fetch_recent_sessions(),
                "student_results": fetch_student_latest_results(),
                "status": monitor.get_status(),
            }
        )

    @app.post("/api/admin/camera")
    def admin_camera_settings():
        if not session.get("admin_logged_in"):
            return jsonify({"ok": False, "message": "Avval admin sifatida kiring"}), 401
        payload = request.get_json(silent=True) or {}
        room_name = (payload.get("room_name") or "").strip()
        camera_source = (payload.get("camera_source") or "").strip()
        zoom_link = (payload.get("zoom_link") or "").strip()
        zoom_meeting_id = (payload.get("zoom_meeting_id") or "").strip()
        zoom_passcode = (payload.get("zoom_passcode") or "").strip()
        notes = (payload.get("notes") or "").strip()
        try:
            camera_index = int(payload.get("camera_index", -1))
        except (TypeError, ValueError):
            return jsonify({"ok": False, "message": "Virtual kamera indeksi raqam bo'lishi kerak"}), 400
        settings = save_camera_settings(
            room_name=room_name,
            camera_index=camera_index,
            camera_source=camera_source,
            zoom_link=zoom_link,
            zoom_meeting_id=zoom_meeting_id,
            zoom_passcode=zoom_passcode,
            notes=notes,
        )
        return jsonify(
            {
                "ok": True,
                "message": "Zoom manbasi saqlandi",
                "camera_settings": settings,
            }
        )

    @app.post("/api/monitor/reset")
    def reset_monitor():
        payload = request.get_json(silent=True) or {}
        monitor.reset(session_name=payload.get("session_name"))
        return jsonify({"ok": True, "message": "Joriy statistika tozalandi", "status": monitor.get_status()})

    @app.post("/api/participants/assign")
    def assign_participant():
        payload = request.get_json(silent=True) or {}
        participant_id = (payload.get("participant_id") or "").strip()
        student_name = (payload.get("student_name") or "").strip()
        if not participant_id or not student_name:
            return jsonify({"ok": False, "message": "Track va talaba nomi kiritilishi kerak"}), 400
        try:
            status = monitor.assign_participant_name(participant_id, student_name)
        except KeyError as exc:
            return jsonify({"ok": False, "message": str(exc)}), 404
        return jsonify({"ok": True, "message": "Track talaba nomiga biriktirildi", "status": status})

    @app.post("/api/students")
    def add_student():
        if not session.get("admin_logged_in"):
            return jsonify({"ok": False, "message": "Talabalar bazasini o'zgartirish uchun admin sifatida kiring"}), 401
        payload = request.get_json(silent=True) or {}
        student_name = (payload.get("student_name") or "").strip()
        group_name = (payload.get("group_name") or "").strip()
        notes = (payload.get("notes") or "").strip()
        if not student_name:
            return jsonify({"ok": False, "message": "Talaba nomi kiritilishi kerak"}), 400
        row = add_student_roster(student_name=student_name, group_name=group_name, notes=notes)
        return jsonify(
            {
                "ok": True,
                "message": "Talaba ro'yxatga qo'shildi",
                "student": row,
                "student_roster": fetch_student_roster(),
            }
        )

    @app.get("/api/stats/current")
    def current_stats():
        return jsonify(
            {
                "status": monitor.get_status(),
                "summary": fetch_summary(),
                "sessions": fetch_recent_sessions(),
                "student_results": fetch_student_latest_results(),
                "student_roster": fetch_student_roster(),
                "camera_settings": fetch_camera_settings(),
            }
        )

    @app.get("/export/csv")
    def export_csv():
        export_path = export_sessions_csv()
        return send_file(export_path, as_attachment=True)

    return app
