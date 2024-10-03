from fastapi import HTTPException, Request, status, Response, BackgroundTasks, Depends
from service.userModule.userService import get_current_user_profile
from service.common.roleFinder import get_role_list
from request.userRequest import CreateEditorRequest, CreateAuthorRequest
from model.userModel import AuthorModel, EditorModel, UserModel, UserRoleModel
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


async def create_editor_or_author(request: Request,
                        createEditorOrAuthorReq: CreateEditorRequest,
                        db,  role: str, mode: str):
    try:
        current_user, user_email, exp = get_current_user_profile(request, db)
        user_role, creator_role_list = get_role_list(user_email, db)
        sadmin_role = 1453

        if sadmin_role not in creator_role_list:
            raise HTTPException(status_code=403, detail="User not authorized to make this change !") 
        
        # check is to-be editor is a user or nor
        toBeEditorOrAuthor = db.query(UserModel).filter(
                        UserModel.email == createEditorOrAuthorReq.user_email
                    ).filter(
                        UserModel.user_id == createEditorOrAuthorReq.user_id
                    ).first()
        if not toBeEditorOrAuthor:
            raise HTTPException(status_code=409, detail="User doesn't exist !")
        
        # check if assigned category list (id and name) are present in db
        if (createEditorOrAuthorReq.assigned_cat_id_list != "all" and createEditorOrAuthorReq.assigned_cat_name_list != "all"):
            check_if_cat_id_name_valid(createEditorOrAuthorReq.assigned_cat_id_list, createEditorOrAuthorReq.assigned_cat_name_list, db)
            assigned_cat_id_list = createEditorOrAuthorReq.assigned_cat_id_list
            assigned_cat_name_list = createEditorOrAuthorReq.assigned_cat_name_list 
        
        elif (createEditorOrAuthorReq.assigned_cat_id_list == "all" and createEditorOrAuthorReq.assigned_cat_name_list == "all"):
            all_cats = db.query(CategoryModel).all()
            assigned_cat_id_list = str([item.category_id for item in all_cats])
            assigned_cat_name_list = str([item.category_name for item in all_cats])
        else: 
            raise HTTPException(status_code=409, detail="Conflict in Category ID and Name !")
             

        if role == "editor":
            editor = db.query(EditorModel).filter(EditorModel.user_email == createEditorOrAuthorReq.user_email).first()
            
            # in create mode
            if mode == "create":
                if editor:
                    raise HTTPException(status_code=409, detail="User already registered as an Editor !")
                new_editor = EditorModel(
                    user_id=createEditorOrAuthorReq.user_id,
                    user_email=createEditorOrAuthorReq.user_email,
                    assigned_cat_id_list=assigned_cat_id_list,
                    assigned_cat_name_list=assigned_cat_name_list
                )
                db.add(new_editor)
                db.commit()
                db.refresh(new_editor)
            
            elif mode == "edit":
                if not editor:
                    raise HTTPException(status_code=409, detail="User isn't registered as an Editor !")
                editor.assigned_cat_id_list = assigned_cat_id_list
                editor.assigned_cat_name_list = assigned_cat_name_list
                db.commit()
                db.refresh(editor)
            else: 
                raise HTTPException(status_code=409, detail="Incorrect Mode !")

        if role == "author":
            author = db.query(AuthorModel).filter(AuthorModel.user_email == createEditorOrAuthorReq.user_email).first()
            
            if mode == "create":
                if author:
                    raise HTTPException(status_code=409, detail="User already registered as an Author !")
                new_author = AuthorModel(
                    user_id=createEditorOrAuthorReq.user_id,
                    user_email=createEditorOrAuthorReq.user_email,
                    assigned_cat_id_list=assigned_cat_id_list,
                    assigned_cat_name_list=assigned_cat_name_list
                )
                db.add(new_author)
                db.commit()
                db.refresh(new_author)
            
            elif mode == "edit":
                if not author: 
                    raise HTTPException(status_code=409, detail="User isn't registered as an Author !")
                author.assigned_cat_id_list = assigned_cat_id_list
                author.assigned_cat_name_list = assigned_cat_name_list
                db.commit()
                db.refresh(author)
            else: 
                raise HTTPException(status_code=409, detail="Incorrect Mode !")


        # now need to update user's role in user role table
        toBeEditorOrAuthor_role, toBeEditorOrAuthor_role_id_list = get_role_list(createEditorOrAuthorReq.user_email, db)
        if role == "editor":
            if mode == "create":
                editor_code = 1260
                if editor_code not in toBeEditorOrAuthor_role_id_list:
                    toBeEditorOrAuthor_role_id_list.append(editor_code)
                
                toBeEditorOrAuthor_role.role_code_list = str(toBeEditorOrAuthor_role_id_list)
                db.commit()
                db.refresh(toBeEditorOrAuthor_role)

        if role == "author":
            if mode == "create":
                author_code = 1203
                if author_code not in toBeEditorOrAuthor_role_id_list:
                    toBeEditorOrAuthor_role_id_list.append(author_code)
                
                toBeEditorOrAuthor_role.role_code_list = str(toBeEditorOrAuthor_role_id_list)
                db.commit()
                db.refresh(toBeEditorOrAuthor_role)
        
        return {"msg": f"{role} {mode}ed"}
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {e}"
            )