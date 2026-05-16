import pandas as pd

# ── Column labels ────────────────────────────────────────────────────────────
lb_student_id           = "student_id"
lb_age                  = "age"
lb_gender               = "gender"
lb_study_hours          = "study_hours_per_day"
lb_sleep_hours          = "sleep_hours"
lb_phone_usage          = "phone_usage_hours"
lb_social_media         = "social_media_hours"
lb_youtube              = "youtube_hours"
lb_gaming               = "gaming_hours"
lb_breaks               = "breaks_per_day"
lb_coffee               = "coffee_intake_mg"
lb_exercise             = "exercise_minutes"
lb_assignments          = "assignments_completed"
lb_attendance           = "attendance_percentage"
lb_stress               = "stress_level"
lb_focus                = "focus_score"
lb_final_grade          = "final_grade"
lb_productivity         = "productivity_score"

# ── Friendly names ────────────────────────────────────────────────────────────
alias = {
    lb_student_id:   "Student ID",
    lb_age:          "Age",
    lb_gender:       "Gender",
    lb_study_hours:  "Study Hours/Day",
    lb_sleep_hours:  "Sleep Hours",
    lb_phone_usage:  "Phone Usage (h)",
    lb_social_media: "Social Media (h)",
    lb_youtube:      "YouTube (h)",
    lb_gaming:       "Gaming (h)",
    lb_breaks:       "Breaks/Day",
    lb_coffee:       "Coffee (mg)",
    lb_exercise:     "Exercise (min)",
    lb_assignments:  "Assignments Done",
    lb_attendance:   "Attendance (%)",
    lb_stress:       "Stress Level",
    lb_focus:        "Focus Score",
    lb_final_grade:  "Final Grade",
    lb_productivity: "Productivity Score",
}

# ── Numeric columns for analysis ─────────────────────────────────────────────
numeric_cols = [
    lb_study_hours, lb_sleep_hours, lb_phone_usage, lb_social_media,
    lb_youtube, lb_gaming, lb_breaks, lb_coffee, lb_exercise,
    lb_assignments, lb_attendance, lb_stress, lb_focus,
    lb_final_grade, lb_productivity
]

# ── Distraction vs Productivity groupings ────────────────────────────────────
distraction_cols  = [lb_phone_usage, lb_social_media, lb_youtube, lb_gaming]
productivity_cols = [lb_study_hours, lb_sleep_hours, lb_exercise,
                     lb_assignments, lb_attendance, lb_focus, lb_productivity]


def read_csv_file(file_path: str) -> pd.DataFrame:
    """Read the student CSV; tries comma then semicolon separator."""
    for sep in (",", ";"):
        try:
            df = pd.read_csv(file_path, sep=sep)
            if df.shape[1] > 1:
                return df
        except Exception as e:
            print(f"[read_csv_file] sep='{sep}' failed: {e}")
    print(f"[read_csv_file] Could not read: {file_path}")
    return pd.DataFrame()