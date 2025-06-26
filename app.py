from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import requests

BASE_URL = "http://127.0.0.1:8000"

app = Flask(__name__)
app.secret_key = "Ajay@1234"

@app.route("/", methods=["GET", "POST"])
def index():
    return redirect(url_for("medical_assistant"))

@app.route("/assistant", methods=["GET", "POST"])
def medical_assistant():
    if "messages" not in session:
        session["messages"] = []

    # Only handle the "clear" button
    if request.method == "POST" and request.form.get("clear"):
        session["messages"] = []
        return redirect(url_for("medical_assistant"))

    return render_template("assistant.html")


@app.route("/assistant-ajax", methods=["POST"])
def assistant_ajax():
    data = request.get_json()
    question = data.get("question", "").strip()

    if not question:
        return jsonify({"reply": "⚠️ No question received."})

    messages = session.get("messages", [])
    messages.append({"role": "user", "content": question})

    try:
        response = requests.post(f"{BASE_URL}/ask", json={"question": question}, timeout=20)
        if response.status_code == 200:
            answer = response.json().get("answer", "No response from backend.")
        else:
            answer = f"Error: {response.status_code}"
    except Exception as e:
        answer = f"Backend error: {e}"

    messages.append({"role": "assistant", "content": answer})
    session["messages"] = messages[-10:]

    return jsonify({"reply": answer})







@app.route("/view", methods=["GET"])
def view_patients():
    try:
        response = requests.get(f"{BASE_URL}/view", timeout=10)
        if response.status_code == 200:
            patients_dict = response.json()
            patients_list = list(patients_dict.values())
        else:
            patients_list = []
    except Exception as e:
        print(f"Error fetching patients: {e}")
        patients_list = []

    # print(f"DEBUG patients list: {patients_list}")
    return render_template("view.html", patients=patients_list)



@app.route("/sort", methods=["GET", "POST"])
def sort_patients():
    patients_list = []
    sort_by = None
    order = None

    if request.method == "POST":
        sort_by = request.form.get("sort_by")
        order = request.form.get("order")
        
        try:
            url = f"{BASE_URL}/sort?sort_by={sort_by}&order={order}"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                patients_list = response.json()  # Directly use as list of dicts
            else:
                print(f"Backend returned error: {response.status_code}")
        except Exception as e:
            print(f"Error fetching sorted patients: {e}")
    
    return render_template("sort.html", patients=patients_list, sort_by=sort_by, order=order)




@app.route("/register", methods=["GET", "POST"])
def register_patient():
    if request.method == "POST":
        payload = {
            "id": request.form.get("id"),
            "name": request.form.get("name"),
            "city": request.form.get("city"),
            "age": int(request.form.get("age")),
            "gender": request.form.get("gender"),
            "height": float(request.form.get("height")),
            "weight": float(request.form.get("weight")),
        }
        try:
            response = requests.post(f"{BASE_URL}/create", json=payload, timeout=10)
            if response.status_code in (200, 201):
                return render_template("register.html", success="Patient registered successfully!")
            else:
                return render_template("register.html", error=f"API Error: {response.text}")
        except Exception as e:
            return render_template("register.html", error=f"Request failed: {e}")

    return render_template("register.html")


@app.route("/update", methods=["GET", "POST"])
def update_patient():
    search_id = None
    patient = None

    if request.method == "POST":
        search_id = request.form.get("search_id")
        action = request.form.get("action")

        if action == "fetch" and search_id:
            try:
                resp = requests.get(f"{BASE_URL}/patient/{search_id}", timeout=10)
                if resp.status_code == 200:
                    patient = resp.json()
                else:
                    return render_template("update.html", error="Patient not found.", search_id=search_id)
            except Exception as e:
                return render_template("update.html", error=f"Fetch failed: {e}", search_id=search_id)

        elif action == "update" and search_id:
            payload = {}
            if request.form.get("name"):
                payload["name"] = request.form.get("name")
            if request.form.get("city"):
                payload["city"] = request.form.get("city")
            if request.form.get("age"):
                payload["age"] = int(request.form.get("age"))
            if request.form.get("height"):
                payload["height"] = float(request.form.get("height"))
            if request.form.get("weight"):
                payload["weight"] = float(request.form.get("weight"))
            if request.form.get("gender"):
                payload["gender"] = request.form.get("gender")

            if not payload:
                return render_template("update.html", error="No fields changed.", search_id=search_id)

            try:
                resp = requests.put(f"{BASE_URL}/edit/{search_id}", json=payload, timeout=10)
                if resp.status_code == 200:
                    return render_template("update.html", success="Patient updated successfully!", search_id=search_id)
                else:
                    return render_template("update.html", error=f"Update failed: {resp.text}", search_id=search_id)
            except Exception as e:
                return render_template("update.html", error=f"Update failed: {e}", search_id=search_id)

    return render_template("update.html", search_id=search_id, patient=patient)


@app.route("/delete", methods=["GET", "POST"])
def delete_patient():
    patient = None
    delete_id = None

    if request.method == "POST":
        delete_id = request.form.get("delete_id")
        action = request.form.get("action")

        if action == "fetch" and delete_id:
            try:
                resp = requests.get(f"{BASE_URL}/patient/{delete_id}", timeout=10)
                if resp.status_code == 200:
                    patient = resp.json()
                else:
                    return render_template("delete.html", error="Patient not found.", delete_id=delete_id)
            except Exception as e:
                return render_template("delete.html", error=f"Fetch failed: {e}", delete_id=delete_id)

        elif action == "delete" and delete_id:
            try:
                resp = requests.delete(f"{BASE_URL}/delete/{delete_id}", timeout=10)
                if resp.status_code == 200:
                    return render_template("delete.html", success="Patient deleted successfully!")
                else:
                    return render_template("delete.html", error=f"Delete failed: {resp.text}")
            except Exception as e:
                return render_template("delete.html", error=f"Delete failed: {e}")

    return render_template("delete.html", patient=patient, delete_id=delete_id)


def cast_value(field, val):
    if field in ["age"]:
        return int(val)
    if field in ["height", "weight"]:
        return float(val)
    return val

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=7860)