from flask import Flask, render_template, request
from matchmaking import find_matches

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        user_id = request.form.get("user_id").strip()
        results = find_matches(user_id)
        if results is None:
            return render_template("results.html", error="User ID not found.")
        return render_template("results.html", results=results, user_id=user_id)
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
