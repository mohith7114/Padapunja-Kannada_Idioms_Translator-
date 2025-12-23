from flask import Blueprint, request, jsonify, session, redirect, url_for, render_template, send_file, current_app
from extensions import db
from models import Idiom, History, Suggestion, Feedback
from utils import get_cached_idioms, refresh_idiom_cache
from datetime import datetime, timedelta
from googletrans import Translator
from fuzzywuzzy import fuzz
from functools import wraps
from gtts import gTTS
import speech_recognition as sr
from pydub import AudioSegment
import smtplib
import random
import io
import os
import csv
import json
import time
import logging
from langdetect import detect, LangDetectException

# Create the Blueprint
main_bp = Blueprint('main', __name__)

# --- Configuration Constants (Loaded from Env) ---
SMTP_SERVER = os.getenv("PAD_SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("PAD_SMTP_PORT", 587))
SENDER_EMAIL = os.getenv("PAD_SENDER_EMAIL")
SENDER_PASSWORD = os.getenv("PAD_SENDER_PASS")
OTP_EXPIRY_SECONDS = 5 * 60
FUZZY_MATCH_CONFIDENCE = 85

# --- Helper Decorator ---
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("admin_logged_in"):
            return redirect(url_for("main.login", next=request.url))
        return f(*args, **kwargs)
    return decorated_function

# =================== AUTH ROUTES ====================

@main_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        if not email:
            return render_template("login.html", error="Enter a valid email")

        otp = f"{random.randint(100000, 999999):06d}"
        session["otp"] = otp
        session["otp_time"] = time.time()
        session["email"] = email

        subject = "Padapunja OTP Login"
        message = f"Subject: {subject}\n\nYour OTP for Padapunja is: {otp}\nThis OTP expires in 5 minutes."

        try:
            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=10)
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, email, message)
            server.quit()
        except Exception as e:
            logging.exception("Failed to send OTP via SMTP")
            return render_template("login.html", error=f"Failed to send OTP. Check server logs.")

        return redirect(url_for("main.verify_otp"))

    return render_template("login.html")

@main_bp.route("/verify", methods=["GET", "POST"])
def verify_otp():
    if request.method == "POST":
        user_otp = (request.form.get("otp") or "").strip()
        otp = session.get("otp")
        t0 = session.get("otp_time", 0)

        if not otp:
            return render_template("verify.html", error="No OTP requested.")

        if time.time() - t0 > OTP_EXPIRY_SECONDS:
            session.pop("otp", None)
            return render_template("verify.html", error="OTP expired.")

        if user_otp == otp:
            session["user_logged_in"] = True
            session.permanent = True
            email = session.get("email")

            # SECURITY FIX: Check env variable instead of hardcoded string
            admin_email = os.getenv("ADMIN_EMAIL", "padapunja@gmail.com")
            if email == admin_email:
                session["admin_logged_in"] = True
            else:
                session["admin_logged_in"] = False

            session.pop("otp", None)
            return redirect(url_for("main.home"))
        else:
            return render_template("verify.html", error="Invalid OTP.")

    return render_template("verify.html")

@main_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("main.login"))

# =================== MAIN APP ROUTES ====================

@main_bp.route("/")
def home():
    if not session.get("user_logged_in"):
        return redirect(url_for("main.login"))
    return render_template("index.html")

@main_bp.route("/translate", methods=["POST"])
def translate():
    data = request.get_json()
    if not data or "sentence" not in data:
        return jsonify({"error": "Invalid request"}), 400

    sentence = data.get("sentence", "").strip()
    if not sentence:
        return jsonify({"error": "Empty sentence"}), 400

    translator = Translator()

    # 1. Literal Translation
    try:
        lang = detect(sentence)
    except LangDetectException:
        lang = "kn"

    try:
        if lang == "kn":
            literal_meaning_en = translator.translate(sentence, src="kn", dest="en").text
        else:
            literal_meaning_en = sentence
    except Exception as e:
        literal_meaning_en = f"Translation failed: {e}"

    # 2. PERFORMANCE FIX: Use Cache
    all_idioms_sorted = get_cached_idioms()

    detected_results = []
    working_sentence_kn = sentence
    status = "no_idiom_detected"
    match_type = "none"

    # 3. Exact Match Pass
    for idiom_obj in all_idioms_sorted:
        idiom_phrase = idiom_obj['idiom'].strip()
        if not idiom_phrase: continue

        if idiom_phrase in working_sentence_kn:
            status = "idiom_detected"
            match_type = "exact_multiple"
            
            # Use .copy() to avoid modifying the global cache
            idiom_dict = idiom_obj.copy()
            kannada_expl = idiom_dict.get("explanation_kannada") or ""

            # Auto-translate missing fields
            if not idiom_dict.get("explanation_english") and kannada_expl:
                try:
                    idiom_dict["explanation_english"] = translator.translate(kannada_expl, src="kn", dest="en").text
                except:
                    idiom_dict["explanation_english"] = "---"
            
            try:
                idiom_phrase_en = translator.translate(idiom_phrase, src="kn", dest="en").text
            except:
                idiom_phrase_en = idiom_phrase

            detected_results.append({
                "result": idiom_dict,
                "idiom_english_translation": idiom_phrase_en,
                "matched_phrase": idiom_phrase
            })
            
            working_sentence_kn = working_sentence_kn.replace(idiom_phrase, kannada_expl)

    # 4. Return Exact Matches
    if status == "idiom_detected":
        try:
            full_sentence_en = translator.translate(working_sentence_kn, src="kn", dest="en").text
        except Exception as e:
            full_sentence_en = f"Error: {e}"

        save_history_entry(sentence, "idiom_detected", "exact_multiple", 
                           ", ".join([r['matched_phrase'] for r in detected_results]), full_sentence_en)

        return jsonify({
            "status": "idiom_detected",
            "match_type": "exact_multiple",
            "literal_meaning_en": literal_meaning_en,
            "results_list": detected_results,
            "full_sentence_kannada": working_sentence_kn,
            "full_sentence_english": full_sentence_en
        })

    # 5. Fuzzy Match Pass (Using Cache)
    best_match_idiom = None
    highest_score = 0
    best_match_phrase = ""
    sentence_tokens = sentence.split()

    for idiom_obj in all_idioms_sorted:
        idiom_phrase = idiom_obj['idiom'].strip()
        idiom_tokens = idiom_phrase.split()
        if not idiom_tokens or len(idiom_tokens) > len(sentence_tokens): continue

        for i in range(len(sentence_tokens) - len(idiom_tokens) + 1):
            window_phrase = " ".join(sentence_tokens[i : i + len(idiom_tokens)])
            score = fuzz.token_sort_ratio(idiom_phrase, window_phrase)
            if score > highest_score:
                highest_score = score
                best_match_idiom = idiom_obj
                best_match_phrase = window_phrase

    if highest_score >= FUZZY_MATCH_CONFIDENCE and best_match_idiom:
        idiom_dict = best_match_idiom.copy()
        kannada_expl = idiom_dict.get("explanation_kannada") or ""
        
        # Translate missing parts
        if not idiom_dict.get("explanation_english") and kannada_expl:
             try: idiom_dict["explanation_english"] = translator.translate(kannada_expl, src="kn", dest="en").text
             except: idiom_dict["explanation_english"] = "---"
        
        full_sentence_kn = sentence.replace(best_match_phrase, kannada_expl)
        try: full_sentence_en = translator.translate(full_sentence_kn, src="kn", dest="en").text
        except: full_sentence_en = "Translation Error"

        save_history_entry(sentence, "idiom_detected", "fuzzy_single", idiom_dict['idiom'], full_sentence_en, highest_score)

        return jsonify({
            "status": "idiom_detected",
            "match_type": "fuzzy_single",
            "confidence": highest_score,
            "literal_meaning_en": literal_meaning_en,
            "results_list": [{
                "result": idiom_dict,
                "idiom_english_translation": idiom_dict.get('idiom'), # Simplified for brevity
                "matched_phrase": best_match_phrase
            }],
            "full_sentence_kannada": full_sentence_kn,
            "full_sentence_english": full_sentence_en
        })

    # 6. No Idiom Found
    save_history_entry(sentence, "no_idiom_detected", "", "", literal_meaning_en)
    
    literal_meaning_kn = sentence
    if lang == "en":
        try: literal_meaning_kn = translator.translate(sentence, src="en", dest="kn").text
        except: pass

    return jsonify({
        "status": "no_idiom_detected",
        "literal_meaning_en": literal_meaning_en,
        "literal_meaning_kn": literal_meaning_kn,
        "normal_translation": literal_meaning_en
    })

def save_history_entry(original, status, match_type, idiom, translation, confidence=None):
    """Helper to save history to DB"""
    try:
        new_entry = History(
            email=session.get('email', 'anonymous'),
            original_sentence=original,
            status=status,
            match_type=match_type,
            idiom=idiom,
            confidence=confidence,
            translation=translation,
            timestamp=datetime.now()
        )
        db.session.add(new_entry)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        logging.error(f"DB Error: {e}")

# =================== UTILITY ROUTES ====================

@main_bp.route("/synthesize", methods=["GET"])
def synthesize_speech():
    text = request.args.get("text")
    lang = request.args.get("lang", "kn")
    if not text: return jsonify({"error": "No text"}), 400
    try:
        tts = gTTS(text=text, lang=lang)
        mp3_fp = io.BytesIO()
        tts.write_to_fp(mp3_fp)
        mp3_fp.seek(0)
        return send_file(mp3_fp, mimetype="audio/mpeg", download_name="speech.mp3")
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@main_bp.route("/feedback", methods=["POST"])
def feedback():
    if not session.get("user_logged_in"):
        return jsonify({"error": "Login required"}), 401
    
    data = request.get_json()
    msg = data.get("feedback")
    if not msg: return jsonify({"error": "Empty message"}), 400

    try:
        fb = Feedback(message=msg, email=session.get("email"), timestamp=datetime.now())
        db.session.add(fb)
        db.session.commit()
        return jsonify({"message": "Feedback sent"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@main_bp.route('/suggest_idiom', methods=['POST'])
def suggest_idiom():
    data = request.get_json()
    if not data.get('idiom') or not data.get('example'):
        return jsonify({"error": "Missing fields"}), 400

    try:
        # Check for duplicate suggestion
        existing = Suggestion.query.filter_by(idiom=data['idiom']).first()
        if existing:
            return jsonify({"error": "This suggestion is already pending."}), 400

        sug = Suggestion(
            idiom=data['idiom'],
            explanation_kannada=data['example'],
            timestamp=datetime.now()
        )
        db.session.add(sug)
        db.session.commit()
        return jsonify({"message": "Suggestion submitted."})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@main_bp.route("/recognize_speech", methods=["POST"])
def recognize_speech():
    if "audio" not in request.files: return jsonify({"error": "No audio"}), 400
    file = request.files["audio"]
    if file.filename == "": return jsonify({"error": "No file"}), 400

    r = sr.Recognizer()
    try:
        audio = AudioSegment.from_file(file)
        wav_io = io.BytesIO()
        audio.export(wav_io, format="wav")
        wav_io.seek(0)
        with sr.AudioFile(wav_io) as source:
            data = r.record(source)
        text = r.recognize_google(data, language="kn-IN")
        return jsonify({"text": text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# =================== PUBLIC HISTORY ====================

@main_bp.route('/history', methods=['GET'])
def get_public_history():
    items = History.query.order_by(History.timestamp.desc()).all()
    return jsonify([i.to_dict() for i in items])

@main_bp.route('/clear_history', methods=['POST'])
def clear_public_history():
    db.session.query(History).delete()
    db.session.commit()
    return jsonify({"message": "Cleared"})

# =================== ADMIN ROUTES ====================

@main_bp.route('/admin')
@admin_required
def admin_dashboard():
    history = History.query.order_by(History.timestamp.desc()).all()
    suggestions = Suggestion.query.all()
    feedback_items = Feedback.query.order_by(Feedback.timestamp.desc()).all()
    return render_template('admin.html', history=history, suggestions=suggestions, feedback=[f.to_dict() for f in feedback_items])

@main_bp.route('/admin/approve_idiom', methods=['POST'])
@admin_required
def approve_idiom():
    s_id = request.form.get('id')
    if not s_id: return redirect(url_for('main.admin_dashboard'))

    try:
        suggestion = Suggestion.query.get(s_id)
        if suggestion:
            clean_idiom = suggestion.idiom.strip()
            clean_kn = suggestion.explanation_kannada.strip()
            
            # Translate Logic
            try: 
                gen_en = Translator().translate(clean_kn, src='kn', dest='en').text
            except: 
                gen_en = "Translation unavailable"

            existing = Idiom.query.filter_by(idiom=clean_idiom).first()
            if existing:
                existing.explanation_kannada = clean_kn
                existing.explanation_english = gen_en
            else:
                new_idiom = Idiom(idiom=clean_idiom, explanation_english=gen_en, explanation_kannada=clean_kn)
                db.session.add(new_idiom)

            db.session.delete(suggestion)
            db.session.commit()
            
            # REFRESH CACHE
            refresh_idiom_cache()

    except Exception as e:
        db.session.rollback()
        logging.error(f"Approval error: {e}")

    return redirect(url_for('main.admin_dashboard'))

@main_bp.route('/admin/reject_idiom', methods=['POST'])
@admin_required
def reject_idiom():
    idiom_txt = request.form.get('idiom')
    if idiom_txt:
        Suggestion.query.filter_by(idiom=idiom_txt).delete()
        db.session.commit()
    return redirect(url_for('main.admin_dashboard'))

@main_bp.route('/admin/export/tsv', methods=['GET'])
@admin_required
def export_tsv():
    # EXPORT AS TSV (Tab Separated) as requested
    items = History.query.all()
    if not items: return "Empty history", 404
    
    data = [i.to_dict() for i in items]
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=sorted(list(data[0].keys())), delimiter='\t')
    writer.writeheader()
    writer.writerows(data)
    
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8')),
        mimetype='text/tab-separated-values',
        as_attachment=True,
        download_name='translation_history.tsv'
    )
# Add these to routes.py

@main_bp.route('/admin/clear_history', methods=['POST'])
@admin_required
def clear_admin_history():
    try:
        db.session.query(History).delete()
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error clearing admin history: {e}")
    return redirect(url_for('main.admin_dashboard'))

@main_bp.route('/admin/export/json', methods=['GET'])
@admin_required
def download_admin_history_json():
    history_items = History.query.all()
    history_list = [item.to_dict() for item in history_items]
    
    json_bytes = io.BytesIO(
        json.dumps(history_list, ensure_ascii=False, indent=2).encode('utf-8')
    )
    return send_file(
        json_bytes,
        mimetype='application/json',
        as_attachment=True,
        download_name='translation_history.json'
    )