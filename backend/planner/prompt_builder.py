"""
Prompt Builder — Builds the AI enhancement prompt.
RESPONSIBILITY: Communicates the pre-built schedule to the LLM for personalization only.
"""
import json


def build_enhancement_prompt(user_data: dict, analysis: dict, schedule: list, date: str) -> str:
    """
    Builds a highly specific prompt that asks the LLM to ENHANCE the pre-built schedule,
    not to generate one from scratch.
    """
    schedule_json = json.dumps(schedule, indent=2)

    prompt = f"""You are AcadMate's AI Study Mentor.

A student's personalized daily schedule has already been calculated by our intelligent planning system.
Your sole task is to ENHANCE this schedule with better language, personalized advice, and mentor-level reasoning.

=== STUDENT PROFILE ===
Name/Goal: {user_data.get('motivation_goal', 'Do well in academics and career')}
Semester: {user_data.get('semester', 'Current')}
Placement Goal: {user_data.get('placement_goal', 'Not specified')}
Weak Subjects: {', '.join(user_data.get('weak_subjects', [])) or 'None identified'}
Biggest Distraction: {user_data.get('biggest_distraction', 'Social media')}
Stress Level: {user_data.get('stress_level', 'medium')}
Burnout Level: {user_data.get('burnout_level', 'low')}
Consistency: {user_data.get('consistency_level', 'medium')}
Procrastination Level: {user_data.get('procrastination_level', 'medium')}
Confidence: {user_data.get('confidence_level', 'medium')}

=== PLANNING ANALYSIS ===
Academic Focus: {analysis['academic_weight']}%
Placement Focus: {analysis['placement_weight']}%
Planning Reason: {analysis['reason']}

=== PRE-CALCULATED SCHEDULE FOR {date} ===
{schedule_json}

=== YOUR INSTRUCTIONS ===
1. Return the schedule EXACTLY as given (same start_time, end_time, task_type, priority).
2. ENHANCE each task_name to be more specific, actionable, and motivating.
3. REWRITE each reason to sound like a real mentor speaking directly to this student.
4. Add 3-5 highly personalized productivity_advice items based on their distractions, stress, and burnout.
5. Write a compelling plan_summary.reason that explains this specific student's strategy.

=== CRITICAL RULES ===
- Return ONLY valid JSON. No markdown. No code blocks. No comments inside JSON.
- Do not change start_time, end_time, task_type, or priority values.
- The academic_focus and placement_focus values must stay exactly: {analysis['academic_weight']} and {analysis['placement_weight']}.

=== REQUIRED JSON STRUCTURE ===
{{
  "plan_summary": {{
    "academic_focus": {analysis['academic_weight']},
    "placement_focus": {analysis['placement_weight']},
    "reason": "Write a specific, mentor-like explanation here."
  }},
  "schedule": [
    {{
      "start_time": "09:00 AM",
      "end_time": "10:00 AM",
      "task_name": "Enhanced task name here",
      "task_type": "academic",
      "priority": "high",
      "reason": "Mentor-level personal reason here."
    }}
  ],
  "productivity_advice": [
    "Highly specific advice 1",
    "Highly specific advice 2",
    "Highly specific advice 3"
  ]
}}"""
    return prompt
