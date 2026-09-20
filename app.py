from flask import Flask, render_template, request, redirect, url_for, session

from analyzer import compare_context
from database import setup_database, save_case, get_cases

from opensearch_db import (
    save_case as opensearch_save_case,
    search_similar_cases
)


app = Flask(__name__)

# Secret key for Flask session
app.secret_key = "contextloss-demo-secret-key"

# Initialize SQLite database
setup_database()


@app.route("/", methods=["GET", "POST"])
def home():

    # =====================================================
    # POST: Analyze the submitted context
    # =====================================================

    if request.method == "POST":

        original = request.form.get(
            "original",
            ""
        ).strip()

        handoff = request.form.get(
            "handoff",
            ""
        ).strip()

        if original and handoff:

            # --------------------------------
            # 1. Analyze context
            # --------------------------------

            result = compare_context(
                original,
                handoff
            )

            # --------------------------------
            # 2. Save to SQLite
            # --------------------------------

            save_case(
                original,
                handoff,
                result
            )

            # --------------------------------
            # 3. Prepare OpenSearch document
            # --------------------------------

            opensearch_case = {
                "original": original,
                "handoff": handoff,
                "risk": result.get(
                    "risk",
                    "UNKNOWN"
                ),
                "integrity": result.get(
                    "integrity",
                    0
                ),
                "similarity": result.get(
                    "similarity",
                    0
                )
            }

            # --------------------------------
            # 4. Save to OpenSearch
            # --------------------------------

            current_case_id = opensearch_save_case(
                opensearch_case
            )

            # --------------------------------
            # 5. Search historical cases
            # --------------------------------

            similar_cases = search_similar_cases(
                original + " " + handoff,
                current_original=original,
                current_handoff=handoff,
                exclude_id=current_case_id
            )

            # --------------------------------
            # 6. Store result temporarily
            #    in Flask session
            # --------------------------------

            session["analysis"] = {
                "result": result,
                "original": original,
                "handoff": handoff,
                "similar_cases": similar_cases
            }

        # --------------------------------
        # IMPORTANT:
        # Redirect POST → GET
        # --------------------------------

        return redirect(url_for("home"))


    # =====================================================
    # GET: Display the page normally
    # =====================================================

    analysis = session.pop(
        "analysis",
        None
    )

    if analysis:

        return render_template(
            "index.html",
            result=analysis["result"],
            original=analysis["original"],
            handoff=analysis["handoff"],
            similar_cases=analysis["similar_cases"]
        )

    return render_template(
        "index.html",
        result=None,
        original="",
        handoff="",
        similar_cases=[]
    )


@app.route("/cases")
def cases():

    all_cases = get_cases()

    return render_template(
        "cases.html",
        cases=all_cases
    )


if __name__ == "__main__":

    app.run(
        debug=True
    )