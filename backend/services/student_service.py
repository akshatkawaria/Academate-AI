from backend.services.supabase_client import supabase

def get_student(student_id):
    response = (
        supabase
        .table("student_profiles")
        .select("*")
        .eq("id", student_id)
        .execute()
    )
    return response.data

def update_student(student_id, student_data):
    response = (
        supabase
        .table("student_profiles")
        .update(student_data)
        .eq("id", student_id)
        .execute()
    )
    return response.data