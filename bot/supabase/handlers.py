from supabase import Client

#cehck user already exists in database
def user_status(phone_number:str,db:Client):
    """Check user phone number already exists in database """
    result = db.table("botusers").select("*").eq("phoneNumber",phone_number).execute()
    if len(result.data) == 0:
        """when user not registerd. we have to create user record in the database"""
        record = db.table("botusers").insert({"phoneNumber":phone_number}).execute()
        if len(record.data) > 0 :
            return True
    elif(result.data[0]["isBanned"]==True):
        return False
    return True
    
#get all the configs if available
def get_configs(phone:str,db:Client):
    """get all the configs realted to a user number"""
    return db.table("botusers").select("config").eq("phoneNumber",phone).execute()    