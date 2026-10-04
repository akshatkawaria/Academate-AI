from backend.services.supabase_client import supabase

def get_resources(skill_name):
    response = (
        supabase
        .table("skill_resources")
        .select("*")
        .eq("skill_name", skill_name)
        .execute()
    )
    return response.data

def add_resources(resources_data):
    response = (
        supabase
        .table("skill_resources")
        .insert(resources_data)
        .execute()
    )
    return response.data