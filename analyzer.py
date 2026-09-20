import re


# ============================================================
# WORD NORMALIZATION
# ============================================================

def normalize_word(word):

    word = word.lower().strip()

    replacements = {
        "overheating": "overheat",
        "overheats": "overheat",
        "overheated": "overheat",

        "leaking": "leak",
        "leaks": "leak",
        "leaked": "leak",

        "broken": "break",

        "damaged": "damage",
        "damaging": "damage",

        "fails": "fail",
        "failed": "fail",

        "stops": "stop",
        "stopped": "stop",

        "crashes": "crash",
        "crashed": "crash"
    }

    return replacements.get(word, word)


# ============================================================
# CONTEXT EXTRACTION
# ============================================================

def extract_context(text):

    text_lower = text.lower()

    context = {
        "deadlines": [],
        "time_conditions": [],
        "locations": [],
        "conditions": [],
        "priorities": [],
        "quantities": []
    }

    # ========================================================
    # DEADLINES
    # ========================================================

    deadline_patterns = [

        r"\b(?:before|by)\s+(?:monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b",

        r"\b(?:before|by)\s+(?:today|tomorrow|tonight|next week)\b",

        r"\bwithin\s+\d+\s+(?:hours?|days?|weeks?)\b"
    ]

    for pattern in deadline_patterns:

        matches = re.findall(
            pattern,
            text_lower
        )

        for match in matches:

            if match not in context["deadlines"]:

                context["deadlines"].append(match)


    # ========================================================
    # TIME CONDITIONS
    # ========================================================

    time_patterns = [

        r"\bafter\s+\d+\s+(?:hours?|minutes?|days?|weeks?)\b",

        r"\bbefore\s+\d{1,2}(?::\d{2})?\s*(?:am|pm)\b",

        r"\bduring\s+\d+\s+(?:hours?|minutes?)\b",

        r"\bafter\s+heavy\s+rain\b",

        r"\bduring\s+heavy\s+rain\b",

        r"\bwhen\s+it\s+rains\b",

        r"\bwhen\s+raining\b",

        r"\bduring\s+peak\s+hours\b",

        r"\bat\s+night\b",

        r"\bin\s+the\s+morning\b",

        r"\bin\s+the\s+evening\b",

        r"\bduring\s+the\s+day\b",

        r"\bevery\s+day\b",

        r"\bevery\s+night\b"
    ]

    for pattern in time_patterns:

        matches = re.findall(
            pattern,
            text_lower
        )

        for match in matches:

            if match not in context["time_conditions"]:

                context["time_conditions"].append(match)


    # ========================================================
    # LOCATIONS
    # ========================================================

    location_words = [

        "college",
        "hostel",
        "office",
        "factory",
        "hospital",
        "school",
        "warehouse",
        "branch",
        "gate",
        "lab",
        "room",
        "campus",
        "shop",
        "store",
        "station",
        "block",
        "building",
        "road",
        "street",
        "parking",
        "library",
        "classroom"
    ]

    for location in location_words:

        if re.search(
            rf"\b{re.escape(location)}\b",
            text_lower
        ):

            context["locations"].append(location)


    # ========================================================
    # CONDITIONS
    # ========================================================

    condition_words = [

        "overheat",
        "overheating",

        "leak",
        "leaking",

        "broken",
        "break",

        "damaged",
        "damage",

        "unsafe",

        "not working",

        "fails",
        "fail",
        "failure",

        "stops",
        "stop",
        "stopped",

        "cracked",

        "blocked",

        "missing",

        "error",

        "crash",
        "crashes",

        "slow",

        "short circuit",

        "slippery",

        "flood",
        "flooding",

        "smoke",

        "noise",

        "vibration",

        "power outage",

        "water shortage",

        "low pressure"
    ]

    for condition in condition_words:

        if re.search(
            rf"\b{re.escape(condition)}\b",
            text_lower
        ):

            normalized = normalize_word(condition)

            if normalized not in context["conditions"]:

                context["conditions"].append(normalized)


    # ========================================================
    # PRIORITIES
    # ========================================================

    if re.search(
        r"\b(?:urgent|critical|emergency|high priority)\b",
        text_lower
    ):

        context["priorities"].append("urgent")

    elif re.search(
        r"\b(?:routine|normal|low priority)\b",
        text_lower
    ):

        context["priorities"].append("routine")


    # ========================================================
    # QUANTITIES
    # ========================================================

    quantity_pattern = (
        r"\b\d+\s+"
        r"(?:machines?|devices?|units?|items?|products?|orders?|"
        r"tickets?|requests?|files?|servers?|systems?|vehicles?|"
        r"people|workers?|customers?|students?|components?|parts?|"
        r"tasks?|records?|documents?|boxes?|packages?|issues?|cases?)\b"
    )

    quantity_matches = re.findall(
        quantity_pattern,
        text_lower
    )

    for quantity in quantity_matches:

        if quantity not in context["quantities"]:

            context["quantities"].append(quantity)


    return context


# ============================================================
# CONTEXT OVERLAP
# ============================================================

def _overlap(original_items, handoff_items):

    if not original_items:

        return 100

    if not handoff_items:

        return 0

    original_set = set(original_items)
    handoff_set = set(handoff_items)

    common = original_set.intersection(
        handoff_set
    )

    return (
        len(common)
        / len(original_set)
    ) * 100


# ============================================================
# CONTEXT COMPARISON
# ============================================================

def compare_context(original, handoff):

    original_context = extract_context(
        original
    )

    handoff_context = extract_context(
        handoff
    )

    lost = []
    changed = []
    conflicts = []

    # ========================================================
    # WEIGHTS
    # ========================================================

    weights = {
        "deadline": 30,
        "time": 20,
        "condition": 30,
        "location": 10,
        "priority": 10,
        "quantity": 10
    }

    integrity = 100


    # ========================================================
    # DEADLINES
    # ========================================================

    original_deadlines = original_context[
        "deadlines"
    ]

    handoff_deadlines = handoff_context[
        "deadlines"
    ]

    if original_deadlines:

        if not handoff_deadlines:

            for deadline in original_deadlines:

                lost.append(
                    f"Deadline information lost: '{deadline}'"
                )

            integrity -= weights["deadline"]


        elif original_deadlines != handoff_deadlines:

            changed.append(
                "Deadline changed: "
                + ", ".join(original_deadlines)
                + " → "
                + ", ".join(handoff_deadlines)
            )

            integrity -= weights["deadline"]


    # ========================================================
    # TIME CONDITIONS
    # ========================================================

    original_times = original_context[
        "time_conditions"
    ]

    handoff_times = handoff_context[
        "time_conditions"
    ]

    if original_times:

        if not handoff_times:

            for time_condition in original_times:

                lost.append(
                    f"Time condition lost: '{time_condition}'"
                )

            integrity -= weights["time"]


        elif original_times != handoff_times:

            changed.append(
                "Time condition changed: "
                + ", ".join(original_times)
                + " → "
                + ", ".join(handoff_times)
            )

            integrity -= weights["time"]


    # ========================================================
    # CONDITIONS
    # ========================================================

    original_conditions = original_context[
        "conditions"
    ]

    handoff_conditions = handoff_context[
        "conditions"
    ]

    if original_conditions:

        missing_conditions = [
            condition
            for condition in original_conditions
            if condition not in handoff_conditions
        ]

        if missing_conditions:

            for condition in missing_conditions:

                lost.append(
                    f"Problem condition lost: '{condition}'"
                )

            integrity -= weights["condition"]


    # ========================================================
    # LOCATIONS
    # ========================================================

    original_locations = original_context[
        "locations"
    ]

    handoff_locations = handoff_context[
        "locations"
    ]

    if original_locations:

        missing_locations = [
            location
            for location in original_locations
            if location not in handoff_locations
        ]

        if missing_locations:

            for location in missing_locations:

                lost.append(
                    f"Location information lost: '{location}'"
                )

            integrity -= (
                weights["location"]
                * len(missing_locations)
                / max(len(original_locations), 1)
            )


    # ========================================================
    # PRIORITY
    # ========================================================

    original_priorities = original_context[
        "priorities"
    ]

    handoff_priorities = handoff_context[
        "priorities"
    ]

    if original_priorities and handoff_priorities:

        original_priority = original_priorities[0]
        handoff_priority = handoff_priorities[0]

        if original_priority != handoff_priority:

            conflicts.append(
                "Priority conflict: "
                "original request is "
                + original_priority
                + " but handoff says "
                + handoff_priority
            )

            integrity -= weights["priority"]


    # ========================================================
    # QUANTITIES
    # ========================================================

    original_quantities = original_context[
        "quantities"
    ]

    handoff_quantities = handoff_context[
        "quantities"
    ]

    if original_quantities and handoff_quantities:

        if original_quantities != handoff_quantities:

            changed.append(
                "Quantity changed: "
                + ", ".join(original_quantities)
                + " → "
                + ", ".join(handoff_quantities)
            )

            integrity -= weights["quantity"]


    elif original_quantities and not handoff_quantities:

        for quantity in original_quantities:

            lost.append(
                f"Quantity information lost: '{quantity}'"
            )

        integrity -= weights["quantity"]


    # ========================================================
    # KEEP INTEGRITY BETWEEN 0 AND 100
    # ========================================================

    integrity = max(
        0,
        min(100, round(integrity))
    )


    # ========================================================
    # TEXT SIMILARITY
    # ========================================================

    stop_words = {
        "the", "a", "an", "is", "are", "was", "were",
        "be", "to", "of", "in", "on", "at", "for", "and",
        "or", "but", "it", "this", "that", "with", "from",
        "as", "by", "before", "after", "because", "please",
        "should", "can", "has", "have", "had", "do", "does",
        "did", "will", "would", "could", "may", "might",
        "than", "into", "their", "there", "they", "we", "you",
        "i", "he", "she", "customer", "team"
    }

    def get_similarity_words(text):

        words = re.findall(
            r"\b[a-zA-Z]+\b",
            text.lower()
        )

        normalized_words = []

        for word in words:

            if word in stop_words:
                continue

            normalized_words.append(
                normalize_word(word)
            )

        return set(normalized_words)


    original_words = get_similarity_words(
        original
    )

    handoff_words = get_similarity_words(
        handoff
    )

    if original_words and handoff_words:

        common_words = (
            original_words
            .intersection(handoff_words)
        )

        precision = (
            len(common_words)
            / len(handoff_words)
        )

        recall = (
            len(common_words)
            / len(original_words)
        )

        if precision + recall:

            f1_similarity = (
                2
                * precision
                * recall
                / (precision + recall)
            ) * 100

        else:

            f1_similarity = 0

    else:

        f1_similarity = 0


    # ========================================================
    # CONTEXT-AWARE SIMILARITY
    # ========================================================

    context_keys = [
        "deadlines",
        "time_conditions",
        "locations",
        "conditions",
        "priorities",
        "quantities"
    ]

    important_original = set()
    important_handoff = set()

    for key in context_keys:

        for item in original_context[key]:

            important_original.update(
                get_similarity_words(item)
            )

        for item in handoff_context[key]:

            important_handoff.update(
                get_similarity_words(item)
            )


    if important_original:

        context_overlap = (
            len(
                important_original.intersection(
                    important_handoff
                )
            )
            / len(important_original)
        ) * 100

    else:

        context_overlap = 100


    # 80% text overlap + 20% important-context overlap.

    similarity = (
        (f1_similarity * 0.80)
        + (context_overlap * 0.20)
    )

    similarity = round(
        min(100, max(0, similarity)),
        2
    )


    # ========================================================
    # RISK LEVEL
    # ========================================================

    if conflicts:

        risk = "CRITICAL"

    elif integrity < 40:

        risk = "HIGH"

    elif integrity < 70:

        risk = "MEDIUM"

    else:

        risk = "LOW"


    # ========================================================
    # INTEGRITY BREAKDOWN
    # ========================================================

    integrity_breakdown = []

    if lost:

        for item in lost:

            integrity_breakdown.append(
                {
                    "type": "LOST",
                    "message": item
                }
            )


    if changed:

        for item in changed:

            integrity_breakdown.append(
                {
                    "type": "CHANGED",
                    "message": item
                }
            )


    if conflicts:

        for item in conflicts:

            integrity_breakdown.append(
                {
                    "type": "CONFLICT",
                    "message": item
                }
            )


    if not integrity_breakdown:

        integrity_breakdown.append(
            {
                "type": "PRESERVED",
                "message": "All important context was preserved."
            }
        )


    # ========================================================
    # FINAL RESULT
    # ========================================================

    return {

        "similarity": similarity,

        "integrity": integrity,

        "risk": risk,

        "lost": lost,

        "changed": changed,

        "conflicts": conflicts,

        "integrity_breakdown": integrity_breakdown
    }


# ============================================================
# TEST CASES
# ============================================================

if __name__ == "__main__":

    # --------------------------------------------------------
    # TEST 1 - INFORMATION LOSS
    # --------------------------------------------------------

    print("\n")
    print("=" * 42)
    print("TEST 1 - INFORMATION LOSS")
    print("=" * 42)

    original = (
        "Repair machine X before Friday. "
        "It overheats after 2 hours "
        "at the college factory."
    )

    handoff = (
        "Repair machine X. "
        "Customer reports overheating."
    )

    result = compare_context(
        original,
        handoff
    )

    print("\nOriginal:")
    print(original)

    print("\nHandoff:")
    print(handoff)

    print("\n")
    print("=" * 42)
    print("          CONTEXTLOSS ANALYZER")
    print("=" * 42)

    print(
        f"\nContext Similarity : "
        f"{result['similarity']}%"
    )

    print(
        f"Context Integrity  : "
        f"{result['integrity']}%"
    )

    print(
        f"Risk Level         : "
        f"{result['risk']}"
    )

    print("\n🔴 LOST INFORMATION")

    if result["lost"]:

        for item in result["lost"]:

            print("  ❌ " + item)

    else:

        print("  None")


    print("\n🟡 CHANGED INFORMATION")

    if result["changed"]:

        for item in result["changed"]:

            print("  ⚠️ " + item)

    else:

        print("  None")


    print("\n🟠 CONFLICTING INFORMATION")

    if result["conflicts"]:

        for item in result["conflicts"]:

            print("  🚨 " + item)

    else:

        print("  None")


    print("\n🔎 INTEGRITY BREAKDOWN")

    for item in result["integrity_breakdown"]:

        print(
            f"  [{item['type']}] "
            f"{item['message']}"
        )


    # --------------------------------------------------------
    # TEST 2 - GOOD HANDOFF
    # --------------------------------------------------------

    print("\n")
    print("=" * 42)
    print("TEST 2 - GOOD HANDOFF")
    print("=" * 42)

    original = (
        "Repair machine X before Friday. "
        "It overheats after 2 hours "
        "at the college factory."
    )

    handoff = (
        "Repair machine X before Friday. "
        "It is overheating after 2 hours "
        "at the college factory."
    )

    result = compare_context(
        original,
        handoff
    )

    print("\nOriginal:")
    print(original)

    print("\nHandoff:")
    print(handoff)

    print("\n")
    print("=" * 42)
    print("          CONTEXTLOSS ANALYZER")
    print("=" * 42)

    print(
        f"\nContext Similarity : "
        f"{result['similarity']}%"
    )

    print(
        f"Context Integrity  : "
        f"{result['integrity']}%"
    )

    print(
        f"Risk Level         : "
        f"{result['risk']}"
    )

    print("\n🔴 LOST INFORMATION")

    print(
        "  None"
        if not result["lost"]
        else "\n".join(
            "  ❌ " + item
            for item in result["lost"]
        )
    )

    print("\n🟡 CHANGED INFORMATION")

    print(
        "  None"
        if not result["changed"]
        else "\n".join(
            "  ⚠️ " + item
            for item in result["changed"]
        )
    )

    print("\n🟠 CONFLICTING INFORMATION")

    print(
        "  None"
        if not result["conflicts"]
        else "\n".join(
            "  🚨 " + item
            for item in result["conflicts"]
        )
    )

    print("\n🔎 INTEGRITY BREAKDOWN")

    for item in result["integrity_breakdown"]:

        print(
            f"  [{item['type']}] "
            f"{item['message']}"
        )


    # --------------------------------------------------------
    # TEST 3 - CONFLICT
    # --------------------------------------------------------

    print("\n")
    print("=" * 42)
    print("TEST 3 - CONFLICT")
    print("=" * 42)

    original = (
        "Urgent repair required for the machine "
        "before Friday."
    )

    handoff = (
        "Routine repair can be handled next week."
    )

    result = compare_context(
        original,
        handoff
    )

    print("\nOriginal:")
    print(original)

    print("\nHandoff:")
    print(handoff)

    print("\n")
    print("=" * 42)
    print("          CONTEXTLOSS ANALYZER")
    print("=" * 42)

    print(
        f"\nContext Similarity : "
        f"{result['similarity']}%"
    )

    print(
        f"Context Integrity  : "
        f"{result['integrity']}%"
    )

    print(
        f"Risk Level         : "
        f"{result['risk']}"
    )

    print("\n🔴 LOST INFORMATION")

    print(
        "  None"
        if not result["lost"]
        else "\n".join(
            "  ❌ " + item
            for item in result["lost"]
        )
    )

    print("\n🟡 CHANGED INFORMATION")

    print(
        "  None"
        if not result["changed"]
        else "\n".join(
            "  ⚠️ " + item
            for item in result["changed"]
        )
    )

    print("\n🟠 CONFLICTING INFORMATION")

    print(
        "  None"
        if not result["conflicts"]
        else "\n".join(
            "  🚨 " + item
            for item in result["conflicts"]
        )
    )

    print("\n🔎 INTEGRITY BREAKDOWN")

    for item in result["integrity_breakdown"]:

        print(
            f"  [{item['type']}] "
            f"{item['message']}"
        )


    # --------------------------------------------------------
    # TEST 4 - QUANTITY CHANGE
    # --------------------------------------------------------

    print("\n")
    print("=" * 42)
    print("TEST 4 - QUANTITY CHANGE")
    print("=" * 42)

    original = (
        "Repair 5 machines before Friday "
        "at the college factory."
    )

    handoff = (
        "Repair 3 machines before Friday "
        "at the college factory."
    )

    result = compare_context(
        original,
        handoff
    )

    print("\nOriginal:")
    print(original)

    print("\nHandoff:")
    print(handoff)

    print("\n")
    print("=" * 42)
    print("          CONTEXTLOSS ANALYZER")
    print("=" * 42)

    print(
        f"\nContext Similarity : "
        f"{result['similarity']}%"
    )

    print(
        f"Context Integrity  : "
        f"{result['integrity']}%"
    )

    print(
        f"Risk Level         : "
        f"{result['risk']}"
    )

    print("\n🔴 LOST INFORMATION")

    print(
        "  None"
        if not result["lost"]
        else "\n".join(
            "  ❌ " + item
            for item in result["lost"]
        )
    )

    print("\n🟡 CHANGED INFORMATION")

    print(
        "  None"
        if not result["changed"]
        else "\n".join(
            "  ⚠️ " + item
            for item in result["changed"]
        )
    )

    print("\n🟠 CONFLICTING INFORMATION")

    print(
        "  None"
        if not result["conflicts"]
        else "\n".join(
            "  🚨 " + item
            for item in result["conflicts"]
        )
    )

    print("\n🔎 INTEGRITY BREAKDOWN")

    for item in result["integrity_breakdown"]:

        print(
            f"  [{item['type']}] "
            f"{item['message']}"
        )


    # --------------------------------------------------------
    # TEST 5 - RAIN CONDITION
    # --------------------------------------------------------

    print("\n")
    print("=" * 42)
    print("TEST 5 - RAIN CONDITION")
    print("=" * 42)

    original = (
        "The water pipe in Hostel Block A "
        "is leaking. Please repair it before Monday "
        "because the floor becomes slippery "
        "after heavy rain."
    )

    handoff = (
        "Hostel Block A has a water leakage. "
        "Maintenance team should check the pipe."
    )

    result = compare_context(
        original,
        handoff
    )

    print("\nOriginal:")
    print(original)

    print("\nHandoff:")
    print(handoff)

    print("\n")
    print("=" * 42)
    print("          CONTEXTLOSS ANALYZER")
    print("=" * 42)

    print(
        f"\nContext Similarity : "
        f"{result['similarity']}%"
    )

    print(
        f"Context Integrity  : "
        f"{result['integrity']}%"
    )

    print(
        f"Risk Level         : "
        f"{result['risk']}"
    )

    print("\n🔴 LOST INFORMATION")

    print(
        "  None"
        if not result["lost"]
        else "\n".join(
            "  ❌ " + item
            for item in result["lost"]
        )
    )

    print("\n🟡 CHANGED INFORMATION")

    print(
        "  None"
        if not result["changed"]
        else "\n".join(
            "  ⚠️ " + item
            for item in result["changed"]
        )
    )

    print("\n🟠 CONFLICTING INFORMATION")

    print(
        "  None"
        if not result["conflicts"]
        else "\n".join(
            "  🚨 " + item
            for item in result["conflicts"]
        )
    )

    print("\n🔎 INTEGRITY BREAKDOWN")

    for item in result["integrity_breakdown"]:

        print(
            f"  [{item['type']}] "
            f"{item['message']}"
        )


    print("\n")
    print("=" * 42)
    print("ALL TESTS COMPLETED")
    print("=" * 42)

