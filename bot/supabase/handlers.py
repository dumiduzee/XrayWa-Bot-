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


#Check user already have a config or not
def CheckUserHaveConfig(number:str,db:Client):
    """Arguemnt | Number
        Return type true or false
    """
    result = get_configs(phone=number,db=db)
    print(result)
    if result.data[0]["config"] == "" or result.data[0]["config"] ==  None:
        return False
    return True



#save config and config username/package into database 
def SaveConfig(config:str,username:str,number:str,package:str,db:Client)->bool:
    result = db.table("botusers").update({"config":config,"marzbanUsername":username,"configCount":1,"package":package}).eq("phoneNumber",number).execute()
    if len(result.data) == 0:
        return False
    return True


#get user's package
def getUserPackage(number:str,db:Client)->str:
    """Return users package type"""
    result = db.table("botusers").select("package").eq("phoneNumber",number).execute()
    if len(result.data) == 0:
        return False
    return result.data[0]