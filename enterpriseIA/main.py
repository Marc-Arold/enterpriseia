# main_controller.py
from app.gui.login_window import main
from databaseHandler import get_user_consent, get_user_by_id  
from app.modules.compliance_module import ComplianceModule      
from app.system import System
# In your main.py:
if __name__ == "__main__":
    main()
    # print(get_user_consent(21))
    # cp_module = ComplianceModule(90)
    # rights = cp_module.has_valid_consent(21)
    # print(rights)
    # user = get_user_by_id(21)
    # sys = System()
    # request = "hello"
    
    # reponses = sys.makeRequest(user, request)
    # print(reponses)

