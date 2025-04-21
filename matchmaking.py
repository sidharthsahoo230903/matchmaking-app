import pandas as pd

def find_matches(input_user_id, csv_path="data/xyz.csv"):
    # Load the CSV
    df = pd.read_csv(csv_path)

    # User input
    user_rows = df[df["USER ID"] == input_user_id]

    if user_rows.empty:
        return None  # If user ID is not found, return None

    ldr_values = user_rows["LDR (1: NO LDR)"].dropna().unique()
    user_locations = user_rows["LOCATION"].dropna().unique().tolist()
    commitment_values = user_rows["1: PLATONIC TO 5: COMMITTED"].dropna().unique()
    user_gender = user_rows["GENDER"].dropna().unique()

    # ---- Custom Rankings ----
    career_order = ["High clarity", "Moderate clarity", "Low clarity"]
    optimism_order = ["Positive", "Neutral", "Mixed", "Negative"]
    self_understanding_order = ["Detailed", "Moderate", "Low Effort"]

    # MBTI-DISC ranking list (highest to lowest approachable)
    mbti_disc_rank = [
        "ENFJ-I", "ENFJ-S", "ENFJ-C", "ENFJ-D",
        "ESFJ-I", "ESFJ-S", "ESFJ-C", "ESFJ-D",
        "ENFP-I", "ENFP-S", "ENFP-C", "ENFP-D",
        "ESFP-I", "ESFP-S", "ESFP-C", "ESFP-D",
        "INFJ-I", "INFJ-S", "INFJ-C", "INFJ-D",
        "ISFJ-I", "ISFJ-S", "ISFJ-C", "ISFJ-D",
        "INFP-I", "INFP-S", "INFP-C", "INFP-D",
        "ISFP-I", "ISFP-S", "ISFP-C", "ISFP-D",
        "ENTP-I", "ENTP-S", "ENTP-C", "ENTP-D",
        "ESTP-I", "ESTP-S", "ESTP-C", "ESTP-D",
        "INTP-I", "INTP-S", "INTP-C", "INTP-D",
        "ISTP-I", "ISTP-S", "ISTP-C", "ISTP-D",
        "ENTJ-I", "ENTJ-S", "ENTJ-C", "ENTJ-D",
        "ESTJ-I", "ESTJ-S", "ESTJ-C", "ESTJ-D",
        "INTJ-I", "INTJ-S", "INTJ-C", "INTJ-D",
        "ISTJ-I", "ISTJ-S", "ISTJ-C", "ISTJ-D"
    ]

    # Combine MBTI and DISC
    df["MBTI_DISC_COMBO"] = df["MBTI"].astype(str).str.strip() + "-" + df["DISC"].astype(str).str.strip()

    # Map ranking
    mbti_disc_rank_dict = {val: rank for rank, val in enumerate(mbti_disc_rank)}
    df["MBTI_DISC_RANK"] = df["MBTI_DISC_COMBO"].map(mbti_disc_rank_dict).fillna(len(mbti_disc_rank) + 1)

    # Understanding of self
    def classify_understanding(text):
        if isinstance(text, str):
            text_lower = text.lower()
            if text_lower.startswith("detailed"):
                return "Detailed"
            elif text_lower.startswith("moderate"):
                return "Moderate"
            elif text_lower.startswith("low effort"):
                return "Low Effort"
        return "Other"

    df["SELF_CLASS"] = df["UNDERSTANDING OF ONESELF"].apply(classify_understanding)

    df["CLARITY ABOUT CAREER"] = pd.Categorical(df["CLARITY ABOUT CAREER"], categories=career_order, ordered=True)
    df["OPTIMISM ABOUT SOCIETY"] = pd.Categorical(df["OPTIMISM ABOUT SOCIETY"], categories=optimism_order, ordered=True)
    df["SELF_CLASS"] = pd.Categorical(df["SELF_CLASS"], categories=self_understanding_order + ["Other"], ordered=True)

    # Match logic
    df["LOCATION_MATCH"] = df["LOCATION"].isin(user_locations) if user_locations else False

    def gender_priority(row):
        if any(val in [4, 5] for val in commitment_values) and len(user_gender) == 1:
            ug = user_gender[0]
            if ug == "M" and row["GENDER"] == "F":
                return 1
            elif ug == "F" and row["GENDER"] == "M":
                return 1
        return 0

    df["GENDER_PRIORITY"] = df.apply(gender_priority, axis=1)

    # Communication + Attachment score
    df["SOCIAL_ATTUNEMENT_SCORE"] = df["COMMUNICATION (1: INTROVERT)"] + df["ATTACHMENT (1: NOT ATTACHED)"]

    # Final sorting logic
    if any(val in [1, 2] for val in ldr_values):
        sort_cols = [
            "GENDER_PRIORITY",
            "LOCATION_MATCH",
            "SOCIAL_ATTUNEMENT_SCORE",
            "MBTI_DISC_RANK",
            "CLARITY ABOUT CAREER",
            "OPTIMISM ABOUT SOCIETY",
            "SELF_CLASS"
        ]
        sort_order = [False, False, False, True, True, True, True]
    else:
        sort_cols = [
            "GENDER_PRIORITY",
            "SOCIAL_ATTUNEMENT_SCORE",
            "MBTI_DISC_RANK",
            "CLARITY ABOUT CAREER",
            "OPTIMISM ABOUT SOCIETY",
            "SELF_CLASS"
        ]
        sort_order = [False, False, True, True, True, True]

    result_df = df.sort_values(by=sort_cols, ascending=sort_order)

    # Final cleanup
    result_df = result_df.drop(columns=[  # Remove unnecessary columns
        "LOCATION_MATCH", "SELF_CLASS", "GENDER_PRIORITY", "SOCIAL_ATTUNEMENT_SCORE",
        "MBTI_DISC_COMBO", "MBTI_DISC_RANK"
    ])

    # Return the cleaned-up results as a dictionary for use in Flask
    return result_df[["USER ID", "AGE", "GENDER", "LOCATION", "PERSONALITY", "LIKES AND DISLIKES"]].to_dict(orient="records")
