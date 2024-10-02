from fastapi import HTTPException, Request, status, Response, BackgroundTasks, Depends
from service.userModule.userService import get_current_user_profile
from service.common.roleFinder import get_role_list
from request.userRequest import CreateEditorRequest, CreateAuthorRequest
from model.userModel import EditorModel, UserModel, UserRoleModel
from model.articleModel import CategoryModel
import ast

def check_if_cat_id_name_valid(cat_id_list, cat_name_list, db):
    cat_id_list = ast.literal_eval(cat_id_list)
    cat_name_list = ast.literal_eval(cat_name_list)
    if len(cat_id_list) != len(cat_name_list):
        raise HTTPException(status_code=406, detail="Category name and id list doesn't match !") 
    
    for i in range(len(cat_id_list)):
        category = db.query(CategoryModel).filter(
                        CategoryModel.category_id == cat_id_list[i]
                    ).filter(
                        CategoryModel.category_name == cat_name_list[i]
                    ).first()
        if not category:
            raise HTTPException(status_code=409, 
                                detail=f"Category id:{cat_id_list[i]} with name:{cat_name_list[i]} doesn't exist !")


async def create_editor(request: Request,
                        createEditorReq: CreateEditorRequest,
                        db):
    try:
        current_user, user_email, exp = get_current_user_profile(request, db)
        user_role, creator_role_list = get_role_list(user_email, db)
        sadmin_role = 1453
        if sadmin_role not in creator_role_list:
            raise HTTPException(status_code=403, detail="User not authorized to make this change !") 
        
        # check is to-be editor is a user or nor
        toBeEditor = db.query(UserModel).filter(
                        UserModel.email == createEditorReq.user_email
                    ).filter(
                        UserModel.user_id == createEditorReq.user_id
                    ).first()
        if not toBeEditor:
            raise HTTPException(status_code=409, detail="User doesn't exist !")
        
        # check if assigned category list (id and name) are present in db
        check_if_cat_id_name_valid(createEditorReq.assigned_cat_id_list, createEditorReq.assigned_cat_name_list, db)

        editor = db.query(EditorModel).filter(EditorModel.user_email == createEditorReq.user_email).first()
        if editor:
            raise HTTPException(status_code=409, detail="User already registered as an Editor !")
        new_editor = EditorModel(
            user_id=createEditorReq.user_id,
            user_email=createEditorReq.user_email,
            assigned_cat_id_list=createEditorReq.assigned_cat_id_list,
            assigned_cat_name_list=createEditorReq.assigned_cat_name_list
        )

        db.add(new_editor)
        db.commit()
        db.refresh(new_editor)

        # now need to update user's role in user role table
        toBeEditor_role, toBeEditor_role_id_list = get_role_list(createEditorReq.user_email, db)
        editor_code = 1260
        if editor_code not in toBeEditor_role_id_list:
            toBeEditor_role_id_list.append(editor_code)
        
        toBeEditor_role.role_code_list = str(toBeEditor_role_id_list)
        db.commit()
        db.refresh(toBeEditor_role)
        
        return {"msg": "new editor created"}
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {e}"
            )