from opensearchpy import OpenSearch

from analyzer import extract_context


client = OpenSearch(
    hosts=[{"host": "localhost", "port": 9200}],
    use_ssl=False,
    verify_certs=False
)

INDEX_NAME = "contextloss_cases"


def ensure_index():
    """
    Make sure the OpenSearch index exists.
    """

    if not client.indices.exists(index=INDEX_NAME):
        client.indices.create(index=INDEX_NAME)
        print("OpenSearch index created.")


def save_case(case):
    """
    Save a case to OpenSearch.

    Features:
    - Prevents exact duplicate cases.
    - Stores important context extracted from the original complaint.
    """

    ensure_index()

    original = case.get("original", "").strip()
    handoff = case.get("handoff", "").strip()

    # -----------------------------------------
    # Extract important context
    # -----------------------------------------

    context = extract_context(original)

    case_to_save = dict(case)

    case_to_save["conditions"] = context.get(
        "conditions",
        []
    )

    case_to_save["locations"] = context.get(
        "locations",
        []
    )

    case_to_save["deadlines"] = context.get(
        "deadlines",
        []
    )

    case_to_save["time_conditions"] = context.get(
        "time_conditions",
        []
    )

    case_to_save["priorities"] = context.get(
        "priorities",
        []
    )

    case_to_save["quantities"] = context.get(
        "quantities",
        []
    )

    # -----------------------------------------
    # Check exact duplicate
    # -----------------------------------------

    duplicate_query = {
        "query": {
            "bool": {
                "must": [
                    {
                        "match_phrase": {
                            "original": original
                        }
                    },
                    {
                        "match_phrase": {
                            "handoff": handoff
                        }
                    }
                ]
            }
        }
    }

    response = client.search(
        index=INDEX_NAME,
        body=duplicate_query
    )

    if response["hits"]["total"]["value"] > 0:

        existing_id = response["hits"]["hits"][0]["_id"]

        print(
            "Duplicate case detected. "
            "Not saving again."
        )

        return existing_id

    # -----------------------------------------
    # Save new case
    # -----------------------------------------

    response = client.index(
        index=INDEX_NAME,
        body=case_to_save,
        refresh=True
    )

    print("New case saved to OpenSearch.")

    return response["_id"]


def _get_context(source):
    """
    Get context from an existing OpenSearch document.

    New documents already contain context fields.

    Older documents may not contain them, so their
    context is extracted from the original complaint.
    """

    original = source.get(
        "original",
        ""
    )

    extracted_context = extract_context(original)

    return {
        "conditions": source.get(
            "conditions"
        ) or extracted_context.get(
            "conditions",
            []
        ),

        "locations": source.get(
            "locations"
        ) or extracted_context.get(
            "locations",
            []
        ),

        "deadlines": source.get(
            "deadlines"
        ) or extracted_context.get(
            "deadlines",
            []
        ),

        "time_conditions": source.get(
            "time_conditions"
        ) or extracted_context.get(
            "time_conditions",
            []
        ),

        "priorities": source.get(
            "priorities"
        ) or extracted_context.get(
            "priorities",
            []
        ),

        "quantities": source.get(
            "quantities"
        ) or extracted_context.get(
            "quantities",
            []
        )
    }


def _overlap(current_items, historical_items):
    """
    Return common context items.
    """

    current = {
        str(item).strip().lower()
        for item in current_items
        if str(item).strip()
    }

    historical = {
        str(item).strip().lower()
        for item in historical_items
        if str(item).strip()
    }

    return sorted(
        current.intersection(historical)
    )


def search_similar_cases(
    text,
    current_original="",
    current_handoff="",
    limit=5,
    exclude_id=None
):
    """
    Search historical cases similar to the current case.

    Relevance is improved using:
    - problem conditions
    - locations
    - priorities
    - quantities

    Exact copies of the current case are removed.

    exclude_id:
    - Optional OpenSearch document ID.
    - Used to make sure the current case itself
      does not appear in similar historical cases.
    """

    ensure_index()

    # -----------------------------------------
    # Extract context from current case
    # -----------------------------------------

    current_context = extract_context(
        current_original
    )

    current_conditions = current_context.get(
        "conditions",
        []
    )

    current_locations = current_context.get(
        "locations",
        []
    )

    current_priorities = current_context.get(
        "priorities",
        []
    )

    current_quantities = current_context.get(
        "quantities",
        []
    )

    # -----------------------------------------
    # OpenSearch text search
    # -----------------------------------------

    query = {
        "size": max(limit * 10, 50),

        "query": {
            "multi_match": {
                "query": text,

                "fields": [
                    "original^3",
                    "handoff"
                ]
            }
        }
    }

    response = client.search(
        index=INDEX_NAME,
        body=query
    )

    candidates = []

    # -----------------------------------------
    # Process search results
    # -----------------------------------------

    for hit in response["hits"]["hits"]:

        source = hit["_source"]

        historical_original = source.get(
            "original",
            ""
        ).strip()

        historical_handoff = source.get(
            "handoff",
            ""
        ).strip()

        historical_id = str(
            hit.get("_id", "")
        )

        # -----------------------------------------
        # Remove current case using ID
        # -----------------------------------------

        if (
            exclude_id is not None
            and historical_id == str(exclude_id)
        ):
            continue

        # -----------------------------------------
        # Remove exact current case
        # -----------------------------------------

        if (
            historical_original == current_original.strip()
            and
            historical_handoff == current_handoff.strip()
        ):
            continue

        # -----------------------------------------
        # Extract historical context
        # -----------------------------------------

        historical_context = _get_context(
            source
        )

        condition_matches = _overlap(
            current_conditions,
            historical_context["conditions"]
        )

        location_matches = _overlap(
            current_locations,
            historical_context["locations"]
        )

        priority_matches = _overlap(
            current_priorities,
            historical_context["priorities"]
        )

        quantity_matches = _overlap(
            current_quantities,
            historical_context["quantities"]
        )

        # -----------------------------------------
        # Context relevance score
        # -----------------------------------------

        context_score = (
            len(condition_matches) * 10
            +
            len(location_matches) * 6
            +
            len(priority_matches) * 4
            +
            len(quantity_matches) * 3
        )

        # -----------------------------------------
        # If the current case has important context,
        # require at least one meaningful match.
        #
        # This prevents unrelated cases such as
        # MACHINE cases appearing for WATER cases.
        # -----------------------------------------

        has_current_context = (
            len(current_conditions) > 0
            or
            len(current_locations) > 0
            or
            len(current_priorities) > 0
            or
            len(current_quantities) > 0
        )

        if (
            has_current_context
            and
            context_score == 0
        ):
            continue

        # -----------------------------------------
        # Final relevance score
        # -----------------------------------------

        opensearch_score = hit.get(
            "_score",
            0
        )

        final_score = (
            context_score
            +
            opensearch_score
        )

        candidates.append({

            "id": historical_id,

            "original": historical_original,

            "handoff": historical_handoff,

            "risk": source.get(
                "risk",
                ""
            ),

            "integrity": source.get(
                "integrity",
                0
            ),

            "similarity": source.get(
                "similarity",
                0
            ),

            "score": final_score,

            "context_matches": {
                "conditions": condition_matches,
                "locations": location_matches,
                "priorities": priority_matches,
                "quantities": quantity_matches
            }
        })

    # -----------------------------------------
    # Sort by relevance
    # -----------------------------------------

    candidates.sort(
        key=lambda item: item["score"],
        reverse=True
    )

    # -----------------------------------------
    # Return top results
    # -----------------------------------------

    return candidates[:limit]


if __name__ == "__main__":

    print(
        "OpenSearch functions ready!"
    )