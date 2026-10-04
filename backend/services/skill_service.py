from backend.services.supabase_client import supabase

def get_skill(skill_name):
    response = (
        supabase
        .table("Skills")
        .select("*")
        .eq("skill_name", skill_name)
        .execute()
    )
    return response.data

def add_skill(skill_data):
    response = (
        supabase
        .table("Skills")
        .insert(skill_data)
        .execute()
    )
    return response.data